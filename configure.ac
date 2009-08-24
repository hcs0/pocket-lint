# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)

m4_define(gdp_major_version,  2)
m4_define(gdp_minor_version, 20)
m4_define(gdp_micro_version,  0)
m4_define(gdp_version, gdp_major_version.gdp_minor_version.gdp_micro_version)

AC_INIT(gedit-developer-plugins, gdp_version, sinzui.is@verizon.net)
AM_INIT_AUTOMAKE([1.8 -Wno-portability])

AM_MAINTAINER_MODE

# Command line options.
AC_ARG_WITH([home],
    AS_HELP_STRING([--without-home],
        [Do not install the plugins in $HOME/.gnome2/gedit]),
    ,
    [with_home=yes]
)

# Checks for programs.
AM_PATH_PYTHON

# Checks for libraries.
# We should check for Gedit, but the package pkg-config data is
# not always available. gtksourceview is a good indicator of the
# Gedit version.
PKG_CHECK_MODULES(GEDIT, [
    pygtk-2.0 >= 0.18
    gtksourceview-2.0 >= 2.0.0
])

# i18n configuration.
GETTEXT_PACKAGE=gedit-developer-plugins
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.40.0])

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# Set the location to install the plugins. The personal location (.gnome2)
# is different form public locations.
AC_DEFUN([GEDIT_PLUGIN], [
    if test $with_home = 'yes'; then
        gedit_plugin_dir=`echo "${HOME}/.gnome2/gedit/plugins"`
    else
        gedit_plugin_dir='$(libdir)/gedit-2/plugins'
    fi
    AC_SUBST(GEDIT_PLUGIN_DIR, [$gedit_plugin_dir])
])
GEDIT_PLUGIN

# The location of Gedit's personal external tools.
AC_DEFUN([GEDIT_TOOLS], [
    gedit_tools_dir=`echo "${HOME}/.gnome2/gedit/tools"`
    AC_SUBST(GEDIT_TOOLS_DIR, [$gedit_tools_dir])
])
GEDIT_TOOLS

# The location of Gedit's personal snippets.
AC_DEFUN([GEDIT_SNIPPETS], [
    gedit_snippets_dir=`echo "${HOME}/.gnome2/gedit/snippets"`
    AC_SUBST(GEDIT_SNIPPETS_DIR, [$gedit_snippets_dir])
])
GEDIT_SNIPPETS

# The location of GTKSourceViews lang files.
AC_DEFUN([GTKSOURCEVIEW_LANGS], [
    gtksourceview_langs_dir=`echo "${HOME}/.local/share/gtksourceview-2.0/language-specs"`
    AC_SUBST(GTKSOURCEVIEW_LANGS_DIR, [$gtksourceview_langs_dir])
])
GTKSOURCEVIEW_LANGS

# Automake files to create
AC_CONFIG_FILES([
    Makefile
    testing/Makefile
    plugins/Makefile
    plugins/gdp/Makefile
    po/Makefile.in
    tools/Makefile
    snippets/Makefile
    language-specs/Makefile
])
AC_OUTPUT

echo "

Configuration:
    prefix: ${prefix}
    gedit plugin dir: $GEDIT_PLUGIN_DIR
    gedit tools dir: $GEDIT_TOOLS_DIR
    gedit snippets dir: $GEDIT_SNIPPETS_DIR
    GTKSourceView langs dir: $GTKSOURCEVIEW_LANGS_DIR
"
