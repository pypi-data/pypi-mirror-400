#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_alchemy.schema module

This module defines a base class which can be used to create tables whose
schema can be defined using configuration settings instead of static definition.
"""

from sqlalchemy.ext.declarative import declared_attr

from pyams_utils.registry import get_pyramid_registry


__docformat__ = 'restructuredtext'


class DynamicSchemaMixin:
    """Dynamic schema mixin class

    This class is used to set an entity schema name in Pyramid settings.
    """

    __schema__ = None

    @classmethod
    def get_schema_settings_name(cls):
        """Class table schema settings name getter"""
        return f'pyams_alchemy.{cls.__module__}.{cls.__name__}.schema'

    @classmethod
    def get_schema(cls):
        """Class table schema getter"""
        schema_name = None
        registry = get_pyramid_registry()
        if hasattr(registry, 'settings'):
            settings_name = cls.get_schema_settings_name()
            schema_name = registry.settings.get(settings_name)
            if not schema_name:
                settings_name = f'pyams_alchemy.schema.{cls.__schema__}.alias'
                schema_name = registry.settings.get(settings_name)
        return {
            'schema': schema_name or cls.__schema__
        }

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return cls.get_schema()
