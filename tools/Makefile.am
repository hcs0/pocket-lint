NULL =

toolsdir = $(GEDIT_TOOLS_DIR)

tools_DATA = \
	2-make \
	3-lint \
	3-make-lint \
	4-shift-test \
	4-test \
	5-bzr-diff \
	5-bzr-diff-ancestor \
	build \
	bzr-annotate \
	bzr-commit \
	bzr-diff-ancestor \
	bzr-diff-branch \
	bzr-diff-file \
	bzr-open-changed-files \
	bzr-status \
	encode \
	find.py \
	find-in-files \
	formatdoctest.py \
	format-doctest \
	remove-trailing-spaces \
	selectioncommands.py \
	task-selection.glade \
	$(NULL)

install-data-hook:
	chmod +x $(toolsdir)/*
	chmod -x $(toolsdir)/*.glade
