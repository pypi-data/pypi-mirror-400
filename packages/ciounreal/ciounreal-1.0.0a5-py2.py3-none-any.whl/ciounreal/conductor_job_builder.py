#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import unreal
import pprint

from ciounreal.common import context
from ciounreal.common import unreal_utils
from ciounreal.conductor_job import ConductorJob, PerforceConductorJob


class ConductorJobBuilder:

    """
    Helper class to build a Conductor Job
    """

    @classmethod
    def get_build_context(cls, mrq_job: unreal.ConductorMoviePipelineExecutorJob) -> context.Context:
        """
        Get build context from the given unreal.ConductorMoviePipelineExecutorJob

        :param mrq_job: unreal.ConductorMoviePipelineExecutorJob
        :return: :class:`ciounreal.common.context.Context` object
        :rtype: :class:`ciounreal.common.context.Context`
        """

        level_sequence_path = os.path.splitext(unreal_utils.soft_obj_path_to_str(mrq_job.sequence))[0]
        level_sequence_name = level_sequence_path.split("/")[-1]

        map_path = os.path.splitext(unreal_utils.soft_obj_path_to_str(mrq_job.map))[0]
        map_name = level_sequence_path.split("/")[-1]

        output_settings = mrq_job.get_configuration().find_setting_by_class(unreal.MoviePipelineOutputSetting)

        build_context = context.Context(
            {
                'project_path': unreal_utils.get_project_file_path(),
                'project_dir': unreal_utils.get_project_directory(),
                'job_name': mrq_job.job_name,
                'level_sequence': level_sequence_path,
                'level_sequence_name': level_sequence_name,
                'sequence_name': level_sequence_name,
                'map_path': map_path,
                'map_name': map_name,
                'level_name': map_name,
                'resolution': f'{output_settings.output_resolution.x}x{output_settings.output_resolution.y}',
            }
        )
        build_context.update(
            {
                'output_dir': output_settings.output_directory.path.format_map(build_context).replace(
                    "\\", "/"
                ).rstrip("/"),
                'filename_format': output_settings.file_name_format.format_map(build_context)
            }
        )

        return build_context

    def build_conductor_job(self, mrq_job: unreal.ConductorMoviePipelineExecutorJob) -> ConductorJob:
        """
        Build a Conductor Job from the given unreal.ConductorMoviePipelineExecutorJob

        :param mrq_job: unreal.ConductorMoviePipelineExecutorJob

        :return: ConductorJob object
        :rtype: Union[:class:`ciounreal.conductor_job.conductor_job.ConductorJob`,
                      :class:`ciounreal.conductor_job.perforce_conductor_job.PerforceConductorJob`]
        """

        build_context = self.get_build_context(mrq_job)
        job_class = PerforceConductorJob if mrq_job.conductor_settings.perforce_settings.use_perforce else ConductorJob
        job = job_class(mrq_job, build_context=build_context)
        unreal_utils.log(f'Conductor Job:')
        unreal_utils.log(pprint.pformat(job.as_dict()))
        return job
