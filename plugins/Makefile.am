DIST_DIRS = gdp
SUBDIRS = gdp

plugindir = $(libdir)/gedit-2/plugins

plugin_PYTHON = \
	syntaxcompleterplugin.py

plugin_in_files = syntaxcompleter.gedit-plugin.desktop.in
%.gedit-plugin: %.gedit-plugin.desktop.in $(INTLTOOL_MERGE) $(wildcard $(top_srcdir)/po/*po) ; $(INTLTOOL_MERGE) $(top_srcdir)/po $< $@ -d -u -c $(top_builddir)/po/.intltool-merge-cache

plugin_DATA = $(plugin_in_files:.gedit-plugin.desktop.in=.gedit-plugin)

EXTRA_DIST = $(plugin_in_files)

CLEANFILES = *.bak *.pyc $(plugin_DATA)
DISTCLEANFILES = *.bak *.pyc $(plugin_DATA)
