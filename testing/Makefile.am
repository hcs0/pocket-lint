NULL =

EXTRA_DIST = \
	fakegen.py \
	gedithelpers.py \
	__init__.py \
	testrunner.py \
	$(NULL)

dist-hook:
	mkdir $(distdir)/tests
	cp -p $(srcdir)/tests/* $(distdir)/tests
	rm -f $(distdir)/tests/*.pyc
	mkdir $(distdir)/codegen
	cp -p $(srcdir)/codegen/* $(distdir)/codegen
	rm -f $(distdir)/codegen/*.pyc
