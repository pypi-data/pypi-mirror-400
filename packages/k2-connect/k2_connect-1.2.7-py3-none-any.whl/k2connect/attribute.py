"""
"attribute.py" creates simple python properties, getters
and setters functionality for  for attributes passed to the
attribute(key=value) function in a class.
A property name as well as private variable __name is created
and made available of instances of that class

    Example::
        >>>from k2connect.attribute import attribute
        >>>class WinterIsComing:
            ...attribute(name='John Snow')

        >>>instance_of_my_class = WinterIsComing()
        >>>instance_of_my_class.name
        'John Doe'
        >>>instance_of_my_class.name = 'Changing name to : Arya Stark'
        >>>instance_of_my_class.name
        'Changing name to : Arya Stark'
"""

import sys

__all__ = ['attribute', 'readable', 'writable']
__version__ = '3.0'
__author__ = 'Sean Ross'
__credits__ = ['Guido van Rossum', 'Garth Kidd']
__refactor__ = 'Philip Wafula'
__created__ = '10/21/02'
__modified__ = '02/07/19'


def mangle(classname, attribute_name):
    """Mangles name according to python name-mangling
       conventions for private variables"""
    return "_%s__%s" % (classname, attribute_name)


def class_space(class_level=3):
    """Returns the calling class' name and dictionary"""
    frame = sys._getframe(class_level)
    classname = frame.f_code.co_name
    class_dict = frame.f_locals
    return classname, class_dict


# create getting function
def readable(**kwds):
    """Returns one read-only property for each (key,value) pair in kwds"""
    return _attribute(permission='r', **kwds)


# create setting function
def writable(**kwds):
    """Returns one write-only property for each (key,value) pair in kwds"""
    return _attribute(permission='w', **kwds)


# needed because of the way class_space is resolved in _attribute
def attribute(permission='rwd', **kwds):
    """Returns one property for each (key,value) pair in kwds;
       each property provides the specified level of access(permission):
           'r': readable, 'w':writable, 'd':deletable
    """
    return _attribute(permission, **kwds)


# based on code by Guido van Rossum, comp.lang.python 2001-07-31
def _attribute(permission='rwd', **kwds):
    """Returns one property for each (key,value) pair in kwds;
       each property provides the specified level of access(permission):
           'r': readable, 'w':writable, 'd':deletable
    """
    classname, class_dict = class_space()

    def _property(property_attribute_name, property_default):
        property_name, property_attribute_name = property_attribute_name, \
                                                 mangle(classname, property_attribute_name)
        fget, fset, fdel, doc = None, None, None, property_name
        attr_name = property_attribute_name
        if 'r' in permission:
            def fget(self):
                value = property_default
                try:
                    value = getattr(self, attr_name)
                except AttributeError:
                    setattr(self, attr_name, property_default)
                return value
        if 'w' in permission:
            def fset(self, value):
                setattr(self, attr_name, value)
        if 'd' in permission:
            def fdel(self):
                try:
                    delattr(self, attr_name)
                except AttributeError:
                    pass
                # calling fget can restore this attribute, so remove property
                delattr(self.__class__, property_name)
        return property(fget=fget, fset=fset, fdel=fdel, doc=doc)

    for attribute_name, default in kwds.items():
        class_dict[attribute_name] = _property(attribute_name, default)


