"""Find in files and replace strings in many files."""


__metaclass__ = type


from optparse import OptionParser
import os
import re
import sys


class FindGenerator:
    """Search files for matching text."""

    @staticmethod
    def find_matches(root_dir, file_pattern, match_pattern,
                     substitution=None):
        """Iterate a summary of matching lines in a file."""
        match_re = re.compile(match_pattern)
        for file_path in FindGenerator.find_files(
            root_dir, file_pattern=file_pattern):
            summary = FindGenerator.extract_match(
                file_path, match_re, substitution=substitution)
            if summary:
                yield summary

    @staticmethod
    def find_files(root_dir, skip_dir_pattern='^[.]', file_pattern='.*'):
        """Iterate the matching files below a directory."""
        skip_dir_re = re.compile(r'^.*%s' % skip_dir_pattern)
        file_re = re.compile(r'^.*%s' % file_pattern)
        for path, subdirs, files in os.walk(root_dir):
            subdirs[:] = [dir_ for dir_ in subdirs
                          if skip_dir_re.match(dir_) is None]
            for file_ in files:
                file_path = os.path.join(path, file_)
                if os.path.islink(file_path):
                    continue
                if file_re.match(file_path) is not None:
                    yield file_path

    @staticmethod
    def extract_match(file_path, match_re, substitution=None):
        """Return a summary of matches in a file."""
        lines = []
        content = []
        match = None
        file_ = open(file_path, 'r')
        try:
            for lineno, line in enumerate(file_):
                match = match_re.search(line)
                if match:
                    lines.append(
                        {'lineno' : lineno + 1, 'text' : line.strip()})
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
            return {'file_path' : file_path, 'lines' : lines}
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
        for summary in FindGenerator.find_matches(
            root_dir, file_pattern, match_pattern, substitution=substitution):
            print "\n%(file_path)s" % summary
            for line in summary['lines']:
                print "    %(lineno)4s: %(text)s" % line

