#!/usr/bin/python
# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""Generate fake python implementations from a defs file."""

from codegen.definitions import (BoxedDef, EnumDef, FlagsDef,
     FunctionDef, InterfaceDef, MethodDef, ObjectDef, PointerDef, VirtualDef)
from codegen.defsparser import DefsParser
from codegen import override
from codegen.override import Overrides

import keyword
import optparse
import os
import re
from string import Template
import sys


class FakeBoxedDef(BoxedDef):
    """Convert of GObjects to PyObjects."""

    def write_code(self, fp=sys.stdout):
        """Unimpelmented."""
        pass


class FakeEnumDef(EnumDef):
    """Enumerated constants."""
    template = Template ("""
$val = '$name'""")

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""
        for name, val in self.values:
            params = {'name' : name, 'val' : val}
            fp.write(self.template.substitute(params))


class FakeFlagsDef(FlagsDef):
    """Python flags defined at the start of the block."""
    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""


class FakeFunctionDef(FunctionDef):
    """A fake python function that returns data from the test environment."""

    module_template = Template ("""
def $name($params):
    \"\"\"A fake implementation of $name.\"\"\"
    key = '%s' % '$name'
    return Fake().data.get(key, None)
""")

    class_template = Template ("""
    def $name($params):
        \"\"\"A fake implementation of $name.\"\"\"
""")

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""
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


class FakeInterfaceDef(InterfaceDef):
    """A python interface."""

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""


class FakeMethodDef(MethodDef):
    """A fake python method that returns data from the test environment."""
    template = Template ("""
    def $name(self$params):
        \"\"\"A fake implementation of $name.\"\"\"
        key = '%s_%s' % (self.__class__.__name__, '$name')
        return Fake().data.get(key, None)
""")

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""
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


class FakeObjectDef(ObjectDef):
    """A fake Python class."""
    template = Template ("""

class $name($parent):
    \"\"\"A fake implementation of $name.\"\"\"

""")

    def write_code(self, fp=sys.stdout, methods=None):
        """Write fake python implemention."""
        params = {'name' : self.name, 'parent' : parent_name(self.parent)}
        fp.write(self.template.substitute(params))
        for method in methods:
            method.write_code(fp)

class FakePointerDef(PointerDef):
    """A fake pointer generator."""

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""


class FakeVirtualDef(VirtualDef):
    """A Fake virtual generator."""

    def write_code(self, fp=sys.stdout):
        """Write fake python implemention."""


class FakeDefsParser(DefsParser):
    """Module and class generator from def files."""

    def define_object(self, *args):
        """Add a new object to the defs."""
        odef = FakeObjectDef(*args)
        self.objects.append(odef)
        self.c_name[odef.c_name] = odef

    def define_interface(self, *args):
        """Add a new interface to the defs."""
        idef = FakeInterfaceDef(*args)
        self.interfaces.append(idef)
        self.c_name[idef.c_name] = idef

    def define_enum(self, *args):
        """Add a new enum to the defs."""
        edef = FakeEnumDef(*args)
        self.enums.append(edef)
        self.c_name[edef.c_name] = edef

    def define_flags(self, *args):
        """Add new flags to the defs."""
        fdef = FakeFlagsDef(*args)
        self.enums.append(fdef)
        self.c_name[fdef.c_name] = fdef

    def define_boxed(self, *args):
        """Add a new boxed type to the defs."""
        bdef = FakeBoxedDef(*args)
        self.boxes.append(bdef)
        self.c_name[bdef.c_name] = bdef

    def define_pointer(self, *args):
        """Add a new pointer type to the defs."""
        pdef = FakePointerDef(*args)
        self.pointers.append(pdef)
        self.c_name[pdef.c_name] = pdef

    def define_function(self, *args):
        """Add a new function to the defs."""
        fdef = FakeFunctionDef(*args)
        self.functions.append(fdef)
        self.c_name[fdef.c_name] = fdef

    def define_method(self, *args):
        """Add a new method to the defs."""
        mdef = FakeMethodDef(*args)
        self.functions.append(mdef)
        self.c_name[mdef.c_name] = mdef

    def define_virtual(self, *args):
        """Add a new virtual class to the defs."""
        vdef = FakeVirtualDef(*args)
        self.virtuals.append(vdef)


class DefOverridesMixer(object):
    """Write a python source file from a pair of defs and overides files."""

    def __init__(self, defs, overrides=None):
        """Initialize the DefOverridesMixer with the defs and overrides.
        
        When overrides is none, the defs are used exclusively to create the
        python source file.
        """
        if not overrides:
            overrides = Overrides()
        self.overrides = overrides
        self.defs = defs

    def write_code(self, fp=sys.stdout):
        """Write the top-level objects and functions."""
        fp.write('''"""A fake implemetation of objects."""''')
        if self.overrides.headers:
            fp.write('%s\n\n' % self.overrides.headers)
        if self.overrides.imports:
            fp.write('%s\n\n' % '\n'.join(
                imp[0] for imp in self.overrides.imports))

        for enum in self.defs.enums:
            enum.write_code(fp)
        if self.defs.enums:
            fp.write('\n')
        functions = [func for func in self.defs.functions
                     if not hasattr(func, 'of_object')]
        for func in functions:
            func.write_code(fp)
        for obj in self.defs.objects:
            methods = [meth for meth in self.defs.functions
                         if (hasattr(meth, 'of_object')
                            and meth.of_object == obj.c_name)]
            obj.write_code(fp, methods=methods)
#         for boxed in self.defs.boxes:
#             boxed.write_defs(fp)
#         for pointer in self.defs.pointers:
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
        usage="usage: %prog [options] defs-file [python-file]")
    parser.add_option(
        "-s", "--source", help="Copy the defs from a gedit source directory",
        default=False)
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("wrong number of arguments")
    return (options, args)


if __name__ == '__main__':
    (options, args) = parse_args()
    dir_name = os.path.dirname(args[0])
    defs_file_name = os.path.basename(args[0])
    overrides_file_name = defs_file_name.replace('.defs', '.overrides')
    os.chdir(dir_name)
    # Replace the import pattern to include 'from' statements.
    override.import_pat = re.compile(r'((from|import).*)')
    if os.path.exists(overrides_file_name):
        overrides = Overrides(overrides_file_name)
    else:
        overrides = Overrides()

    if len(args) == 2:
        module_file_name = '%s.py' % args[1]
    elif overrides.modulename:
        module_file_name = '%s.py' % overrides.modulename
    else:
        module_file_name = defs_file_name.replace('.defs', '.py')
    module_file = open(module_file_name, 'w')

    defs = FakeDefsParser(defs_file_name)
    defs.startParsing()
    mixer = DefOverridesMixer(defs, overrides)
    mixer.write_code(module_file)
