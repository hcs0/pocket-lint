SUBDIRS = gdp

NULL =

plugindir = $(GEDIT_PLUGIN_DIR)

plugin_PYTHON = \
	gdpbzr.py \
	gdpfind.py \
	gdpformat.py \
	gdpsyntaxcompleter.py \
	$(NULL)

plugin_in_files = \
	gdpbzr.gedit-plugin.desktop.in \
	gdpfind.gedit-plugin.desktop.in \
	gdpformat.gedit-plugin.desktop.in \
	gdpsyntaxcompleter.gedit-plugin.desktop.in \
	$(NULL)

%.gedit-plugin: %.gedit-plugin.desktop.in \
	$(INTLTOOL_MERGE) $(wildcard $(top_srcdir)/po/*po); \
	$(INTLTOOL_MERGE) $(top_srcdir)/po $< \
	$@ -d -u -c $(top_builddir)/po/.intltool-merge-cache

plugin_DATA = $(plugin_in_files:.gedit-plugin.desktop.in=.gedit-plugin)

EXTRA_DIST = $(plugin_in_files)

dist-hook:
	mkdir $(distdir)/tests
	cp -p $(srcdir)/tests/* $(distdir)/tests
	rm -f $(distdir)/tests/*.pyc

CLEANFILES = *.bak *.pyc *.pyo $(plugin_DATA)
DISTCLEANFILES = *.bak *.pyc *.pyo $(plugin_DATA)
