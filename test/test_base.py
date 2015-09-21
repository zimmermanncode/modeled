"""Test :mod:`modeled.base`,
   defining base class and metaclass for all modeled components.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import warnings
from warnings import catch_warnings
from inspect import getmembers
from itertools import chain

from modeled.base import metabase, base
import modeled

import pytest


def test_metabase():
    """Test :class:`modeled.base.metabase`,
       the metaclass of :class:`modeled.base`.
    """
    # should not be available in modeled toplevel
    assert metabase not in (obj for (_, obj) in getmembers(modeled))

    # check convenience classmethod for getting mro of metaclass
    assert metabase.metamro() == metabase.mro(metabase) \
        == type.mro(metabase)

    # check that dir(metabase) is not broken somehow
    assert sorted(dir(metabase)) == sorted(type.__dir__(metabase))


def test_base():
    """Test :class:`modeled.base.base`.
    """
    # should not be available in modeled top-level
    assert base not in (obj for (_, obj) in getmembers(modeled))

    # check metaclass and .meta property
    assert base.meta is type(base) is metabase
    # and deprecation of .type property
    with pytest.warns(DeprecationWarning), catch_warnings():
        warnings.simplefilter('always')
        assert base.type is metabase

    # check convenience classmethod for getting mro of metaclass
    assert base.metamro() == metabase.mro(metabase)

    # check that __dir__ also returns all metaclass attribute names
    assert sorted(dir(base)) == sorted(set(chain(
        type.__dir__(base), dir(metabase))))
