# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)
AC_INIT(gedit-developer-plugins, 0.1, sinzui.is@verizon.net)
AM_INIT_AUTOMAKE

AM_MAINTAINER_MODE

# Checks for programs.
AM_PATH_PYTHON

# Checks for libraries.
PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AC_CONFIG_FILES([
  Makefile
  testing/Makefile
  plugins/Makefile
  plugins/gdp/Makefile
])
AC_OUTPUT
