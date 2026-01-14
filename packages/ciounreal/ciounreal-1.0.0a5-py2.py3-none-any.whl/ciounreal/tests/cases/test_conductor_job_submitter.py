#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import time
import unreal
import unittest
from unittest.mock import Mock, MagicMock, PropertyMock, patch

from ciounreal.conductor_job_submitter import ConductorJobSubmitter, UnrealConductorJobSubmitStatus


PIPELINE_QUEUE = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).get_queue()


def submission_main_mock():
    return {'body': 'job submitted.', 'jobid': '00004', 'status': 'success', 'uri': '/jobs/00004'}, 201


def submission_main_fail_mock():
    return {'body': 'Frightful error', 'status': 'error'}, 500


class TestUnrealSubmitter(unittest.TestCase):

    def test_add_job(self, submitter: ConductorJobSubmitter = None, delete: bool = False):

        submitter = submitter or ConductorJobSubmitter(silent_mode=True)

        for job in PIPELINE_QUEUE.get_jobs():
            submitter.add_job(job)

        self.assertIsNot(len(submitter._jobs), 0)

        if delete:
            submitter.delete_jobs()

    @patch('ciounreal.conductor_job_submitter.Submit.main', side_effect=submission_main_mock)
    def test_submit_jobs(self, submission_main_mock: Mock):

        submitter = ConductorJobSubmitter(silent_mode=True)
        self.test_add_job(submitter, delete=False)
        submitter.submit_jobs()

        submission_main_mock.assert_called_once()

    @patch('ciounreal.conductor_job_submitter.Submit.main', side_effect=submission_main_mock)
    @patch('ciounreal.conductor_job_submitter.ConductorJobSubmitter._submission_result_dialog', new_callable=MagicMock)
    def test_cancel_submit_jobs(self, submission_main_mock: Mock, submission_result_dialog_mock: MagicMock):

        submitter = ConductorJobSubmitter(silent_mode=True)
        self.test_add_job(submitter, delete=False)

        with patch.object(submitter, '_submit_status', UnrealConductorJobSubmitStatus.CANCELED):
            submitter.submit_jobs()

        submission_main_mock.assert_called_once()

        submission_result_dialog_mock.assert_called_once_with(
            f'Jobs submission canceled.\n'
            f'Number of not submitted jobs: 1'
        )

    @patch('ciounreal.conductor_job_submitter.ConductorJobSubmitter.submit_failed_message', new_callable=PropertyMock)
    @patch('ciounreal.conductor_job_submitter.Submit.main', side_effect=submission_main_fail_mock)
    @patch('ciounreal.conductor_job_submitter.ConductorJobSubmitter._submission_result_dialog', new_callable=MagicMock)
    def test_fail_submit_jobs(
            self,
            submission_result_dialog_mock: MagicMock,
            submission_main_fail_mock: Mock,
            submit_failed_message_mock: Mock
    ):

        submit_failed_message_mock.side_effect = ['Test interrupt submission']

        submitter = ConductorJobSubmitter(silent_mode=True)
        self.test_add_job(submitter, delete=False)

        with patch.object(submitter, '_submit_status', UnrealConductorJobSubmitStatus.FAILED):
            submitter.submit_jobs()

        submission_main_fail_mock.assert_called_once()

        submit_failed_message_mock.assert_called_once()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnrealSubmitter)
    unittest.TextTestRunner(stream=sys.stdout, buffer=True).run(suite)
