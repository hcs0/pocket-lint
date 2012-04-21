from pocketlint.formatcheck import ReStructuredTextChecker
from pocketlint.tests import CheckerTestCase

#
# This is a valid rst content.
# This comment is here so that the content starts at line 11
# and make it easier to identify errors in tests.
# Just add 10 to the reported line number.
#
valid_rst_content = '''\
=============
First section
=============

Text *for* first **section**.


--------------
Second section
--------------


Third section
^^^^^^^^^^^^^

Paragrhap for
third section `with link<http://my.home>`_.

::

  Literal block1.

  Literal block paragraph.


| Line blocks are useful for addresses,
| verse, and adornment-free lists.


Another Section
---------------

>>> print "This is a doctest block."
... with a line continuation
This is a doctest block.

A grid table.

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
| body row 3 | Cells may  | - Cells   |
+------------+ span rows. | - contain |
| body row 4 |            | - blocks. |
+------------+------------+-----------+

A simple table.

Simple table:

=====  =====  ======
   Inputs     Output
------------  ------
  A      B    A or B
=====  =====  ======
False  False  False
True   False  True
False  True   True
True   True   True
=====  =====  ======

A transition marker is a horizontal line
of 4 or more repeated punctuation
characters.

------------

A transition should not begin or end a
section or document, nor should two
transitions be immediately adjacent.

Footnote references, like [5]_.
Note that footnotes may get
rearranged, e.g., to the bottom of
the "page".

.. [5] A numerical footnote. Note
   there's no colon after the ``]``.

External hyperlinks, like Python_.
.. _Python: http://www.python.org/

For instance:

.. image:: images/ball1.gif

The |biohazard| symbol must be used on containers used to dispose of
medical waste.

.. |biohazard| image:: biohazard.png

.. This text will not be shown
   (but, for instance, in HTML might be
   rendered as an HTML comment)
'''


class TestReStructuredTextChecker(CheckerTestCase):
    """Verify reStructuredTextChecker checking."""

    def test_empty_file(self):
        self.reporter.call_count = 0
        content = ('')
        checker = ReStructuredTextChecker('bogus', content, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)
        self.assertEqual(0, self.reporter.call_count)

    def test_valid_content(self):
        self.reporter.call_count = 0
        checker = ReStructuredTextChecker(
            'bogus', valid_rst_content, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)
        self.assertEqual(0, self.reporter.call_count)

    def test_no_empty_last_line(self):
        self.reporter.call_count = 0
        content = (
            'Some first line\n'
            'the second and last line witout newline'
            )
        checker = ReStructuredTextChecker('bogus', content, self.reporter)
        checker.check_empty_last_line()
        expected = [(
            2, 'File does not ends with an empty line.')]
        self.assertEqual(expected, self.reporter.messages)
        self.assertEqual(1, self.reporter.call_count)

    def test_multiple_empty_last_lines(self):
        self.reporter.call_count = 0
        content = (
            'Some first line\n'
            'the second and last\n'
            '\n'
            )
        checker = ReStructuredTextChecker('bogus', content, self.reporter)
        checker.check_empty_last_line()
        expected = [(
            3, 'File does not ends with an empty line.')]
        self.assertEqual(expected, self.reporter.messages)
        self.assertEqual(1, self.reporter.call_count)

    def test_multiple_empty_last_lines(self):
        self.reporter.call_count = 0
        content = (
            'Some first line\n'
            'the second and last\n'
            '\n'
            )
        checker = ReStructuredTextChecker('bogus', content, self.reporter)
        checker.check_empty_last_line()
        expected = [(
            3, 'File does not ends with an empty line.')]
        self.assertEqual(expected, self.reporter.messages)
        self.assertEqual(1, self.reporter.call_count)