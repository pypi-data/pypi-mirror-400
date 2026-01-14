#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import json
import unreal
import logging
import datetime
import threading
import traceback
from typing import Union
from enum import IntEnum

from ciocore import config
from ciocore.conductor_submit import Submit
from ciocore.uploader.upload_stats import UploadStats

from ciounreal.common import unreal_utils
from ciounreal.conductor_job import ConductorJob
from ciounreal.conductor_job_builder import ConductorJobBuilder


class UnrealConductorJobSubmitStatus(IntEnum):
    """
    Job submission status
    """

    UPLOADING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELED = 4


# TODO make pretty clickable link
class SubmittedConductorJobDescriptor:
    """
    Submitted Conductor Job payload.
    Consist of job name, https response and response code
    """

    def __init__(self, job_name: str, submission_response: dict, submission_response_code: int):
        self.job_name = job_name
        self.submission_response = submission_response
        self.submission_response_code = submission_response_code

        if isinstance(self.submission_response_code, int) and self.submission_response_code <= 201:
            job_uri = self.submission_response['uri'].rstrip('/').lstrip('/').replace('jobs', 'job')
        else:
            job_uri = ''

        self.job_url = f'{config.config().config["url"]}/{job_uri}'

    def __str__(self):
        return f'{self.job_name} - {self.job_url}'


class ConductorJobSubmitter:
    """
    Main class that manage Conductor Job submission process
    """

    def __init__(self, silent_mode: bool = False):
        self._silent_mode = silent_mode

        self._jobs: list[ConductorJob] = []
        self._job_builder = ConductorJobBuilder()

        self._submission: Union[Submit, None] = None
        self._submit_status: Union[UnrealConductorJobSubmitStatus, None] = None
        self._submit_message: Union[str, None] = None
        self._submit_failed_message: Union[str, None] = None

        self._progress_list: list[float] = []
        self._submitted_job_descriptors: list[SubmittedConductorJobDescriptor] = []

    @property
    def submit_failed_message(self):
        """
        Last submission error message

        :return: Last submission error message
        :rtype: str
        """

        return self._submit_failed_message

    @classmethod
    def save_conductor_job_to_file(cls, job: ConductorJob) -> str:
        """
        .. warning::
           FOR DEBUG ONLY

        Save Conductor Job payload to JSON file to %APPDATA%/Conductor/ciounreal/jobs/<current_datetime>.json
        instead of real submit

        To use it, set env variable CIOUNREAL_DEBUG as "True":
        os.environ['CIOUNREAL_DEBUG'] = 'True'

        To not, set env variable CIOUNREAL_DEBUG as "False":
        os.environ['CIOUNREAL_DEBUG'] = 'False'

        :param job: :class:`ciounreal.conductor_job.conductor_job.ConductorJob`
        :return: path to saved JSON file
        :rtype: str
        """

        jobs_directory = f'{os.getenv("APPDATA")}/Conductor/ciounreal/jobs'
        os.makedirs(jobs_directory, exist_ok=True)
        with open(f'{jobs_directory}/{datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.json', 'w') as f:
            json.dump(
                job.as_dict(),
                f,
                indent=4
            )

        return f.name

    def _display_progress(self, submit_status: UnrealConductorJobSubmitStatus, title: str):
        """
        Display submission progress with unreal.ScopedSlowTask

        :param submit_status: target submission status
        :param title: target title to display
        """

        last_progress = 0
        with unreal.ScopedSlowTask(100, title) as submit_task:
            submit_task.make_dialog(can_cancel=False)  # Cancel work only for uploader, so disable cancelling here
            while self._submit_status == submit_status:
                if self._submit_status == UnrealConductorJobSubmitStatus.FAILED:
                    break

                if submit_task.should_cancel():
                    self._submission.stop_work()
                    self._submit_status = UnrealConductorJobSubmitStatus.CANCELED
                    break

                if len(self._progress_list) > 0:
                    new_progress = self._progress_list.pop(0)
                else:
                    new_progress = last_progress
                # work_increment = new_progress - last_progress if new_progress > last_progress else 0
                # submit_task.enter_progress_frame(work_increment, self._submit_message)
                submit_task.enter_progress_frame(new_progress - last_progress, self._submit_message)
                last_progress = new_progress

    def _uploader_time_formatter(self, time_delta):
        """
        Format uploader time (datetime.timedelta) to string.
        
        :param time_delta: Uploader time ('N/A', 'hh:mm:ss.sss', 'hh:mm:ss')
        :return: Formatted upload time
        :rtype: str
        """
        return f'{time_delta}'.split('.')[0]
    
    def _uploader_progress_handler(self, upload_stats: UploadStats):
        """
        Callback function that passed to :class:`ciocore.conductor_submit.Submit`
        to track current upload progress and display in UI

        :param upload_stats: :class:`ciocore.uploader.upload_stats.UploadStats`
        """

        self._submit_status = UnrealConductorJobSubmitStatus.UPLOADING

        unreal_utils.log(f'Uploader progress: {upload_stats.get_formatted_text()}')

        elapsed_time = self._uploader_time_formatter(upload_stats.elapsed_time)
        time_remaining = self._uploader_time_formatter(upload_stats.time_remaining)

        self._submit_message = f'{upload_stats.bytes_uploaded} / {upload_stats.bytes_to_upload}, ' \
                               f'transfer rate {upload_stats.transfer_rate}/s, ' \
                               f'{elapsed_time} / {time_remaining}'

        completion = upload_stats.percent_complete.value  # Can be N/A
        if completion:
            self._progress_list.append(completion * 100)  # value between 0.0 and 1.0, convert to UE 0.0 to 100.0

    def _start_submit(self, job: ConductorJob):
        """
        Start submission process of the given job

        :param job: :class:`ciounreal.conductor_job.conductor_job.ConductorJob`
        """
        try:
            self._submission = Submit(job.as_dict())
            if job.local_upload:
                self._submission.progress_handler = self._uploader_progress_handler
            response, response_code = self._submission.main()
            unreal_utils.log(f'Submission response: {response}, {response_code}')

            self._submit_status = UnrealConductorJobSubmitStatus.COMPLETED
            self._submitted_job_descriptors.append(
                SubmittedConductorJobDescriptor(job.job_title, response, response_code)
            )

        except Exception as e:
            unreal_utils.log(str(e), logging.ERROR)
            self._submit_failed_message = str(e)
            self._submit_status = UnrealConductorJobSubmitStatus.FAILED

    def _submission_result_dialog(
            self,
            message: str,
            title='Conductor Job Submission',
            message_type=unreal.AppMsgType.OK
    ):
        """
        Display submission result dialog

        :param message: Submission result message
        :param title: Submission result title
        :param message_type: unreal message type (see unreal.AppMsgType)
        """

        unreal_utils.log(f'{title}: {message}')

        if self._silent_mode:
            return

        unreal.EditorDialog.show_message(
            title=unreal.Text(title),
            message=unreal.Text(message),
            message_type=message_type
        )

    def delete_jobs(self):
        """
        Clear list of the jos to submit
        """

        self._jobs.clear()

    def add_job(self, mrq_job: unreal.ConductorMoviePipelineExecutorJob):
        """
        Add a new job to the submission list

        :param mrq_job: unreal.ConductorMoviePipelineExecutorJob
        """

        try:
            self._jobs.append(self._job_builder.build_conductor_job(mrq_job))
        except Exception as e:
            self._submission_result_dialog(f'Job {mrq_job.job_name} failed to submit due to an error: \n{str(e)}')
            unreal_utils.log(traceback.format_exc())

    def submit_jobs(self):
        """
        Submit all the added jobs to Conductor.
        """

        for job in self._jobs:
            job._save_queue_manifest_file()

            if os.getenv('CIOUNREAL_DEBUG', 'False') == 'True':
                save_path = self.save_conductor_job_to_file(job)
                self._submission_result_dialog(
                    message=f'Job saved in {save_path}',
                    title='Conductor Job Submission DEBUG'
                )
                continue

            self._submit_status = UnrealConductorJobSubmitStatus.UPLOADING
            self._submit_message = 'Start submitting ...'
            self._progress_list = []

            t = threading.Thread(target=self._start_submit, args=(job,), daemon=True)
            t.start()

            self._display_progress(submit_status=UnrealConductorJobSubmitStatus.UPLOADING, title='Uploading')

            t.join()

            unreal_utils.log(f'SUBMISSION STATUS: {self._submit_status.value}')
            if self._submit_status == UnrealConductorJobSubmitStatus.FAILED:
                self._submission_result_dialog(
                    f'Job {job.job_title} failed to submit due to an error: \n{self.submit_failed_message}'
                )

            elif self._submit_status == UnrealConductorJobSubmitStatus.CANCELED:
                self._submission_result_dialog(
                    f'Jobs submission canceled.\n'
                    f'Number of not submitted jobs: {len(self._jobs) - len(self._submitted_job_descriptors)}'
                )
                break

        self._submission_result_dialog(
            f'Submitted jobs ({len(self._submitted_job_descriptors)}):\n' +
            '\n'.join([str(j) for j in self._submitted_job_descriptors])
        )
