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

"""PyAMS_alchemy.converter.csv module

This module provides a simple utility which can be used to convert an
SQLAlchemy results proxy to CSV.
"""

__docformat__ = 'restructuredtext'

import csv
import io

from pyams_alchemy.interfaces import IAlchemyConverter
from pyams_alchemy.task import IAlchemyTask
from pyams_scheduler.interfaces.task.pipeline import IPipelineOutput
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.dict import DotDict
from pyams_utils.registry import utility_config


@utility_config(name='csv',
                provides=IAlchemyConverter)
class CSVAlchemyConverter:
    """SQLAlchemy converter to CSV format"""

    mimetype = 'text/csv; charset=utf-8'

    @staticmethod
    def convert(rows, **kwargs):
        """Convert provided rows to CSV"""
        output = io.StringIO()
        keys = rows.keys()
        writer = csv.DictWriter(output, fieldnames=keys, **kwargs)
        writer.writeheader()
        for row in rows:
            value = dict(((key, getattr(row, key)) for key in keys))
            writer.writerow(value)
        output.seek(0)
        return output.read()


@adapter_config(name='csv',
                required=IAlchemyTask,
                provides=IPipelineOutput)
class AlchemyTaskCsvPipelineOutput(ContextAdapter):
    """SQLAlchemy task pipeline CSV output"""

    def get_values(self, result):
        if not result:
            return {}
        values = [
            DotDict(item)
            for item in csv.DictReader(io.StringIO(result))
        ]
        return values[0] if len(values) == 1 else values
