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

"""PyAMS_alchemy.converter.json module

This module provides a utility which can be used to convert an SQLAlchemy
results proxy to JSON.
"""

__docformat__ = 'restructuredtext'

import json

from pyams_alchemy.interfaces import IAlchemyConverter
from pyams_alchemy.task import IAlchemyTask
from pyams_scheduler.interfaces.task.pipeline import IPipelineOutput
from pyams_scheduler.task.pipeline import BasePipelineOutput
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import utility_config


@utility_config(name='json',
                provides=IAlchemyConverter)
class JSONAlchemyConverter:
    """SQLAlchemy converter to JSON format"""

    mimetype = 'application/json; charset=utf-8'

    @staticmethod
    def convert(rows, **kwargs):  # pylint: disable=unused-argument
        """Convert provided rows to JSON"""
        result = []
        append = result.append
        keys = rows.keys()
        for row in rows:
            value = dict(((key, getattr(row, key)) for key in keys))
            append(value)
        if len(result) == 1:
            result = result[0]
        return json.dumps(result)


@adapter_config(name='json',
                required=IAlchemyTask,
                provides=IPipelineOutput)
class AlchemyTaskJsonPipelineOutput(BasePipelineOutput):
    """SQLAlchemy task pipeline JSON output"""
