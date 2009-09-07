NULL =

EXTRA_DIST = \
	fakegen.py \
	gedithelpers.py \
	__init__.py \
	testrunner.py \
	$(NULL)

gen_gedit = (cd $(top_srcdir) \
	&& rm -f gedit/*.py gedit/*.pyc \
	&& $(PYTHON) utils/gen-gedit.py)

all:
	$(gen_gedit)
