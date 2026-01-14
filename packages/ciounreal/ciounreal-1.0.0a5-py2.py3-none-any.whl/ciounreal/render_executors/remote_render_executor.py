#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unreal
import logging

from ciounreal.common import unreal_utils
from ciounreal.conductor_job_submitter import ConductorJobSubmitter


@unreal.uclass()
class MoviePipelineConductorRemoteExecutor(unreal.MoviePipelineExecutorBase):
    """
    Movie Pipeline Executor that submit jobs to the Conductor
    """

    # The queue we are working on, null if no queue has been provided.
    pipeline_queue = unreal.uproperty(unreal.MoviePipelineQueue)
    job_ids = unreal.uproperty(unreal.Array(str))

    @unreal.ufunction(override=True)
    def execute(self, pipeline_queue):
        """
        Execute the provided Queue.
        You are responsible for deciding how to handle each job in the queue and processing them.

        Here we define totalFrameRange as frames count from the sequence/job configuration

        :param queue: The queue that this should process all jobs for
        :return: None
        """

        unreal_utils.log(f"Asked to execute Queue: {pipeline_queue}")
        unreal_utils.log(f"Queue has {len(pipeline_queue.get_jobs())} jobs")

        if not pipeline_queue or (not pipeline_queue.get_jobs()):
            self.on_executor_finished_impl()
            return

        if not self.check_dirty_packages():
            return

        if not self.check_maps(pipeline_queue):
            return

        self.pipeline_queue = pipeline_queue

        submitter = ConductorJobSubmitter()

        enabled_jobs = [job for job in self.pipeline_queue.get_jobs() if job.is_enabled()]

        for job in enabled_jobs:
            unreal_utils.log(f"Submitting Job `{job.job_name}` to CoreWeave Conductor ...")
            submitter.add_job(job)

        submitter.submit_jobs()

    @unreal.ufunction(override=True)
    def is_rendering(self):
        """
        Because we forward unfinished jobs onto another service when the
        button is pressed, they can always submit what is in the queue and
        there's no need to block the queue.

        A MoviePipelineExecutor implementation must override this. If you
        override a ufunction from a base class you don't specify the return
        type or parameter types

        :return: False
        :rtype: bool
        """

        return False

    def check_dirty_packages(self) -> bool:
        """
        Checks if the current project has dirty unsaved packages

        :return: True if there is unsaved content, False otherwise
        :rtype: bool
        """

        dirty_packages = []
        dirty_packages.extend(
            unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
        )
        dirty_packages.extend(
            unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        )

        if dirty_packages:
            if not unreal.EditorLoadingAndSavingUtils.save_dirty_packages_with_dialog(
                True, True
            ):
                message = (
                    "One or more jobs in the queue have an unsaved map/content. "
                    "{packages} "
                    "Please save and check-in all work before submission.".format(
                        packages="\n".join(dirty_packages)
                    )
                )

                unreal_utils.log(message, logging.ERROR)
                unreal.EditorDialog.show_message(
                    "Unsaved Maps/Content", message, unreal.AppMsgType.OK
                )
                self.on_executor_finished_impl()
                return False
        return True

    def check_maps(self, pipeline_queue) -> bool:
        """
        Checks if the jobs' maps is valid for remote render
        (see `unreal.MoviePipelineEditorLibrary.is_map_valid_for_remote_render <https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MoviePipelineEditorLibrary?application_version=5.3#unreal.MoviePipelineEditorLibrary.is_map_valid_for_remote_render>`__)


        :return: True if valid, False otherwise
        :rtype: bool
        """

        has_valid_map = (
            unreal.MoviePipelineEditorLibrary.is_map_valid_for_remote_render(
                pipeline_queue.get_jobs()
            )
        )
        if not has_valid_map:
            message = (
                "One or more jobs in the queue have an unsaved map as "
                "their target map. "
                "These unsaved maps cannot be loaded by an external process, "
                "and the render has been aborted."
            )
            unreal_utils.log(message, logging.ERROR)
            unreal.EditorDialog.show_message(
                "Unsaved Maps", message, unreal.AppMsgType.OK
            )
            self.on_executor_finished_impl()
            return False

        return True
