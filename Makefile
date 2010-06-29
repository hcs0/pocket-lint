PYTHON = python

build:
	$(PYTHON) setup.py build

check: build
	$(PYTHON) test.py -v

dist: build
	$(PYTHON) setup.py sdist --manifest-only

clean:
	$(PYTHON) setup.py clean

distclean: clean
	rm -r dist/ MANIFEST

.PHONY: build check clean dist
