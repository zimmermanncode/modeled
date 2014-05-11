# python-modeled
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# python-modeled is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-modeled is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python-modeled.  If not, see <http://www.gnu.org/licenses/>.

"""modeled.property

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass

__all__ = [
  'PropertyError', 'PropertiesDict', 'property',
  'ismodeledproperty', 'getmodeledproperties']

from moretools import cached, simpledict

import modeled
from .member import member, MemberError, MembersDict


class PropertiesDictStructBase(simpledict.structbase):
    """Custom `simpledict.structbase` type
       to create PropertiesDict.struct class.
    """
    def __init__(self, model, properties):
        def bases():
            for cls in model.__bases__:
                if cls is not object:
                    yield cls.properties
        # Delegates properties to SimpleDictType.__init__()
        simpledict.structbase.__init__( # First arg is struct __name__
          self, '%s.properties' % repr(model), bases(), properties)


PropertiesDict = simpledict(
  'PropertiesDict', structbase=PropertiesDictStructBase,
  dicttype=MembersDict.dicttype)


class PropertyError(MemberError):
    __module__ = 'modeled'


class Type(member.type):
    error = PropertyError

    @cached
    def __getitem__(cls, mtype):
        class typedcls(cls):
            def __init__(self, fget=None, fset=None, **options):
                cls.__init__(self, fget=fget, fset=fset, **options)

        return member.type.__getitem__(cls, mtype, typedcls)

Type.__name__ = 'property.type'


class property(with_metaclass(Type, member)):
    """Typed property member of a :class:`modeled.object`.

    - Instances can be used like Python's builtin.property,
      but each only for one member and without deleter support.
    - Instantiated like a :class:`modeled.member`,
      with additional fget and fset options.
    """
    __module__ = 'modeled'

    def __init__(self, mtype=None, fget=None, fset=None, **options):
        if mtype is None:
            assert(self.mtype)
        else:
            self.__class__ = type(self)[mtype]
        member.__init__(self, **options)
        self.fget = fget
        self.fset = fset

    def __call__(self, fget, fset=None):
        """The actual decorator function.
        """
        self.fget = fget
        self.fset = fset
        return self

    def setter(self, fset):
        """The .setter decorator function.
        """
        self.fset = fset
        return self

    def __get__(self, obj, owner=None):
        """Get the current property value via defined getter function.
        """
        if not obj: # ==> Accessed from modeled.object class level
            return self
        if not self.fget:
            raise PropertyError("'%s' has no getter." % self.name)
        value = self.fget(obj)
        if type(value) is not self.mtype:
            return self.mtype(value)
        return value

    def __set__(self, obj, value):
        """Pass a new property `value` to the defined setter function.

        - Converts value to property data type (instantiates type with value).
        """
        if not self.fset:
            raise PropertyError("'%s' has no setter." % self.name)
        if not isinstance(value, self.mtype):
            value = self.new(value)
        self.fset(obj, value)


def ismodeledproperty(obj):
    """Checks if `obj` is an instance of :class:`modeled.property`.
    """
    return isinstance(obj, property)


def getmodeledproperties(obj):
    """Get a list of all :class:`modeled.property` (name, instance) pairs
       of a :class:`modeleled.object` subclass
       or (name, value) pairs of a :class:`modeled.object` instance
       in property creation and inheritance order.
    """
    if modeled.ismodeledclass(obj):
        return list(obj.model.properties)
    if modeled.ismodeledobject(obj):
        return [(name, getattr(obj, name))
                for (name, _) in obj.model.properties]
    raise TypeError(
      "getmodeledproperties() arg must be a subclass or instance"
      " of modeled.object")
