# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Format text and code"""

import os
import re
import sys
from textwrap import wrap


def selection_to_one_line():
    """Convert the selection to one line."""
    lines = []
    for line in os.sys.stdin:
        lines.append(line.strip())
    long_line = ' ' + ' '.join(lines)
    os.sys.stdout.write(long_line.strip())


def wrap_selection_list():
    """Wrap long lines and preserve indentation."""
    paras = []
    indent_re = re.compile('^( +[0-9*-]*\.*)')
    for line in os.sys.stdin:
        match = indent_re.match(line)
        if match is not None:
            symbol = match.group(1)
            # When there is not symbol in the indent, remove a space
            # because a space is automatically added for the symbol.
            if not symbol.replace(' ', ''):
                symbol = symbol[0:-1]
        else:
            symbol = ''
        padding_size = len(symbol)
        padding = ' ' * padding_size
        run = 72 - padding_size
        new_lines = []
        new_line = [symbol]
        new_length = padding_size
        # ignore the symbol
        words = line.split()
        for word in words[1:]:
            # The space between the words is 1
            if new_length + 1 + len(word) > run:
                new_lines.append(' '.join(new_line))
                new_line = [padding]
                new_length = padding_size
            new_line.append(word)
            new_length += 1 + len(word)
        new_lines.append(' '.join(new_line))
        paras.extend(new_lines)
    os.sys.stdout.write('\n'.join(paras))


def wrap_selection_para(long_line=None):
    """Wrap long lines."""
    paras = []
    indent_re = re.compile('^( +[0-9*-]\.*)')
    if long_line:
        source = long_line.split('\n')
    else:
        source = os.sys.stdin
    for line in source:
        match = indent_re.match(line)
        if match is not None:
            symbol = match.group(1)
        else:
            symbol = ''
        padding_size = len(symbol)
        padding = ' ' * padding_size
        run = 72 - padding_size
        new_lines = []
        new_line = [symbol]
        new_length = padding_size
        # ignore the symbol
        words = line.split()
        if symbol != '':
            words = words[1:]
        for word in words:
            # The space between the words is 1
            if new_length + 1 + len(word) > run:
                new_lines.append(' '.join(new_line).strip())
                new_line = [padding]
                new_length = padding_size
            new_line.append(word)
            new_length += 1 + len(word)
        new_lines.append(' '.join(new_line).strip())
        paras.extend(new_lines)
    os.sys.stdout.write('\n'.join(paras))


def newline_ending():
    """Fix the selection's line endings."""
    lines = []
    for line in os.sys.stdin:
        lines.append(line.rstrip())
    text = '\n'.join(lines)
    os.sys.stdout.write(text)


def _format_paragraph(paragraph, lines):
    """Rewrap the paragraph and normalize leading blank lines."""
    long_line = ' '.join(paragraph).strip()
    paragraph_lines = wrap(long_line, 72)
    # One blank line between blocks, except for headings, which
    # should have two leading blanks
    if len(lines) != 0 and long_line[0] == '=':
        paragraph_lines.insert(0, '')
    return paragraph_lines


def quote_line():
    """Quote the selected text passage."""
    lines = []
    for line in os.sys.stdin:
        lines.append('> %s' % line)
    os.sys.stdout.write(''.join(lines))


def rewrap_selection():
    """Rewrap the selection."""
    lines = []
    for line in os.sys.stdin:
        lines.append(line.strip())
    long_line = ' ' + ' '.join(lines)
    wrap_selection_para(long_line=long_line)


def sort_imports():
    """Sort python imports."""
    lines = []
    for line in os.sys.stdin:
        lines.append(line.strip())
    text = ' '.join(lines)
    imports = text.split(', ')
    imports = sorted(imports, key=str.lower)
    imports = [imp.strip() for imp in imports if imp != '']
    wrap_selection_para(', '.join(imports))

