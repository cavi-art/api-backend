"""This is the CAVI-ART Tools framework.

The tools framework provides a way of defining a toolset for
performing analysis through the CAVI-ART platform."""

from datetime import datetime
import os, subprocess
from collections import namedtuple
from contextlib import contextmanager
from glob import iglob as glob

import six

from django.core.files import File

from . import models


# Export meaningful objects
__all__ = ['ExecutionResult', 'TaskQueue', 'Tool' + 'FakeClirizeTool']


ExecutionResult = namedtuple('ExecutionResult', ['ok', 'log', 'touched_files'])

class TaskQueue(object):
    def __init__(self):
        self.registered_tools = {}

    def register_tool(self, cls):
        self.registered_tools[cls.tool_name] = cls

    def get_registered_tools(self):
        return self.registered_tools.keys()

    def get_registered_tool_choices(self):
        for k in self.registered_tools.keys():
            yield (k, self.registered_tools[k].human_readable_name)

    def run_planned(self):
        raise Exception('Not yet implemented')

    def run_task(self, operation, save=True):
        project = operation.project
        tool_ = self.registered_tools[operation.type]
        operation.status = 'R'
        if save:
            operation.save()

        with self._change_cwd(project):
            tool = tool_()
            execution_result = tool.execute()
            operation.log = execution_result.log
            operation.status = 'F' if execution_result.ok else 'X'
            print("Touched files: %s" % (execution_result.touched_files))

            # Actually create the files on BD for the relevant touched_files
            for path in execution_result.touched_files:
                file_instance, created = models.ProjectFile.objects.get_or_create(
                    project=project,
                    path=path,
                )

                if not file_instance.file_type:
                    file_instance.file_type = 'text/plain'

                with open(path, 'r') as f:
                    if created: # No previous file contents:
                        file_instance.content = File(f)
                    else:
                        file_instance.content = os.path.join(project.id.hex, path)

                    # The content already changed on disk; but we must
                    # overwrite the last_mod argument in the DB
                    file_instance.last_mod = datetime.fromtimestamp(os.path.getmtime(path))
                    file_instance.save()


        if save:
            operation.save()
        return operation

    @contextmanager
    def _change_cwd(self, project):
        prevdir = os.getcwd()
        newdir = project.get_project_root()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield newdir
        finally:
            os.chdir(prevdir)


class MetaTool(type):
    @property
    def human_readable_name(cls):
        if hasattr(cls, 'verbose_name'):
            return cls.verbose_name
        else:
            return cls.tool_name


@six.add_metaclass(MetaTool)
class Tool(object):
    tool_name = 'Unnamed tool'

    def get_relevant_files(self, file_set):
        """By default return all files as relevant. This makes the tools
        always correct even if the bandwidth transfer would not be
        optimal.

        """

        return file_set

    def execute(self):
        """Returns an ExecutionResult or the 3-tuple: (status, log, touched_files)"""
        raise Exception("You must define an execution function for tool %s." % self._get_tool_name())

    def _get_tool_name(self):
        return self.__class__.__qualname__



class FakeClirizeTool(Tool):
    tool_name = 'fake_clirize'
    params = {
        'source_files': '**/*.java',
    }

    def execute(self):
        created_files = []
        for file in glob(self.params['source_files'], recursive=True):
            with open(file) as stdin:
                p = subprocess.run(['tee', file + '.clir'], stdin=stdin, stderr=subprocess.PIPE, universal_newlines=True)
            if p.returncode != 0:
                return ExecutionResult(
                    ok=False,
                    log=p.stderr,
                    touched_files=created_files,
                )
            created_files.append(file + '.clir')
        return ExecutionResult(
            ok=True,
            log='All files passed through tee',
            touched_files=created_files,
        )


default_task_queue = TaskQueue()
default_task_queue.register_tool(FakeClirizeTool)
