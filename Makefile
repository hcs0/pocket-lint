PYTHON = python

build:
	$(PYTHON) setup.py build

check: build
	$(PYTHON) test.py -v

manifest:
	$(PYTHON) setup.py sdist --manifest-only

dist: build
	$(PYTHON) setup.py sdist

clean:
	$(PYTHON) setup.py clean
	rm -r build/

distclean: clean
	rm -r dist/ MANIFEST

.PHONY: build check clean dist
