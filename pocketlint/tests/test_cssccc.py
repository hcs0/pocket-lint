'''Test module for cssccc'''

from unittest import TestCase, main as unittest_main


from pocketlint.contrib.cssccc import (
     CSSCodingConventionChecker, CSSAtRule, CSSRuleSet, CSSStatementMember)


class TestCSSCodingConventionChecker(TestCase):
    '''Test for parsing the CSS text.'''

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
        text = '/*c\nm*/\nsel\n{\ns/*com*/\ncont1;/*com*/\ncont2;}'
        lint = CSSCodingConventionChecker(text)
        rule = lint.getNextRule()
        self.assertTrue(rule.type is CSSRuleSet.type)
        self.assertEqual('sel\n', rule.selector.text)
        self.assertEqual(0, rule.selector.start_line)
        self.assertEqual(0, rule.selector.start_character)
        self.assertEqual('\ns\ncont1;\ncont2;', rule.declarations.text)
        self.assertEqual(3, rule.declarations.start_line)
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


class RuleTesterBase(TestCase):
    '''Base class for rule checkers.'''

    def setUp(self):
        self.logs = []

    def log(self, line_number, code, message):
        self.logs.append((line_number, code, message))

    @property
    def last_log_code(self):
        (line_number, code, message) = self.logs.pop()
        return code


class TestCSSRuleSetSelectorChecks(RuleTesterBase):
    '''Test coding conventions for selector from rule sets.'''

    def test_valid_selector(self):

        selector = CSSStatementMember(0, 0, 'something\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual([], self.logs)

        selector = CSSStatementMember(0, 0, '\nsomething\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual([], self.logs)

        selector = CSSStatementMember(1, 0, '\n\nsomething\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual([], self.logs)

        selector = CSSStatementMember(2, 0, '\n\nsomething,\nsomethi\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual([], self.logs)

        selector = CSSStatementMember(3, 0, '\n\nsom:some some,\n#somethi\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual([], self.logs)

    def test_I002(self):
        selector = CSSStatementMember(0, 0, '\n\n\nsomething\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I002', self.last_log_code)
        selector = CSSStatementMember(0, 0, '\n\n\n\nsomething\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I002', self.last_log_code)

    def test_I003(self):
        selector = CSSStatementMember(2, 0, '\nsomething\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I003', self.last_log_code)

        selector = CSSStatementMember(2, 0, 'something\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I003', self.last_log_code)

    def test_I004(self):
        selector = CSSStatementMember(0, 0, '\nsomething, something\n')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I004', self.last_log_code)

    def test_I005(self):
        selector = CSSStatementMember(0, 0, '\nsomething,\nsomething')
        rule = CSSRuleSet(selector=selector, declarations=None, log=self.log)
        rule.checkSelector()
        self.assertEqual('I005', self.last_log_code)


class TestCSSRuleSetDeclarationsChecks(RuleTesterBase):
    '''Test coding conventions for declarations from rule sets.'''

    def test_valid_declarations(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some: 3px;\n    other:\n        url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual([], self.logs)

    def test_I006(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some: 3px;\n    other: url();')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I006', self.last_log_code)

    def test_I007(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some: 3px; other: url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I007', self.last_log_code)

    def test_I008(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some: 3px;\n  other: url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I008', self.last_log_code)

        stmt = CSSStatementMember(
            0, 0, '\n    some: 3px;\n     other: url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I008', self.last_log_code)

    def test_I009(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some 3px;\n    other: url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I009', self.last_log_code)

        stmt = CSSStatementMember(
            0, 0, '\n    some: 3:px;\n    other: url();\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I009', self.last_log_code)

    def test_I010(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some : 3px;\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I010', self.last_log_code)

    def test_I011(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some:3px;\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I011', self.last_log_code)

    def test_I012(self):
        stmt = CSSStatementMember(
            0, 0, '\n    some:  3px;\n')
        rule = CSSRuleSet(selector=None, declarations=stmt, log=self.log)
        rule.checkDeclarations()
        self.assertEqual('I012', self.last_log_code)


if __name__ == '__main__':
    unittest_main()
