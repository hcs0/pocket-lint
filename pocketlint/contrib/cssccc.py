'''
This code is in the public domain.

Check CSS code for some common coding conventions.
The code must be in a valid CSS format.
It is recommend to first parse it using cssutils.

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
'''

from unittest import TestCase, main as unittest_main
#import re


#        '''Check the text and sent messages to logger.'''
#        for line_no, line in enumerate(self._text.splitlines()):
#            if ' ,' in line:
#                self.message(
#                    line_no, 'Whitespace before \',\'', icon='info')

#            if self.no_space_after_comma_pattern.search(line):
#                self.message(
#                    line_no, 'Missing whitespace after \',\'', icon='info')

#            if ' :' in line:
#                self.message(
#                    line_no, 'Whitespace before \':\'', icon='info')

#            if self.no_space_after_colon_pattern.search(line):
#                self.message(
#                    line_no, 'Missing whitespace after \':\'', icon='info')

#            if ' ;' in line:
#                self.message(
#                    line_no, 'Whitespace before \';\'', icon='info')

#            if self.no_space_before_curly_pattern.search(line):
#                self.message(
#                    line_no, 'No space before \'{\'', icon='info')

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

    def logDefault(self, line_no, message, icon='error'):
        '''Log the message to STDOUT.'''
        print '    %4s:%s: %s' % (line_no, icon, message)

    def check(self):
        for style in self.getStyles():
            print style.selector
            print style.declarations

    def getStyles(self):
        '''Generates the next CSS style ignoring comments.'''
        yield self.getNextStyle()

    def getNextStyle(self):
        '''Return the next parsed style.

        Return none if we are at the last style.
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

            # Look for comment start/end and update comment level .
            before_comment = ''
            after_comment = ''
            comment_start = data.find(COMMENT_START)
            if comment_start != -1:
                comment_started = True
                before_comment = data[:comment_start]

            comment_end = data.find(COMMENT_END)
            if comment_end != -1:
                comment_started = False
                after_comment = data[comment_end+2:]

            if comment_started:
                # We are inside a comment.
                # Add the data before the comment and go to next line.
                if before_comment != '':
                    result.append(before_comment)
                self.character_number = 0
                self.line_number += 1
                continue

            initial_position = data.find(stop_character)

            if before_comment != '' or after_comment != '':
                data = before_comment + after_comment

            if initial_position == -1:
                # Go to next line and append the data.
                result.append(data)
                self.character_number = 0
                self.line_number += 1
                continue
            else:
                # Go to next character and append data until marker.
                new_position = data.find(stop_character)
                result.append(data[:new_position])
                self.character_number += initial_position + 1
                break

        return CSSStatementMember(
            start_line=start_line,
            start_character=start_character,
            text=''.join(result))


class TestCSSCodingConventionChecker(TestCase):
    '''Test for CSS lint.'''

    def test_getNextStyle_start(self):
        text = 'selector{}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('selector', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)

        text = '\nselector{}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('\nselector', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)

        text = '\n\nselector{}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('\n\nselector', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)

        text = 'selector\n{}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('selector\n', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)

        text = 'selector, {}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('selector, ', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)

    def test_getNextStyle_content(self):
        text = 'selector { content; }'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual(' content; ', style.declarations.text)
        self.assertEqual(0, style.declarations.start_line)
        self.assertEqual(10, style.declarations.start_character)

        text = 'selector \n{\n content; }'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('\n content; ', style.declarations.text)
        self.assertEqual(1, style.declarations.start_line)
        self.assertEqual(1, style.declarations.start_character)

    def test_getNextStyle_continue(self):
        text = 'selector1\n { content1; }\n\nselector2\n{content2}\n'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('selector1\n ', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)
        self.assertEqual(' content1; ', style.declarations.text)
        self.assertEqual(1, style.declarations.start_line)
        self.assertEqual(2, style.declarations.start_character)

        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('\n\nselector2\n', style.selector.text)
        self.assertEqual(1, style.selector.start_line)
        self.assertEqual(14, style.selector.start_character)
        self.assertEqual('content2', style.declarations.text)
        self.assertEqual(4, style.declarations.start_line)
        self.assertEqual(1, style.declarations.start_character)

    def test_getNextStyle_stop(self):
        text ='rule1{st1\n}\n@font-face {\n src: url("u\n u"); \n }\nr2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.failUnlessRaises(StopIteration, lint.getNextStyle)

    def test_getNextStyle_comment(self):
        text = '/*comment*/\nselector\n{content1;/*comment*/\ncontent2;}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.assertEqual('\nselector\n', style.selector.text)
        self.assertEqual(0, style.selector.start_line)
        self.assertEqual(0, style.selector.start_character)
        self.assertEqual('content1;\ncontent2;', style.declarations.text)
        self.assertEqual(2, style.declarations.start_line)
        self.assertEqual(1, style.declarations.start_character)

    def test_get_at_import_rule(self):
        '''Test for @import url(/css/screen.css) screen, projection;'''
        text ='rule1{st1\n}\n@import  url(somet) print, soment ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        self.assertTrue(style.block is None)
        self.assertEqual('import', style.identifier)
        self.assertEqual('\n@import ', style.keyword.text)
        self.assertEqual(1, style.keyword.start_line)
        self.assertEqual(1, style.keyword.start_character)
        self.assertEqual(' url(somet) print, soment ', style.text.text)
        self.assertEqual(2, style.text.start_line)
        self.assertEqual(8, style.text.start_character)

    def test_get_at_charset_rule(self):
        '''Test for @charset "ISO-8859-15";'''
        text ='rule1{st1\n}\n@charset  "utf" ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        self.assertTrue(style.block is None)
        self.assertEqual('charset', style.identifier)
        self.assertEqual('\n@charset ', style.keyword.text)
        self.assertEqual(1, style.keyword.start_line)
        self.assertEqual(1, style.keyword.start_character)
        self.assertEqual(' "utf" ', style.text.text)
        self.assertEqual(2, style.text.start_line)
        self.assertEqual(9, style.text.start_character)

    def test_get_at_namespace_rule(self):
        '''Test for @namespace  foo  "http://foo" ;'''
        text ='rule1{st1\n}@namespace  foo  "http://foo" ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        self.assertTrue(style.block is None)
        self.assertEqual('namespace', style.identifier)
        self.assertEqual('@namespace ', style.keyword.text)
        self.assertEqual(1, style.keyword.start_line)
        self.assertEqual(1, style.keyword.start_character)
        self.assertEqual(' foo  "http://foo" ', style.text.text)
        self.assertEqual(1, style.text.start_line)
        self.assertEqual(12, style.text.start_character)

    def test_get_at_page_rule(self):
        '''Test for @page

        @page :left {
          margin-left: 5cm; /* left pages only */
        }
        '''
        text ='rule1{st1\n}\n@page :left {\n  mar; /*com*/\n }\nrule2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        self.assertTrue(style.text is None)
        self.assertEqual('page', style.identifier)
        self.assertEqual('\n@page :left ', style.keyword.text)
        self.assertEqual(1, style.keyword.start_line)
        self.assertEqual(1, style.keyword.start_character)
        self.assertEqual('\n  mar; \n ', style.block.text)
        self.assertEqual(2, style.block.start_line)
        self.assertEqual(13, style.block.start_character)

    def test_get_at_font_face_rule(self):
        '''Test for @font-face

        @font-face {
          font-family: "Example Font";
          src: url("http://www.example.com
              /fonts/example");
        }
        '''
        text ='rule1{st1\n}\n@font-face {\n src: url("u\n u"); \n }\nr2{st2}'
        lint = CSSCodingConventionChecker(text)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSAtRule.type)
        self.assertTrue(style.text is None)
        self.assertEqual('font-face', style.identifier)
        self.assertEqual('\n@font-face ', style.keyword.text)
        self.assertEqual(1, style.keyword.start_line)
        self.assertEqual(1, style.keyword.start_character)
        self.assertEqual('\n src: url("u\n u"); \n ', style.block.text)
        self.assertEqual(2, style.block.start_line)
        self.assertEqual(12, style.block.start_character)
        style = lint.getNextStyle()
        self.assertTrue(style.type is CSSRuleSet.type)
        self.failUnlessRaises(StopIteration, lint.getNextStyle)


if __name__ == '__main__':
    unittest_main()
