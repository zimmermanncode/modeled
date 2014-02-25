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
__all__ = [
  'PropertyError', 'property',
  'ismodeledproperty', 'getmodeledproperties']

from .member import member, MemberError


class PropertyError(MemberError):
    __module__ = 'modeled'


class property(member):
    """Typed property member of a :class:`modeled.object`.

    - Instances can be used like Python's builtin.property,
      but each only for one member and without deleter support.
    - Instantiated like a :class:`modeled.member`,
      with additional fget and fset options.
    """
    __module__ = 'modeled'

    def __init__(self, dtype, fget=None, fset=None, **options):
        member.__init__(self, dtype, **options)
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
        if type(value) is not self.dtype:
            return self.dtype(value)
        return value

    def __set__(self, obj, value):
        """Pass a new property `value` to the defined setter function.

        - Converts value to property data type (instantiates type with value)
        """
        if not self.fset:
            raise PropertyError("'%s' has no setter." % self.name)
        if type(value) is not self.dtype:
            value = self.dtype(value)
        self.fset(obj, value)

    def __repr__(self):
        return 'modeled.property(%s)' % (self.dtype.__name__)


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
