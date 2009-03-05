"""Find in files and replace strings in many files."""


__metaclass__ = type


from exceptions import IOError
from optparse import OptionParser
import os
import re
import sys


class FileMatch:
    """A file that contains lines that match a text pattern."""

    def __init__(self, file_path, lines):
        """Initialise the FileMatch.

        :param file_path: The path to the file.
        :param lines: a list of `LineMatch` objects.
        """
        self.file_path = file_path
        self.lines = lines


class LineMatch:
    """A line in a file that match a text pattern."""

    def __init__(self, lineno, text):
        """Initialise the LineMatch.

        :param lineno: The line number in the file where the text matches.
        :param text: The text of line that contains the match.
        """
        self.lineno = lineno
        self.text = text


class MatchesGenerator:
    """Search files below a directory for matching text."""

    def __init__(self, root_dir):
        """Create a MatchesGenerator for the directory.

        :param root_dir: The path to the directory to be searched.
        :raise IOError: if the root_dir is not a valid directory.
        """
        if not os.path.isdir(root_dir):
            raise IOError('Non-existent directory: %s' % root_dir)
        self.root_dir = root_dir

    def find(self, file_pattern, match_pattern,
             is_re=True, match_case=True, substitution=None):
        """Iterate a summary of matching lines in a file."""
        if not is_re:
            match_pattern = re.escape(match_pattern)
        flags = re.IGNORECASE
        if match_case:
            # Flip the bits back to case sensative.
            flags = flags ^ re.IGNORECASE
        match_re = re.compile(match_pattern, flags)
        for file_path in self._find_files(
            self.root_dir, file_pattern=file_pattern):
            file_match = self.extract_match(
                file_path, match_re, substitution=substitution)
            if file_match:
                yield file_match

    def _find_files(self, skip_dir_pattern='^[.]', file_pattern='.*'):
        """Iterate the matching files below a directory."""
        skip_dir_re = re.compile(r'^.*%s' % skip_dir_pattern)
        file_re = re.compile(r'^.*%s' % file_pattern)
        for path, subdirs, files in os.walk(self.root_dir):
            subdirs[:] = [dir_ for dir_ in subdirs
                          if skip_dir_re.match(dir_) is None]
            for file_ in files:
                file_path = os.path.join(path, file_)
                if os.path.islink(file_path):
                    continue
                if file_re.match(file_path) is not None:
                    yield file_path

    def extract_match(self, file_path, match_re, substitution=None):
        """Return a FileMatch summarising the matches in a file, or None."""
        lines = []
        content = []
        match = None
        file_ = open(file_path, 'r')
        try:
            for lineno, line in enumerate(file_):
                match = match_re.search(line)
                if match:
                    lines.append(LineMatch(lineno + 1, line.strip()))
                    if substitution:
                        line = match_re.sub(substitution, line)
                if substitution:
                    content.append(line)
        finally:
            file_.close()
        if lines:
            if substitution:
                file_ = open(file_path, 'w')
                try:
                    file_.write(''.join(content))
                finally:
                    file_.close()
            return FileMatch(file_path, lines)
        return None


class FindController:
    """Collect user input and output matches."""

    @staticmethod
    def get_option_parser():
        """Return the option parser for this program."""
        usage = "usage: %prog [options] root_dir file_pattern match"
        parser = OptionParser(usage=usage)
        parser.add_option(
            "-s", "--substitution", dest="substitution",
            help="The replacement string (may contain \\[0-9] match groups).")
        parser.set_defaults(substitution=None)
        return parser

    @staticmethod
    def main(argv=None):
        """Run the command line operations."""
        if argv is None:
            argv = sys.argv
        parser = FindController.get_option_parser()
        (options, args) = parser.parse_args(args=argv[1:])
        root_dir = args[0]
        file_pattern = args[1]
        match_pattern = args[2]
        substitution = options.substitution
        print "Looking for [%s] in files like %s under %s:" % (
            match_pattern, file_pattern, root_dir)
        matches_generator = MatchesGenerator(root_dir)
        for file_match in matches_generator.find(
            file_pattern, match_pattern, substitution=substitution):
            print "\n%s" % file_match.file_path
            for line_match in file_match.lines:
                print "    %s4s: %s" % (line_match.lineno, line_match.text)

