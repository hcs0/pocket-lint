'''Test module for cssccc'''

from unittest import TestCase, main as unittest_main


from pocketlint.contrib.cssccc import (
     CSSCodingConventionChecker, CSSAtRule, CSSRuleSet, CSSStatementMember)


class TestCSSCodingConventionChecker(TestCase):
    '''Test for CSS code convention checker.'''

    def test_getNextRule_start(self):
        text = 'selector{}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('selector', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)

        text = '\nselector{}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('\nselector', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)

        text = '\n\nselector{}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('\n\nselector', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)

        text = 'selector\n{}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('selector\n', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)

        text = 'selector, {}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('selector, ', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)

    def test_getNextRule_content(self):
        text = 'selector { content; }'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual(' content; ', rule.declarations.text)
        self.assertEqual(0, rule.declarations.start_line)
        self.assertEqual(10, rule.declarations.start_character)

        text = 'selector \n{\n content; }'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('\n content; ', rule.declarations.text)
        self.assertEqual(1, rule.declarations.start_line)
        self.assertEqual(1, rule.declarations.start_character)

    def test_getNextRule_continue(self):
        text = 'selector1\n { content1; }\n\nselector2\n{content2}\n'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('selector1\n ', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)
        self.assertEqual(' content1; ', rule.declarations.text)
        self.assertEqual(1, rule.declarations.start_line)
        self.assertEqual(2, rule.declarations.start_character)

        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('\n\nselector2\n', rule.selector.text)
        self.assertEqual(1, rule.selector.start_line)
        self.assertEqual(14, rule.selector.start_character)
        self.assertEqual('content2', rule.declarations.text)
        self.assertEqual(4, rule.declarations.start_line)
        self.assertEqual(1, rule.declarations.start_character)

    def test_getNextRule_stop(self):
        text ='rule1{st1\n}\n@font-face {\n src: url("u\n u"); \n }\nr2{st2}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.failUnlessRaises(StopIteration, lint.getNextRule)

    def test_getNextRule_comment(self):
        text = '/*com*/\nselector\n{\n/*com*/\ncontent1;/*com*/\ncontent2;}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('selector\n', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)
        self.assertEqual('\ncontent1;\ncontent2;', rule.declarations.text)
        self.assertEqual(2, rule.declarations.start_line)
        self.assertEqual(1, rule.declarations.start_character)

    def test_get_at_import_rule(self):
        '''Test for @import url(/css/screen.css) screen, projection;'''
        text ='rule1{st1\n}\n@import  url(somet) print, soment ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        self.assertTrue(rule.block is None)
        self.assertEqual('import', rule.identifier)
        self.assertEqual('\n@import ', rule.keyword.text)
        self.assertEqual(1, rule.keyword.start_line)
        self.assertEqual(1, rule.keyword.start_character)
        self.assertEqual(' url(somet) print, soment ', rule.text.text)
        self.assertEqual(2, rule.text.start_line)
        self.assertEqual(8, rule.text.start_character)

    def test_get_at_charset_rule(self):
        '''Test for @charset "ISO-8859-15";'''
        text ='rule1{st1\n}\n@charset  "utf" ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        self.assertTrue(rule.block is None)
        self.assertEqual('charset', rule.identifier)
        self.assertEqual('\n@charset ', rule.keyword.text)
        self.assertEqual(1, rule.keyword.start_line)
        self.assertEqual(1, rule.keyword.start_character)
        self.assertEqual(' "utf" ', rule.text.text)
        self.assertEqual(2, rule.text.start_line)
        self.assertEqual(9, rule.text.start_character)

    def test_get_at_namespace_rule(self):
        '''Test for @namespace  foo  "http://foo" ;'''
        text ='rule1{st1\n}@namespace  foo  "http://foo" ;rule2{st2}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        self.assertTrue(rule.block is None)
        self.assertEqual('namespace', rule.identifier)
        self.assertEqual('@namespace ', rule.keyword.text)
        self.assertEqual(1, rule.keyword.start_line)
        self.assertEqual(1, rule.keyword.start_character)
        self.assertEqual(' foo  "http://foo" ', rule.text.text)
        self.assertEqual(1, rule.text.start_line)
        self.assertEqual(12, rule.text.start_character)

    def test_get_at_page_rule(self):
        '''Test for @page

        @page :left {
          margin-left: 5cm; /* left pages only */
        }
        '''
        text ='rule1{st1\n}\n@page :left {\n  mar; /*com*/\n }\nrule2{st2}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        self.assertTrue(rule.text is None)
        self.assertEqual('page', rule.identifier)
        self.assertEqual('\n@page :left ', rule.keyword.text)
        self.assertEqual(1, rule.keyword.start_line)
        self.assertEqual(1, rule.keyword.start_character)
        self.assertEqual('\n  mar; \n ', rule.block.text)
        self.assertEqual(2, rule.block.start_line)
        self.assertEqual(13, rule.block.start_character)

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
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSAtRule.type)
        self.assertTrue(rule.text is None)
        self.assertEqual('font-face', rule.identifier)
        self.assertEqual('\n@font-face ', rule.keyword.text)
        self.assertEqual(1, rule.keyword.start_line)
        self.assertEqual(1, rule.keyword.start_character)
        self.assertEqual('\n src: url("u\n u"); \n ', rule.block.text)
        self.assertEqual(2, rule.block.start_line)
        self.assertEqual(12, rule.block.start_character)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.failUnlessRaises(StopIteration, lint.getNextRule)


class TestCSSStatementMember(TestCase):
    '''Tests for CSSStatementMember.'''

    def test_getStartLine(self):
        statement = CSSStatementMember(0, 4, 'some')
        self.assertEqual(1, statement.getStartLine())
        statement = CSSStatementMember(3, 4, 'some')
        self.assertEqual(4, statement.getStartLine())
        statement = CSSStatementMember(3, 4, '\n\nsome')
        self.assertEqual(6, statement.getStartLine())


if __name__ == '__main__':
    unittest_main()
