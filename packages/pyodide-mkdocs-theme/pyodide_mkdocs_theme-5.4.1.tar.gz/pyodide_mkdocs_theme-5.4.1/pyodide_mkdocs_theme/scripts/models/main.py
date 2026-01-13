from pyodide_mkdocs_theme.pyodide_macros import PyodideMacrosPlugin


def define_env(env:PyodideMacrosPlugin):
    """ Define your personal macros here. """

    @env.macro
    def my_macro(*a, **kw):
        """
        Can be used in md files with {{ my_macro(42, msg='this or that') }}.
        A macro must return markdown code (or directly html content).
        """
        return '...'


    @env.macro
    def my_macro_with_auto_indent(*a, **kw):
        """
        If the macro is registered in pyodide_macros.build.macros_with_indents, it has to call
        `env.indent_macro(md_content)` so that PMT can automatically adapt the indentation of
        the content for you.
        Not calling this method will cause an error at build time.
        """
        md_content = '...'
        output = env.indent_macro(md_content)
        return output
