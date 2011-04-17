'''
This code is in the public domain.

Check CSS code for some common coding conventions.
The code must be in a valid CSS format.
It is recommend to first parse it using cssutils.

If a comment is on the whole line, it will 'eat' the whole line like it
was not there.
If a comment is inside a line it will only 'eat' its own content.

Bases on Stoyan Stefanov's http://www.phpied.com/css-coding-conventions/

'@media' rule is not supported.
    @media print {
      html {
        background: #fff;
        color: #000;
      }
      body {
        padding: 1in;
        border: 0.5pt solid #666;
      }
    }

The following at-rules are supported:
 * keyword / text at-rules
  * @charset "ISO-8859-15";
  * @import url(/css/screen.css) screen, projection;
  * @namespace foo "http://example.com/ns/foo";
 * keybord / block rules
  * @page { block; }
  * @font-face { block; }


TODO:
 * add support for TAB as a separator.
 * add support for @media
'''

__version__ = '0.1.0'

import sys

SELECTOR_SEPARATOR = ','
COMMENT_START = r'/*'
COMMENT_END = r'*/'
AT_TEXT_RULES = ['import', 'charset', 'namespace']
AT_BLOCK_RULES = ['page', 'font-face']


class CSSAtRule(object):
    '''A CSS @rule.'''

    type = object()

    def __init__(self, identifier, keyword, text=None, block=None):
        self.identifier = identifier
        self.keyword = keyword
        self.text = text
        self.block = block


class CSSRuleSet(object):
    '''A CSS rule_set.'''

    type = object()

    def __init__(self, selector, declarations):
        self.selector = selector
        self.declarations = declarations

    def __str__(self):
        return '%s{%s}' % (str(self.selector), str(self.declarations))

    def __repr__(self):
        return '%d:%d:%s{%s}' % (
            self.selector.start_line,
            self.selector.start_character,
            str(self.selector),
            str(self.declarations),
            )


class CSSStatementMember(object):
    '''A member of CSS statement.'''

    def __init__(self, start_line, start_character, text):
        self.start_line = start_line
        self.start_character = start_character
        self.text = text

    def getStartLine(self):
        '''Return the line number for first character in the statement.'''
        index = 0
        text = self.text
        character = text[index]
        while character == '\n':
            index += 1
            character = text[index]
        return self.start_line + index + 1

    def __str__(self):
        return self.text

    def __repr__(self):
        return '%d:%d:{%s}' % (
            self.start_line, self.start_character, self.text)


class CSSCodingConventionChecker(object):
    '''CSS coding convention checker.'''

    def __init__(self, text, logger=None):
        self._text = text.splitlines(True)
        self.line_number = 0
        self.character_number = 0
        if logger:
            self.log = logger
        else:
            self.log = self.logDefault

    def logDefault(self, line_no, message, icon='info'):
        '''Log the message to STDOUT.'''
        print '    %4s:%s: %s' % (line_no, icon, message)

    def check(self):
        '''Check all rules.'''
        for rule in self.getRules():
            if rule.type is CSSRuleSet.type:
                self.checkRuleSet(rule)
            elif rule.type is CSSAtRule.type:
                self.checkAtRule(rule)
            else:
                self.log(rule.start_line, 'Unknown rule.', icon='error')
                return

    def checkRuleSet(self, rule):
        '''Check a rule set.'''
        start_line = rule.selector.getStartLine()
        selectors = rule.selector.text.split(SELECTOR_SEPARATOR)
        last_selector = selectors[-1]
        first_selector = selectors[0]
        middle_selectors = selectors[1:-1]

        if first_selector.startswith('\n\n\n'):
            self.log(start_line, 'To many newlines before selectors.')

        for selector in middle_selectors:
            if not selector.startswith(' '):
                self.log(start_line, 'No whitespace after ","')
        if not last_selector.endswith('\n'):
            self.log(start_line, 'No newline after rule selectors.')

    def checkAtRule(self, rule):
        '''Check an at rule.'''

    def getRules(self):
        '''Generates the next CSS rule ignoring comments.'''
        while True:
            yield self.getNextRule()

    def getNextRule(self):
        '''Return the next parsed rule.

        Raise `StopIteration` if we are at the last rule.
        '''
        if self._nextStatementIsAtRule():
            text = None
            block = None
            keyword = self._parse('@')
            # TODO: user regex [ \t {]
            keyword_text = self._parse(' ')
            keyword_name = keyword_text.text
            keyword.text += '@' + keyword_name + ' '

            if keyword_name.lower() in AT_TEXT_RULES:
                text = self._parse(';')
            elif keyword_name.lower() in AT_BLOCK_RULES:
                start = self._parse('{')
                keyword.text += start.text
                block = self._parse('}')
            else:
                self._parse(';')
                raise StopIteration

            return CSSAtRule(
                identifier=keyword_name,
                keyword=keyword,
                text=text,
                block=block)
        else:
            selector = self._parse('{')
            declarations = self._parse('}')
            return CSSRuleSet(
                selector=selector,
                declarations=declarations)

    def _nextStatementIsAtRule(self):
        '''Return True if next statement in the buffer is an at-rule.

        Just look for open brackets and see if there is an @ before that
        braket.
        '''
        search_buffer = []
        line_counter = self.line_number
        current_line = self._text[line_counter][self.character_number:]
        while current_line.find('@') == -1:
            search_buffer.append(current_line)
            line_counter += 1
            try:
                current_line = self._text[line_counter]
            except IndexError:
                return False

        text_buffer = ''.join(search_buffer)
        if text_buffer.find('{') == -1:
            return True
        else:
            return False

    def _parse(self, stop_character):
        '''Return the parsed text until stop_character.'''
        try:
            self._text[self.line_number][self.character_number]
        except IndexError:
            raise StopIteration
        result = []
        start_line = self.line_number
        start_character = self.character_number
        comment_started = False
        while True:
            try:
                data = self._text[self.line_number][self.character_number:]
            except IndexError:
                break

            # Look for comment start/end.
            comment_check = _check_comment(data)
            (comment_update,
            before_comment,
            after_comment,
            newline_consumed) = comment_check
            if comment_update is not None:
                comment_started = comment_update

            if comment_started:
                # We are inside a comment.
                # Add the data before the comment and go to next line.
                if before_comment is not None:
                    result.append(before_comment)
                self.character_number = 0
                self.line_number += 1
                continue

            # Strip the comment from the data.
            # Remember the initial cursor position to know where to
            # continue.
            initial_position = data.find(stop_character)
            if before_comment is not None:
                data = before_comment
            if after_comment is not None:
                if before_comment is not None:
                    data = before_comment + after_comment
                else:
                    data = after_comment

            if initial_position == -1 or newline_consumed:
                # We are not at the end.
                # Go to next line and append the data.
                result.append(data)
                self.character_number = 0
                self.line_number += 1
                continue
            else:
                # Delimiter found.
                # Find it again in the text that now has no comments.
                # Append data until the delimiter.
                # Move cursor to next character and stop searching for it.
                new_position = data.find(stop_character)
                result.append(data[:new_position])
                self.character_number += initial_position + 1
                break

        return CSSStatementMember(
            start_line=start_line,
            start_character=start_character,
            text=''.join(result))


def _check_comment(data):
    '''Check the data for comment markers.'''

    comment_started = None
    before_comment = None
    after_comment = None
    newline_consumed = False
    comment_start = data.find(COMMENT_START)
    if comment_start != -1:
        comment_started = True
        before_comment = data[:comment_start]

    comment_end = data.find(COMMENT_END)
    if comment_end != -1:
        comment_started = False
        # Comment end after the lenght of the actual comment end
        # marker.
        comment_end += len(COMMENT_END)
        if before_comment is None and data[comment_end] == '\n':
            # Consume the new line if it next to the comment end and
            # the comment in on the whole line.
            comment_end += 1
            newline_consumed = True
        after_comment = data[comment_end:]
    return (comment_started, before_comment, after_comment, newline_consumed)


def show_usage():
    '''Print the command usage.'''
    print 'Usage: cssccc OPTIONS'
    print '  -h, --help\t\tShow this help.'
    print '  -v, --version\t\tShow version.'
    print '  -f FILE, --file=FILE\tCheck FILE'


def read_file(filename):
    '''Return the content of filename.'''
    text = ''
    with open(filename, 'r') as f:
        text = f.read()
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_usage()
    elif sys.argv[1] in ['-v', '--version']:
        print 'CSS Code Convention Checker %s' % (__version__)
        sys.exit(0)
    elif sys.argv[1] == '-f':
        text = read_file(sys.argv[2])
        checker = CSSCodingConventionChecker(text)
        sys.exit(checker.check())
    elif sys.argv[1] == '--file=':
        text = read_file(sys.argv[1][len('--file='):])
        checker = CSSCodingConventionChecker(text)
        sys.exit(checker.check())
    else:
        show_usage()
