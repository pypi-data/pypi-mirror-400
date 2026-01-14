#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import unreal
from ciounreal.common import unreal_utils

@unreal.uclass()
class MoviePipelineConductorLocalEditorExecutor(unreal.MoviePipelinePIEExecutor):
    """
    Movie Pipeline Executor that executes render and log progress to the console
    """

    totalFrameRange = unreal.uproperty(int)
    currentFrame = unreal.uproperty(int)

    def _post_init(self):
        """
        Constructor that gets called when created either via C++ or Python
        Note that this is different from the standard __init__ function of Python
        """

        self.totalFrameRange = 0
        self.currentFrame = 0

    @unreal.ufunction(override=True)
    def execute(self, queue: unreal.MoviePipelineQueue):
        """
        Execute the provided Queue.
        You are responsible for deciding how to handle each job in the queue and processing them.

        Here we define totalFrameRange as frames count from the sequence/job configuration

        :param queue: The queue that this should process all jobs for
        """

        try:
            # get the single job from queue
            jobs = queue.get_jobs()
            if len(jobs) == 0:
                self.log(f'Render Executor: Error: {queue} has {len(jobs)} jobs')

            job = jobs[0]

            # get output settings block
            output_settings = job.get_configuration().find_or_add_setting_by_class(
                unreal.MoviePipelineOutputSetting
            )

            # if user override frame range, use overridden values
            if output_settings.use_custom_playback_range:
                self.totalFrameRange = output_settings.custom_end_frame - output_settings.custom_start_frame

            # else use default frame range of the level sequence
            else:
                level_sequence = unreal.EditorAssetLibrary.load_asset(
                    unreal.SystemLibrary.conv_soft_object_reference_to_string(
                        unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(
                            job.sequence
                        )
                    )
                )
                if level_sequence is None:
                    self.log('Error: Level Sequence not loaded. Check if the sequence exists and is valid')

                self.totalFrameRange = level_sequence.get_playback_end() - level_sequence.get_playback_start()

            if self.totalFrameRange == 0:
                self.log(f'Cannot render the Queue with frame range of zero length')
        except Exception as e:
            exit_code = 102
            self.log(f'Error handled during rendering: {str(e)}. Quit with Exit Code {exit_code}')
            unreal.ConductorMiscFunctionLibrary.request_exit(True, exit_code)

        # don't forget to call parent's execute to run the render process
        super().execute(queue)

    @unreal.ufunction(override=True)
    def on_begin_frame(self):
        """
        Called once at the beginning of each engine frame (e.g. tick, fps)
        Since the executor will work with Play in Editor widget, each rendered frame will match with widget frame tick.
        """

        super(MoviePipelineConductorLocalEditorExecutor, self).on_begin_frame()

        # Since PIEExecutor launching Play in Editor before mrq is rendering, we should ensure, that
        # executor actually rendering the sequence.
        if self.is_rendering():
            self.currentFrame += 1
            progress = self.currentFrame / self.totalFrameRange * 100

            # Executor work with the render queue after all frames are rendered - do all
            # support stuff, handle safe quit, etc, so we should ignore progress that more than 100
            if progress <= 100:
                self.log(f'Progress: {progress}')

    @classmethod
    def log(cls, message: str):
        """
        Log message to the console with prepended executor name

        :param message: message to log
        """

        unreal_utils.log('MoviePipelineConductorLocalEditorExecutor: {}'.format(message))
