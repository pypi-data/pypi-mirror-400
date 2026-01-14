#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import re
import unreal
from typing import Optional

from ciocore.package_environment import PackageEnvironment

from ciounreal import exceptions
from ciounreal.common import context
from ciounreal.common import unreal_utils
from ciounreal.common import conductor_data
from ciounreal.common import dependency_collector


class ConductorJob:
    """
    Conductor Job payload representation
    """

    def __init__(self, mrq_job: unreal.ConductorMoviePipelineExecutorJob = None, build_context: context.Context = None):
        if not mrq_job and not build_context:
            return

        self._mrq_job = mrq_job
        self._context = build_context

        self._queue_manifest_file_path = self._save_queue_manifest_file()

        self.project: str = self._mrq_job.conductor_settings.general_settings.project
        self.job_title: str = self._resolve_job_title()
        self.instance_type: dict = self._get_instance_type()
        self.pre_emptible: bool = self._mrq_job.conductor_settings.general_settings.pre_emptible
        self.software_package_ids: list[str] = [self.get_current_software_package()['package_id']]
        self.environment: PackageEnvironment = self._get_environment()
        self.output_path: str = self._resolve_output_path()
        self.location: str = self._mrq_job.conductor_settings.advanced_settings.location_tag
        self.local_upload: bool = False if self._mrq_job.conductor_settings.uploads_settings.use_daemon else True
        self.upload_paths: list[str] = self._get_upload_paths()
        self.tasks_data: list[dict] = [
            {'command': self._resolve_task_template()}
        ]
        self.notifications: list[str] = re.findall(
            pattern=r'[\w.-]+@[\w.-]+\.\w+',
            string=self._mrq_job.conductor_settings.advanced_settings.notify
        )

    @classmethod
    def from_dict(cls, data: dict) -> "ConductorJob":
        """
        Creates a :class:`ciounreal.conductor_job.conductor_job.ConductorJob` instance from the given data

        :param data: Dictionary containing information about the Conductor Job

        :return: :class:`ciounreal.conductor_job.conductor_job.ConductorJob` instance
        :rtype: :class:`ciounreal.conductor_job.conductor_job.ConductorJob`
        """

        conductor_job = cls(None, None)
        conductor_job.project = data['project']
        conductor_job.job_title = data['job_title']
        conductor_job.instance_type = data['instance_type']
        conductor_job.pre_emptible = data['preemptible']
        conductor_job.software_package_ids = data['software_package_ids']
        conductor_job.environment = data['environment']
        conductor_job.output_path = data['output_path']
        conductor_job.location = data['location']
        conductor_job.local_upload = data['local_upload']
        conductor_job.upload_paths = data['upload_paths']
        conductor_job.tasks_data = data['tasks_data']
        conductor_job.notifications = data['notify']

        return conductor_job

    @classmethod
    def get_current_software_package(cls) -> Optional[dict]:
        """
        Get the software package that fit the current UE version.

        Uses :meth:`ciounreal.common.conductor_data.ConductorData.get_supported_software_packages()`
        to get all supported software packages and :meth:`ciounreal.common.unreal_utils.get_engine_version_number()`
        to get the current UE version

        :raises: :class:`ciounreal.exceptions.SoftwareNotFoundError`: If no suitable software package was found
        :return: Software package descriptor or None
        :rtype: Optional[dict]
        """

        engine_version_number = unreal_utils.get_engine_version_number()
        major, minor, patch = engine_version_number.split('.')
        software_packages = conductor_data.ConductorData.get_supported_software_packages()
        current_software_package = next(
            (
                package for package in software_packages
                if package['major_version'] == major and package['minor_version'] == minor
            ),
            None
        )
        if not current_software_package:
            raise exceptions.SoftwareNotFoundError(
                f'No software found for the current version: {engine_version_number}'
            )
        return current_software_package

    def _get_instance_type(self) -> Optional[dict]:
        """
        Get the instance type by description provided in the unreal.ConductorMoviePipelineExecutorJob appropriate field

        :return: Instance type descriptor or None
        :rtype: Optional[dict]
        """

        return conductor_data.ConductorData.get_instance_type_by_description(
            instance_type_description=self._mrq_job.conductor_settings.general_settings.instance_type
        )

    def _get_environment(self) -> PackageEnvironment:
        """
        Build and return the :class:`ciocore.package_environment.PackageEnvironment` object that contains:

        - Environment variables from current software package
          (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob.get_current_software_package()`)
        - Extra environments from unreal.ConductorMoviePipelineExecutorJob
        - CIO_DIR environment variable if existed (point to the directory, where ciounreal package lives)

        :return: :class:`ciocore.package_environment.PackageEnvironment` instance
        :rtype: :class:`ciocore.package_environment.PackageEnvironment`
        """

        current_software_package = self.get_current_software_package()
        environment = PackageEnvironment(current_software_package)

        env_list: list[dict] = []
        extra_environment = self._mrq_job.conductor_settings.environment_settings.variables.key_values
        for key in extra_environment:
            env_list.append(
                {
                    'name': key,
                    'value': extra_environment[key].value,
                    'merge_policy': extra_environment[key].merge_policy or 'append'
                }
            )

        if os.getenv('CIO_DIR'):
            env_list.append(
                {
                    'name': 'CIO_DIR',
                    'value': os.environ['CIO_DIR'],
                    'merge_policy': 'exclusive'
                }
            )

        env_list.append(
            {
                    'name': 'CONDUCTOR_DISABLE_PLUGIN',
                    'value': '1',
                    'merge_policy': 'exclusive'
                }
        )

        environment.extend(env_list)

        return environment

    def _get_mrq_job_dependencies(self, sync_missing: bool = True) -> list[str]:
        """
        Build and return list of dependencies of level and level sequence from unreal.ConductorMoviePipelineExecutorJob

        :param sync_missing: Whether to sync missing dependencies or not

        :return: list of dependencies of level and level sequence
        :rtype: list[str]
        """

        deps_collector = dependency_collector.DependencyCollector()

        level_sequence_path = self._context['level_sequence']
        unreal_utils.log(f'Get Level Sequence dependencies: {level_sequence_path}')
        level_sequence_dependencies = deps_collector.collect(
            asset_path=level_sequence_path,
            filter_method=dependency_collector.DependencyFilters.dependency_in_game_folder,
            sync_missing=sync_missing
        )
        level_sequence_dependencies.append(level_sequence_path)

        level_path = self._context['map_path']
        unreal_utils.log(f'Get Level dependencies: {level_path}')
        level_dependencies = deps_collector.collect(
            asset_path=level_path,
            filter_method=dependency_collector.DependencyFilters.dependency_in_game_folder,
            sync_missing=sync_missing
        )
        level_dependencies.append(level_path)

        return list(set(level_sequence_dependencies + level_dependencies))

    def _get_extra_uploads(self) -> list[str]:
        """
        Build and return list of the extra uploads paths (files and folders)
        if any added in unreal.ConductorMoviePipelineExecutorJob

        :return: list of the extra uploads paths
        :rtype: list[str]
        """

        extra_upload_paths = []

        job_extra_uploads_files = [p.file_path for p in self._mrq_job.conductor_settings.uploads_settings.files.paths]
        job_extra_uploads_folders = [p.path for p in self._mrq_job.conductor_settings.uploads_settings.folders.paths]
        job_extra_uploads = job_extra_uploads_files + job_extra_uploads_folders

        for extra_upload in job_extra_uploads:
            if os.path.exists(extra_upload):
                extra_upload_paths.append(extra_upload)
            else:
                os_path = f'{unreal_utils.get_project_directory()}/{extra_upload}'.replace('\\', '/')
                if os.path.exists(os_path):
                    extra_upload_paths.append(os_path)

        return extra_upload_paths

    def _get_mqr_job_dependency_paths(self, sync_missing: bool = True) -> list[str]:
        """
        Get MRQ Job dependencies
        (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._get_mrq_job_dependencies()`),
        convert dependencies UE paths (/Game/...) to the OS paths, filter not existed and return resulted list of paths

        :param sync_missing: Whether to sync missing dependencies or not

        :return: List of MRQ Job dependencies as local OS paths
        :rtype: list[str]
        """

        os_dependencies = []

        job_dependencies = self._get_mrq_job_dependencies(sync_missing)
        for dependency in job_dependencies:
            os_dependency = unreal_utils.os_path_from_unreal_path(dependency, with_ext=True)
            if os.path.exists(os_dependency):
                os_dependencies.append(os_dependency)

        return os_dependencies

    def _get_upload_paths(self) -> list[str]:
        """
        Build and return the paths list to upload to the CoreWeave cloud storage. Include next path types:

        - Binaries, Config and Plugins folders inside the project directory
        - Path described in `CIO_DIR` environment variable (Optional, if variable and path existed)
        - Path described in `UE_CONDUCTOR_PLUGIN_PATH` environment variable (Optional, if variable and path existed)
        - MoviePipelineQueue manifest file (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._save_queue_manifest_file()`
        - Extra uploads (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._get_extra_uploads()`
        - MRQ Job dependencies (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._get_mqr_job_dependency_paths()`)

        :return: List of local OS upload paths
        :rtype: list[str]
        """

        upload_paths = [
            unreal_utils.get_project_file_path(),
            f'{unreal_utils.get_project_directory()}/Binaries',
            f'{unreal_utils.get_project_directory()}/Config',
            f'{unreal_utils.get_project_directory()}/Plugins'
        ]

        upload_paths = [p for p in upload_paths if os.path.exists(p)]

        if os.getenv('CIO_DIR') and os.path.exists(os.getenv('CIO_DIR')):
            upload_paths.append(os.environ['CIO_DIR'])

        if os.getenv('UE_CONDUCTOR_PLUGIN_PATH') and os.path.exists(os.getenv('UE_CONDUCTOR_PLUGIN_PATH')):
            upload_paths.append(os.environ['UE_CONDUCTOR_PLUGIN_PATH'])

        if self._queue_manifest_file_path:
            upload_paths.append(self._queue_manifest_file_path)

        upload_paths.extend(self._get_extra_uploads())

        upload_paths.extend(self._get_mqr_job_dependency_paths(sync_missing=False))

        return upload_paths

    def _resolve_job_title(self) -> str:
        """
        Build job title from job template property of unreal.ConductorMoviePipelineExecutorJob
        and build context :class:`ciounreal.common.context.Context`

        :return: Job title as string
        :rtype: str
        """

        return self._mrq_job.conductor_settings.general_settings.job_title.format_map(self._context)

    def _resolve_output_path(self) -> str:
        """
        Build output path from job output_directory property of unreal.ConductorMoviePipelineExecutorJob's configuration
        and build context :class:`ciounreal.common.context.Context`

        :return: Job output path as string
        :rtype: str
        """

        output_settings = self._mrq_job.get_configuration().find_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_path: str = output_settings.output_directory.path.rstrip('/')
        return output_path.format_map(self._context)

    def _resolve_task_template(self) -> str:
        """
        Build task (cmd line) from job template property of unreal.ConductorMoviePipelineExecutorJob
        and build context :class:`ciounreal.common.context.Context`

        Example cmd line:

        ``UnrealEditor-Cmd.exe "{project_path}" -windowed -log -stdout -FullStdOutLogOutput -unattended
        -RenderOffscreen -noloadingscreen -allowstdoutlogverbosity -QueueManifest="{queue_manifest}"
        -LevelSequence="{level_sequence}" -Level="{map_path}" -execcmds="r.HLOD 0, py mrq_cli.py"``

        :return: Job task as string
        :rtype: str
        """

        task_template: str = self._mrq_job.conductor_settings.advanced_settings.template

        ctx = self._context.copy()
        ctx['queue_manifest'] = self._queue_manifest_file_path

        return task_template.format_map(ctx)

    def _save_queue_manifest_file(self) -> str:
        """
        Duplicate unreal.ConductorMoviePipelineExecutorJob object to the new unreal.MoviePipelineQueue object
        and save the queue as file

        :return: Path to the unreal.MoviePipelineQueue manifest file
        :rtype: str
        """

        new_queue = unreal.MoviePipelineQueue()
        new_queue.duplicate_job(self._mrq_job)

        # In duplicated job remove empty auto-detected files since we don't want them to be saved in manifest
        # List of the files is moved to OpenJob attachments
        # new_job.preset_overrides.job_attachments.input_files.auto_detected = unreal.ConductorFileAttachmentsArray()

        duplicated_queue, manifest_path = unreal.MoviePipelineEditorLibrary.save_queue_to_manifest_file(
            new_queue
        )
        manifest_path = unreal.Paths.convert_relative_path_to_full(manifest_path)
        return manifest_path

    def as_dict(self) -> dict:
        """
        Return instance as dictionary

        :return: :class:`ciounreal.conductor_job.conductor_job.ConductorJob` as dictionary
        :rtype: dict
        """

        return dict(
            project=self.project,
            job_title=self.job_title,
            instance_type=self.instance_type['name'],
            preemptible=self.pre_emptible,
            software_package_ids=self.software_package_ids,
            environment=dict(self.environment),
            output_path=self.output_path,
            location=self.location,
            local_upload=self.local_upload,
            upload_paths=self.upload_paths,
            tasks_data=self.tasks_data,
            notify=self.notifications
        )
