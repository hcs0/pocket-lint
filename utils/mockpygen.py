#!/usr/bin/python
# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""Generate mock python implementations from a defs file."""

from codegen.definitions import (BoxedDef, EnumDef, FlagsDef,
     FunctionDef, InterfaceDef, MethodDef, ObjectDef, PointerDef, VirtualDef)
from codegen.defsparser import DefsParser

import keyword
import optparse
from string import Template
import sys

class MockBoxedDef(BoxedDef):
    """Convert of GObjects to PyObjects."""

    def write_code(self, fp=sys.stdout):
        """Unimpelmented."""
        pass

class MockEnumDef(EnumDef):
    """Enumerated constants."""
    template = Template ("""
$val = '$name'""")

    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""
        for name, val in self.values:
            params = {'name' : name, 'val' : val}
            fp.write(self.template.substitute(params))


class MockFlagsDef(FlagsDef):
    """Python flags defined at the start of the block."""
    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""


class MockFunctionDef(FunctionDef):
    """A mock python function that returns data from the test environment."""
    module_template = Template ("""
def $name($params):
    \"\"\"A mock implementation of $name.\"\"\"

""")
    class_template = Template ("""
    def $name($params):
        \"\"\"A mock implementation of $name.\"\"\"
""")

    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""
        if hasattr(self, 'of_object'):
            template = self.class_template
        else:
            template = self.module_template
        if self.params:
            symbols = []
            for param in self.params:
                # params (ptype, pname, pdflt, pnull)
                symbols.append(safe_name(param[1]))
            params = ', '.join(symbols)
        else:
            params = ''
        params = {'name' : self.name, 'params' : params}
        fp.write(template.substitute(params))


class MockInterfaceDef(InterfaceDef):
    """A python interface."""
    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""


class MockMethodDef(MethodDef):
    """A mock python method that returns data from the test environment."""
    template = Template ("""
    def $name(self$params):
        \"\"\"A mock implementation of $name.\"\"\"
""")

    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""
        if self.params:
            symbols = []
            for param in self.params:
                # params (ptype, pname, pdflt, pnull)
                symbols.append(safe_name(param[1]))
            params = ', ' + ', '.join(symbols)
        else:
            params = ''
        subs = {'name' : self.name, 'params' : params}
        fp.write(self.template.substitute(subs))


class MockObjectDef(ObjectDef):
    """A mock Python class."""
    template = Template ("""

class $name($parent):
    \"\"\"A mock implementation of $name.\"\"\"
""")

    def write_code(self, fp=sys.stdout, methods=None):
        """Write mock python implemention."""
        params = {'name' : self.name, 'parent' : parent_name(self.parent)}
        fp.write(self.template.substitute(params))
        for method in methods:
            method.write_code(fp)

class MockPointerDef(PointerDef):
    """."""

    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""


class MockVirtualDef(VirtualDef):
    """."""

    def write_code(self, fp=sys.stdout):
        """Write mock python implemention."""


class MockDefsParser(DefsParser):
    """Module and class generator from def files."""


    def define_object(self, *args):
        """Add a new object to the defs."""
        odef = MockObjectDef(*args)
        self.objects.append(odef)
        self.c_name[odef.c_name] = odef

    def define_interface(self, *args):
        """Add a new interface to the defs."""
        idef = MockInterfaceDef(*args)
        self.interfaces.append(idef)
        self.c_name[idef.c_name] = idef

    def define_enum(self, *args):
        """Add a new enum to the defs."""
        edef = MockEnumDef(*args)
        self.enums.append(edef)
        self.c_name[edef.c_name] = edef

    def define_flags(self, *args):
        """Add new flags to the defs."""
        fdef = MockFlagsDef(*args)
        self.enums.append(fdef)
        self.c_name[fdef.c_name] = fdef

    def define_boxed(self, *args):
        """Add a new boxed type to the defs."""
        bdef = MockBoxedDef(*args)
        self.boxes.append(bdef)
        self.c_name[bdef.c_name] = bdef

    def define_pointer(self, *args):
        """Add a new pointer type to the defs."""
        pdef = MockPointerDef(*args)
        self.pointers.append(pdef)
        self.c_name[pdef.c_name] = pdef

    def define_function(self, *args):
        """Add a new function to the defs."""
        fdef = MockFunctionDef(*args)
        self.functions.append(fdef)
        self.c_name[fdef.c_name] = fdef

    def define_method(self, *args):
        """Add a new method to the defs."""
        mdef = MockMethodDef(*args)
        self.functions.append(mdef)
        self.c_name[mdef.c_name] = mdef

    def define_virtual(self, *args):
        """Add a new virtual class to the defs."""
        vdef = MockVirtualDef(*args)
        self.virtuals.append(vdef)

    def write_code(self, fp=sys.stdout):
        """Write the top-level objects and functions."""
        fp.write('''"""A mock implemetation of objects."""''')
        fp.write("""

import gobject
from gobject import *
import gtk
#from gtk import *
import gtk.gdk
from gtk.gdk import *
import gtksourceview
from gtksourceview import *
import gnome
from gnome import *
""") 
        for enum in self.enums:
            enum.write_code(fp)
        if self.enums:
            fp.write('\n')
        functions = [func for func in self.functions
                     if not hasattr(func, 'of_object')]
        for func in functions:
            func.write_code(fp)
        for obj in self.objects:
            methods = [meth for meth in self.functions
                         if (hasattr(meth, 'of_object')
                            and meth.of_object == obj.c_name)]
            obj.write_code(fp, methods=methods)
#         for boxed in self.boxes:
#             boxed.write_defs(fp)
#         for pointer in self.pointers:
#             pointer.write_defs(fp)


def parent_name(name):
    """Strip the G/Gtk namespace prefix to move the name from C to Python."""
    if name.startswith('GtkSource'):
        name = name[3:]
    elif name.startswith('Gtk'):
        name = 'gtk.%s' % name[3:]
    return name


def safe_name(name):
    """Return a safe parameter name.
    
    When name conflicts with a keyword or builtin, it is escaped with
    a leading underscore ('_').
    """
    if keyword.iskeyword(name) or name in dir(__builtins__):
        name = '_%s' % name
    return name


def parse_args():
    """Parse the command line arguments and return the options."""
    parser = optparse.OptionParser(
        usage="usage: %prog [options] defs-file source-file")
    parser.add_option(
        "-f", "--force", help="Overwrite file if it exists", default=False)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("wrong number of arguments")
    return (options, args)


if __name__ == '__main__':
    (options, args) = parse_args()
    module_file = open(args[1], 'w')
    parser = MockDefsParser(args[0])
    parser.startParsing()
    parser.write_code(module_file)
