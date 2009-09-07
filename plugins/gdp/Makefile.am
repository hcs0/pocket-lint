plugindir = $(GEDIT_PLUGIN_DIR)/gdp

plugin_PYTHON = \
	__init__.py \
	bzr.py \
	find.py \
	format.py \
	formatcheck.py \
	formatdoctest.py \
	syntaxcompleter.py

uidir = $(plugindir)
ui_DATA = \
	find.ui \
	format.ui

EXTRA_DIST = $(ui_DATA)

dist-hook:
	mkdir $(distdir)/tests
	cp -p $(srcdir)/tests/* $(distdir)/tests
	rm -f $(distdir)/tests/*.pyc
	mkdir $(distdir)/data
	cp -p $(srcdir)/data/* $(distdir)/data

CLEANFILES = *.bak *.pyc *.pyo
DISTCLEANFILES = *.bak *.pyc *.pyo

