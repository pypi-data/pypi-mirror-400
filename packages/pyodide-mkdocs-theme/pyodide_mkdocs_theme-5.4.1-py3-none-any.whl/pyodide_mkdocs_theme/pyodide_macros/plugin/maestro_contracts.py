"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""
# pylint: disable=multiple-statements



import json
import os
from pathlib import Path
import platform
import re
from textwrap import dedent
from typing import ClassVar, Dict, Iterable, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

from mkdocs.config.defaults import MkDocsConfig


from ...__version__ import __version__
from ..exceptions import PmtMacrosContractError
from ..pyodide_logger import logger
from ..tools_and_constants import GITLAB_UNIQUE_DOMAIN_NAME_SETTING, HashPathMode, MultiProjectFeedbackLevel, MyEnum
from .config import PLUGIN_CONFIG_SRC, GIT_LAB_PAGES
from .maestro_base import BaseMaestro





@dataclass
class Props:

    id: str         = PLUGIN_CONFIG_SRC.get_plugin_path('project.id')
    feedback: str   = PLUGIN_CONFIG_SRC.get_plugin_path('project.id_feedback')
    hash_mode: str  = PLUGIN_CONFIG_SRC.get_plugin_path('build.ides_id_hash_mode')
    dis_ls: str     = PLUGIN_CONFIG_SRC.get_plugin_path('project.disambiguate_local_storage')



class MaestroContractsMultiProjects(BaseMaestro):
    """
    Handle all the logistic related to build.ides_id_hash_mode and project.id.
    """

    _pid_to_names: Dict[str,Set[str]]
    """ Relations project.id -> Set[site_name] """

    _name_to_pids: Dict[str,Set[str]]
    """ Relations site_name -> Set[project.id] """

    _projects_tracker_path: Optional[Path] = None
    """ File location """


    def _build_multi_projects_message(self):
        """
        ALWAYS show these informations, whatever the config is. This will ease helping users,
        making sure some critical informations are always available.
        """
        self.get_projects_json_path()
        self.acquire_projects_json()

        msg = dedent(f"""
            ##############################################################
            ##   MAKE SURE THE `{ Props.id }` IS UNIQUE    ##
            ##  ACROSS ALL PMT PROJECTS HOSTED ON THE SAME DOMAIN NAME  ##
            ##############################################################

            This applies to:
                - Different projects hosted in the same GitLab/GitHub group.
                - Different projects hosted on the same account that are not using "unique
                  domain names" when building the pages/website.
            """)

        _is     = ' is:'
        align_L = 2 + len(_is) + max(map(len, (Props.hash_mode, Props.id, Props.dis_ls)))
        align_R = 10
        msg    += dedent(f"""\

            { Props.hash_mode    +_is :<{align_L}} {self.ides_id_hash_mode!r:>{align_R}}
            { Props.id +_is :<{align_L}} {self.project_id!r:>{align_R}}
            { Props.dis_ls      +_is :<{align_L}} {str(self.project_disambiguate_local_storage):>{align_R}}

            site_name is: { self._conf.site_name }
            """)

        if self._projects_tracker_path:
            msg += dedent(f"""
            File storing the relations project.id <-> site_name:
                { self._projects_tracker_path }
            """)

        return msg


    def get_projects_json_path(self):
        """ Build the path to the target file, depending on the OS used. """
        os_name = platform.system()

        if os_name=='Windows':
            p = Path(os.environ['APPDATA'])
        elif  os_name=='Linux':
            p = Path(os.environ['HOME']) / '.local' / 'share'
        elif  os_name=='Darwin':
            p = Path(os.environ['HOME'])  / "Library" / "Application Support"
        else:
            prop = PLUGIN_CONFIG_SRC.get_plugin_path('project.id')
            logger.info(
                f"Couldn't identify the OS: no consistency check on the `{ prop }` values.")
            return

        self._projects_tracker_path = p / 'Pyodide-MkDocs-Theme' / "project_ids_data.json"


    def acquire_projects_json(self):
        """ Extract the content of the local file, or set a default value. """
        self._pid_to_names = defaultdict(set)
        self._name_to_pids = defaultdict(set)
        if self._projects_tracker_path and self._projects_tracker_path.is_file():
            code = self._projects_tracker_path.read_text(encoding='utf-8')
            for pid,name in json.loads(code):
                self._pid_to_names[pid].add(name)
                self._name_to_pids[name].add(pid)


    def update_and_dump_projects_json(self):
        """ Dump the current _projects_json to the disk. """
        if self._projects_tracker_path and self.project_id is not None:
            self._pid_to_names[self.project_id].add(self._conf.site_name)
            code = self._projects_to_json_arr_as_str()
            self._projects_tracker_path.parent.mkdir(parents=True, exist_ok=True)
            self._projects_tracker_path.write_text(code, encoding='utf-8')


    def _projects_to_json_arr_as_str(self):
        as_arr = sorted( [pid,name] for pid,names in self._pid_to_names.items() for name in names )
        code   = json.dumps(as_arr, indent=2)
        return code


    def _check_multi_projects_configuration(self):
        site_name = self._conf.site_name
        pid       = self.project_id

        if pid == 'null':
            raise PmtMacrosContractError(
                f"The config option { Props.id } cannot be set to `'null'` as a string. "
                "Use either `null` or another string."
            )

        if 'site_name' not in self._conf or not self._conf.site_name:
            raise PmtMacrosContractError(
                f"mkdocs.yml:site_name must be configured, and must be a non empty string."
            )

        msg    = ""
        no_def = pid is None
        exists = pid in self._pid_to_names
        others = self._pid_to_names[pid] - {site_name}
        pids   = self._name_to_pids[site_name] - {pid}

        if MultiProjectFeedbackLevel.is_silent(self):
            logger.info(f"{ Props.feedback } is set to { MultiProjectFeedbackLevel.silent }")
            if not exists:
                self.update_and_dump_projects_json()
            return

        if no_def or others or pids:
            def format_list(data):
                return ''.join(map('\n    - {}'.format, sorted(data) or ["(None)"]))

            msg = ["Configuration troubles:"]

            if no_def:
                msg.append(f"`{ Props.id }` is not configured for the current project.")
            if others:
                msg.append(
                    f"\nThis `{ Props.id }` value is already used with the following projects site_names:"
                    + format_list(others)
                )
            if pids:
                msg.append(
                    f"\nThe current project is already referenced using these project ids:"
                    + format_list(map(repr,pids))
                )

            msg.append(dedent(f"""\

            ----------------------------------------------

            See the documentation (french) for information about how to handle this:

                { GIT_LAB_PAGES }custom/local-storage/#local-storage-tl-dr


            The most generic approaches are:

            1. For a new project:
                - Set { Props.hash_mode } to { HashPathMode.relative }.
                - Set a unique identifier (string) for { Props.id }.

            2. For an existing project, if the codes saved in the localStorage of your users can be dropped
               (ex: beginning of the school period), just apply the logic of the previous point.

            3. For an existing project where the data in the localStorage must be kept:
                - Set a unique identifier (string) for { Props.id }.
                - Set { Props.dis_ls } to `false`.
                - Be ready to handle ids collisions case by case, if some are found.
                  This is more probable to happen if { Props.hash_mode } is set to `{ HashPathMode.relative }`.
                  See the documentation for more information:
                  { GIT_LAB_PAGES }custom/local-storage/#local-storage-vs-theme

            4. If you like living a "dangerous life", you can bypass the current logic by setting
            { Props.feedback } to `{ MultiProjectFeedbackLevel.silent }`. Note that doing so, there are no
            guarantees on the behavior of the theme, considering the consistency of the entries stored
            in the localStorage.

            """))

        if not msg:
            self.update_and_dump_projects_json()
            logger.debug(
                f"\n{ self._projects_tracker_path } content is:\n{ self._projects_to_json_arr_as_str() }"
            )

        if msg and not MultiProjectFeedbackLevel.is_silent(self):
            msg = '\n'.join(msg).strip()
            if MultiProjectFeedbackLevel.is_error(self):
                raise PmtMacrosContractError(msg)
            else:
                method = MultiProjectFeedbackLevel.get_logger_method(self)
                getattr(logger, method)(msg)














class MaestroContracts(MaestroContractsMultiProjects):
    """
    Mixin enforcing various contracts on PMT usage within mkdocs.
    """

    __mkdocs_checked = False
    """ Flag to check the mkdocs.yml config once only """


    # Override
    def on_config(self, config:MkDocsConfig):

        logger.info(f"Building with PMT v{ self.version }")

        logger.info("Validate PMT contracts.")

        multi_projects_msg = self._build_multi_projects_message()
        logger.info(
            "\n----------------------------------------------\n"
           f"{ multi_projects_msg }"
            "\n----------------------------------------------\n"
        )

        if not self.__mkdocs_checked:
            logger.debug("Check multi-projects configuration.")
            self._check_multi_projects_configuration()

            logger.debug("Check Mkdocs-Material's plugins registration in mkdocs.yml.")
            self._check_material_prefixes_plugins_config_once(config)

            logger.debug("Check usage of the old PMT hooks html files.")
            self._check_pmt_hooks_files_usage(config)

            logger.debug("Check the plugin config of the original MacrosPlugin class didn't change.")
            PLUGIN_CONFIG_SRC.validate_macros_plugin_config_once(self)

            self.__mkdocs_checked = True # pylint: disable=attribute-defined-outside-init

        logger.debug("Markdown and python paths names validation.")
        self._check_docs_paths_validity()

        logger.debug("Handle PMT plugin's deprecated configuration options.")
        PLUGIN_CONFIG_SRC.handle_deprecated_options_and_conversions(self)

        logger.debug("Contracts verifications OK.")
        super().on_config(config)


    def _check_docs_paths_validity(self) -> None :
        """
        Travel through all paths in the docs_dir and raises an PmtMacrosContractError
        if  "special characters" are found in directory, py, or md file names (accepted
        characters are: r'[\\w.-]+' ).

        NOTE: Why done here and not in `on_files`?
                => because on_files is subject to files exclusions, and most python files SHOULD
                have been excluded from the build. So `on_files` could make more sense considering
                the kind of task, but is not technically appropriate/relevant...
        """
        if self.skip_py_md_paths_names_validation:
            logger.warning("The build.skip_py_md_paths_names_validation option is activated.")
            return

        invalid_chars = re.compile(r'[^A-Za-z0-9_.-]+')
        wrongs = defaultdict(list)

        # Validation is done on the individual/current segments of the paths, so that an invalid
        # directory name is not affecting the validation of its children:
        for path,dirs,files in os.walk(self.docs_dir):

            files_to_check = [ file for file in files if re.search(r'\.(py|md)$', file)]

            for segment in dirs + files_to_check:
                invalids = frozenset(invalid_chars.findall(segment))
                if invalids:
                    wrongs[invalids].append( os.path.join(path,segment) )

        if wrongs:
            msg = ''.join(
                f"\nInvalid characters {repr(''.join(sorted(invalids)))} found in these filepaths:"
                + "".join(f"\n\t{ path }" for path in sorted(lst))
                for invalids,lst in wrongs.items()
            )
            raise PmtMacrosContractError(
                f"{ msg }\nPython and markdown files, and their parent directories' names "
                'should only contain alphanumerical characters (no accents or special chars), '
                "dots, underscores, and/or hyphens."
            )



    def _check_pmt_hooks_files_usage(self, config:MkDocsConfig):
        """
        From 3.2.0, hooks files defined in the custom_dir are still working, but should be
        replaced using the extension of `main.html` of the theme (making things easier).
        """
        custom_dir_name = getattr(config.theme, 'custom_dir', None)
        if not custom_dir_name:
            return

        cwd = Path.cwd()
        hooks: Path = cwd / custom_dir_name / 'hooks'
        if hooks.is_dir():
            files = ''.join( f"\n    { file.relative_to(cwd) }" for file in hooks.iterdir() )
            logger.warning(
                "Some PMT html hook files are present in Your custom_dir. From PMT 3.2.0, the "
                'extension of `main.html` (extending `"base_pmt.html"`) should be preferred.\n'
                'Please see this page of the documentation for more information: '
                f'{ GIT_LAB_PAGES }custom/custom_dir/\nRelated files:{ files }'
            )




    def _check_material_prefixes_plugins_config_once(self, config:MkDocsConfig):
        """
        Following 2.2.0 breaking change: material plugins' do not _need_ to be prefixed
        anymore, but the json schema validation expects non prefixed plugin names, so:

            if config.theme.name is material:
                error + how to fix it (mismatched config)
            if "material/plugin":
                error + how to fix it (pmt/...)
            if config.theme.name is something else (theme extension):
                if not "pmt/plugin":  error + how to fix it (pmt/...)


        HOW TO SPOT VALUES:
            Access plugins (dict):  `config.plugins`

            The theme prefix IS ALWAYS THERE in the config:
                * `{theme.name}/search`  <-  `mkdocs.yml:plugins: - search`
                * `{some}/search`        <-  `mkdocs.yml:plugins: - {some}/search`
        """
        errors       = []
        material     = 'material'
        pmt          = 'pyodide-mkdocs-theme'
        theme        = config.theme.name
        is_extension = theme and theme not in (material, pmt, None)
        registered   = RegisteredPlugin.convert(config.plugins)


        if not theme or theme==material:
            errors.append(
                f"The { pmt }'s plugin is registered, so `theme.name` should be set "
                f"to `{ pmt }` instead of `{ theme }`."
            )

        features = config.theme.get('features', ())
        if 'navigation.instant' in features:
            errors.append(
                "Remove `navigation.instant` from `mkdocs.yml:theme.features`. "
                "It is not compatible with the pyodide-mkdocs-theme."
            )

        for plug in registered:
            if plug.prefix != theme:
                errors.append(
                    f"The `{ plug.qualname }` plugin should be registered " + (
                        f"with `pyodide-mkdocs-theme/{ plug.name }`."
                            if is_extension else
                        f"using `{ plug.name }` only{ ' (PMT >= 2.2.0)' * (theme==pmt) }."
                    )
                )

        if errors:
            str_errors = ''.join(map( '\n  {}'.format, errors ))
            raise PmtMacrosContractError(
                f"Invalid theme or material's plugins configuration(s):{ str_errors }"
            )














@dataclass
class RegisteredPlugin:
    """
    Represents an mkdocs plugin name, with information about how it's built.
    """

    qualname: str
    """ Fully qualified name: 'pyodide-mkdocs-theme/search' """

    name: str
    """ Plugin's name: 'search' """

    prefix: Optional[str]
    """ Plugin's prefix: 'pyodide-mkdocs-theme' or None """



    MATERIAL_PLUGINS: ClassVar[Set[str]] = set('''
        blog group info offline privacy search social tags
    '''.split())
    """
    All existing mkdocs-material plugins.
    See: https://github.com/squidfunk/mkdocs-material/tree/master/src/plugins
    """


    @classmethod
    def convert(cls, plugins:Iterable[str]) -> List['RegisteredPlugin'] :
        pattern = re.compile(
            f"(?:(?P<prefix>\\w*)/)?(?P<name>{ '|'.join(cls.MATERIAL_PLUGINS) })"
        )
        registered = [
            RegisteredPlugin(m[0], m['name'], m['prefix'])
                for m in map(pattern.fullmatch, plugins)
                if m
        ]
        return registered
