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

"""PyAMS_alchemy.task module

This module defines a PyAMS_scheduler task which can be used to schedule
any SQL command execution.
"""

import json
import pprint
import re
import sys
import traceback
from datetime import datetime, timezone

from sqlalchemy.exc import ResourceClosedError, SQLAlchemyError
from sqlalchemy.sql import text
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_alchemy.engine import get_user_session
from pyams_alchemy.interfaces import IAlchemyConverter
from pyams_alchemy.task.interfaces import IAlchemyTask
from pyams_scheduler.interfaces.task import TASK_STATUS_EMPTY, TASK_STATUS_FAIL, TASK_STATUS_OK
from pyams_scheduler.interfaces.task.pipeline import IPipelineOutput
from pyams_scheduler.interfaces.task.report import ITaskResultReportInfo
from pyams_scheduler.task import Task
from pyams_utils.adapter import ContextRequestAdapter, adapter_config
from pyams_utils.dict import merge_dict
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_pyramid_registry, get_utility
from pyams_utils.text import render_text
from pyams_utils.timezone import tztime

__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


@factory_config(IAlchemyTask)
class AlchemyTask(Task):
    """SQLAlchemy task"""

    label = _("SQL query")
    icon_class = 'fas fa-database'

    session_name = FieldProperty(IAlchemyTask['session_name'])
    query = FieldProperty(IAlchemyTask['query'])
    params = FieldProperty(IAlchemyTask['params'])
    output_format = FieldProperty(IAlchemyTask['output_format'])
    log_output = FieldProperty(IAlchemyTask['log_output'])

    def run(self, report, **kwargs):  # pylint: disable=unused-argument
        """Run SQL query task"""
        session = get_user_session(self.session_name,
                                   join=False,
                                   twophase=False,
                                   use_zope_extension=False)
        try:
            try:
                query = render_text(self.query)
                report.writeln('SQL query output', prefix='### ')
                report.writeln('SQL query:', suffix='\n')
                report.write_code(query.replace('\r', '').replace('\n', '\n    '))
                params = self.params or {}
                if params:
                    params = json.loads(params)
                input_params = kwargs.get('params')
                if input_params:
                    if not params:
                        params = input_params
                    elif isinstance(params, dict):
                        if isinstance(input_params, list):
                            for input_param in input_params:
                                merge_dict(params, input_param)
                            params = input_params
                        else:
                            merge_dict(input_params, params)
                    elif isinstance(params, list):
                        params.append(input_params)
                if params and self.log_output:
                    report.writeln(f'SQL query params:', suffix='\n')
                    report.write_code(pprint.pformat(params))
                results = session.execute(text(query), params)
                session.commit()
                converter = get_utility(IAlchemyConverter, name=self.output_format)
                result = converter.convert(results)
                if self.log_output:
                    report.writeln(f"SQL output: {results.rowcount} "
                                   f"record{'s' if results.rowcount > 1 else ''}", suffix='\n')
                    if not self.attach_reports:
                        report.write_code(result)
                return TASK_STATUS_OK, result
            except ResourceClosedError:
                report.writeln('SQL query returned no result.', suffix='\n')
                return TASK_STATUS_EMPTY, None
        except SQLAlchemyError:
            session.rollback()
            report.writeln('**An SQL error occurred**', suffix='\n')
            report.write_exception(*sys.exc_info())
            return TASK_STATUS_FAIL, None


@adapter_config(required=IAlchemyTask,
                provides=IPipelineOutput)
def alchemy_task_pipeline_output(context):
    """SQLAlchemy task pipeline output"""
    registry = get_pyramid_registry()
    return registry.queryAdapter(context, IPipelineOutput, name=context.output_format)


@adapter_config(required=(IAlchemyTask, Interface),
                provides=ITaskResultReportInfo)
class AlchemyTaskReportInfo:
    """SQLAlchemy task result report info"""
    
    def __init__(self, task, result):
        self.task = task
        self.result = result
        
    @property
    def mimetype(self):
        converter = get_utility(IAlchemyConverter, name=self.task.output_format)
        return converter.mimetype

    @property
    def filename(self):
        now = tztime(datetime.now(timezone.utc))
        return f'report-{now:%Y%m%d}-{now:%H%M%S-%f}.{self.task.output_format}'

    @property
    def content(self):
        return self.result
