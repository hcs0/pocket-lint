NULL =

plugindir = $(GEDIT_PLUGIN_DIR)

plugin_PYTHON = \
	pep8.py \
	$(NULL)

pluginpyflakesdir = $(GEDIT_PLUGIN_DIR)/pyflakes

pluginpyflakes_PYTHON = \
	pyflakes/__init__.py \
	pyflakes/checker.py \
	pyflakes/messages.py \
	$(NULL)

CLEANFILES = *.bak *.pyc *.pyo $(plugin_DATA)
DISTCLEANFILES = *.bak *.pyc *.pyo $(plugin_DATA)
