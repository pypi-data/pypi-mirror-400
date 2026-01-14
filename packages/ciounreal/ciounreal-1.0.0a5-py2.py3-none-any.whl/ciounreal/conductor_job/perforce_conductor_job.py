#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import re
import json
import unreal
from typing import Optional

from p4utilsforunreal import perforce

from ciounreal import exceptions
from ciounreal.common import context
from ciounreal.common import unreal_utils
from ciounreal.conductor_job import ConductorJob

from ciocore.package_environment import PackageEnvironment

class PerforceConductorJob(ConductorJob):

    def __init__(self, mrq_job: unreal.ConductorMoviePipelineExecutorJob = None, build_context: context.Context = None):
        if not mrq_job and not build_context:
            return
        
        self.perforce_settings = mrq_job.conductor_settings.perforce_settings
        perforce.PerforceConnection(port=self.perforce_settings.perforce_server,
                                    user=self.perforce_settings.perforce_username,
                                    password=self.perforce_settings.perforce_password,
                                    required_connection=True)

        self._perforce_workspace_specification_template = self.get_perforce_workspace_specification_template()
        self._perforce_workspace_specification_template_path = self._save_perforce_specification_template_file()

        super().__init__(mrq_job, build_context)

    @classmethod
    def get_unreal_python_path(cls):
        """
        Get the local OS path to the Unreal Engine Python executable

        :return: UE Python executable path, e.g.
                `C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/ThirdParty/Python3/Win64/python.exe`
        :rtype: str
        """

        path_value = next(
            (env['value'] for env in cls.get_current_software_package()['environment'] if env['name'] == 'Path'),
            None
        )
        path_value = path_value.replace('\\', '/')

        ue_binaries_directory = next(
            (p for p in path_value.split(';') if 'Engine/Binaries/Win64' in p),
            None
        )

        unreal_python_path = f'{os.path.dirname(ue_binaries_directory)}/' \
                             f'ThirdParty/Python3/Win64/python.exe'.replace('\\', '/')

        return unreal_python_path

    @classmethod
    def get_perforce_settings_from_ue_source_control(cls) -> tuple[str, str, str]:
        """
        Parse /Saved/Config/WindowsEditor/SourceControlSettings.ini file inside project's directory
        and return P4 Port, User and Workspace

        :raises: :class:`ciounreal.exceptions.SourceControlProviderError`: If source control is not available or provider is invalid
        :return: P4 Port, User and Workspace tuple
        :rtype: tuple[str, str, str]
        """

        if not unreal.SourceControl.is_available():
            raise exceptions.SourceControlProviderError('Unreal Source Control is not available')

        source_control_ini = f'{unreal_utils.get_project_directory()}' \
                             f'/Saved/Config/WindowsEditor/SourceControlSettings.ini'
        if os.path.exists(source_control_ini):
            with open(source_control_ini, 'r') as f:
                lines = f.readlines()
            provider = next((l.split('=')[1].replace('\n', '') for l in lines if l.startswith('Provider')))
            if provider != 'Perforce':
                raise exceptions.SourceControlProviderError(
                    'Perforce is not current Source Control provider. Please, update settings and reopen the project. '
                    f'Current provider: {provider}'
                )
            port = next((l.split('=')[1].replace('\n', '') for l in lines if l.startswith('Port')), None)
            user = next((l.split('=')[1].replace('\n', '') for l in lines if l.startswith('UserName')), None)
            workspace = next((l.split('=')[1].replace('\n', '') for l in lines if l.startswith('Workspace')), None)
            return port, user, workspace
        else:
            raise FileNotFoundError(f'SourceControlSettings.ini not found: {source_control_ini}')

    @classmethod
    def get_perforce_workspace_specification_template(cls) -> Optional[dict]:
        """
        Build and return Perforce workspace specification template (dictionary) that consist of

        - Client (workspace name)
        - Root (workspace local root)
        - Stream (connected Stream name)
        - View (list of view path mappings, if no Stream was defined in original configuration - non-stream workspace)

        :raises: :class:`ciounreal.exceptions.PerforceWorkspaceNotFoundError`: If the workspace was not found
        :return: Perforce workspace specification template dictionary
        :rtype: Optional[dict]
        """

        port, user, workspace = cls.get_perforce_settings_from_ue_source_control()
        if not all([port, user, workspace]):
            raise exceptions.SourceControlProviderError(
                f'Failed to fetch Source control settings. Port: {port}, User: {user}, Workspace: {workspace}'
            )

        workspace_specification = perforce.get_perforce_workspace_specification(port=port, user=user, client=workspace)
        if not workspace_specification:
            raise exceptions.PerforceWorkspaceNotFoundError(
                'No Perforce workspace found. Please check P4 environment and try again'
            )

        workspace_name = workspace_specification['Client']
        workspace_root = workspace_specification['Root']

        workspace_name_template = 'workspace_name'.join('{}')

        workspace_specification_template = {
            'Client': workspace_name_template,
            'Root': workspace_root
        }

        if workspace_specification.get('Stream'):
            workspace_specification_template['Stream'] = workspace_specification['Stream']
        elif workspace_specification.get('View'):
            view_regex = rf'.*(\/\/{workspace_name}\/).*'
            view_templates = []
            for view in workspace_specification['View']:
                match = re.match(view_regex, view)
                if match and len(match.groups()) == 1 and match.groups()[0] == f'//{workspace_name}/':
                    view_templates.append(
                        view.replace(f'//{workspace_name}/', f'//{workspace_name_template}/')
                    )
                else:
                    view_templates.append(view)
            workspace_specification_template['View'] = view_templates

        return workspace_specification_template

    def _save_perforce_specification_template_file(self) -> Optional[str]:
        """
        Save the perforce specification template to the JSON file and return its path if exists

        :return: the path of the perforce specification template JSON file
        :rtype: Optional[str]
        """

        if not self._perforce_workspace_specification_template:
            return

        save_path = f'{unreal_utils.saved_dir}/perforce_specification_template.json'
        with open(save_path, 'w') as f:
            json.dump(self._perforce_workspace_specification_template, f, indent=4)

        return save_path

    def _resolve_task_template(self) -> str:
        """
        Build task (cmd line) from job template property of unreal.ConductorMoviePipelineExecutorJob
        and build context :class:`ciounreal.common.context.Context`

        Override parent task template (:meth:`ciounreal.conductor_job.conductor_job.ConductorJob._resolve_task_template()`)
        and add two commands:

        - Create P4 workspace before launch UE command
        - Delete P4 workspace after launch UE command

        Example cmd line:

        ``& %CIO_DIR%/p4utilsforunreal/cli.py create_workspace -UnrealProjectRelativePath={ue_project_relative_path}
        -PerforceWorkspaceSpecificationTemplate={_perforce_workspace_specification_template_path}
        -PerforceServer={perforce_server};
        UnrealEditor-Cmd.exe "{project_path}" -windowed -log -stdout -FullStdOutLogOutput -unattended
        -RenderOffscreen -noloadingscreen -allowstdoutlogverbosity -QueueManifest="{queue_manifest}"
        -LevelSequence="{level_sequence}" -Level="{map_path}" -execcmds="r.HLOD 0, py mrq_cli.py";
        & %CIO_DIR%/p4utilsforunreal/cli.py delete_workspace -UnrealProjectRelativePath={ue_project_relative_path}``

        :return: Job task as string
        :rtype: str
        """

        unreal_task_template = super()._resolve_task_template()

        unreal_project_path = unreal_utils.get_project_file_path().replace('\\', '/')
        workspace_root = self._perforce_workspace_specification_template['Root'].replace('\\', '/')
        unreal_project_relative_path = unreal_project_path.replace(workspace_root + '/', '')

        perforce_server = (self._mrq_job.conductor_settings.perforce_settings.perforce_server
                           or perforce.PerforceConnection().p4.port)

        unreal_python_path = self.get_unreal_python_path()

        p4utils_for_unreal_cli_path = f'{os.getenv("CIO_DIR")}/p4utilsforunreal/cli.py'.replace('\\', '/')

        # p4utils_exe = f'{unreal_utils.get_project_directory()}' \
        #               f'/Plugins/Conductor/Content/Python/p4utils-for-unreal.exe'.replace('\\', '/')

        create_workspace_template = \
            f'& "{unreal_python_path}" "{p4utils_for_unreal_cli_path}" create_workspace ' \
            f'-UnrealProjectRelativePath="{unreal_project_relative_path}" ' \
            f'-PerforceWorkspaceSpecificationTemplate="{self._perforce_workspace_specification_template_path}" ' \
            f'-PerforceServer="{perforce_server}"'

        delete_workspace_template = \
            f'& "{unreal_python_path}" "{p4utils_for_unreal_cli_path}" delete_workspace ' \
            f'-UnrealProjectRelativePath="{unreal_project_relative_path}"'

        # Save last exit code after Unreal process is complete
        save_ue_exit_code_template = f'$UE_EXIT_CODE = $LASTEXITCODE'

        # After workspace is deleted, exit with UE code if its bad (!=0), exit with last operation code otherwise
        exit_template = 'if ($UE_EXIT_CODE -ne 0) {exit $UE_EXIT_CODE} else {exit $LASTEXITCODE}'

        task_template = f'{create_workspace_template}; ' \
                        f'{unreal_task_template}; ' \
                        f'{save_ue_exit_code_template}; ' \
                        f'{delete_workspace_template}; ' \
                        f'{exit_template}'

        return task_template

    def _get_environment(self) -> PackageEnvironment:
        """"
        Build and return the :class:`ciocore.package_environment.PackageEnvironment` object that contains:

        - Environment variables from current software package
          (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob.get_current_software_package()`)
        - Extra environments from unreal.ConductorMoviePipelineExecutorJob
        - CIO_DIR environment variable if existed (point to the directory, where ciounreal package lives)
        - P4PORT, P4USER, P4PASSWD environment variables

        :return: :class:`ciocore.package_environment.PackageEnvironment` instance
        :rtype: :class:`ciocore.package_environment.PackageEnvironment`
        """
        environment = super()._get_environment()

        p4_vars = {"P4PORT": self.perforce_settings.perforce_server,
                    "P4USER": self.perforce_settings.perforce_username,
                    "P4PASSWD": self.perforce_settings.perforce_password}
            
        for p4_var, p4_value in p4_vars.items():
            try:
                env_list = [{'name': p4_var,
                            'value': p4_value,
                            'merge_policy': 'exclusive'
                            }]
                environment.extend(env_list)
            except ValueError:
                raise Exception(f"Invalid variable, please remove '{p4_var}' from your Conductor Environment Settings.")

        return environment

    def _get_upload_paths(self) -> list[str]:
        """
        Build and return the paths list to upload to the CoreWeave cloud storage. Include next path types:

        - Path described in `CIO_DIR` environment variable (Optional, if variable and path existed)
        - Path described in `UE_CONDUCTOR_PLUGIN_PATH` environment variable (Optional, if variable and path existed)
        - MoviePipelineQueue manifest file (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._save_queue_manifest_file()`
        - Extra uploads (see :meth:`ciounreal.conductor_job.conductor_job.ConductorJob._get_extra_uploads()`
        - P4 Workspace specification template file path (see :meth:`ciounreal.conductor_job.perforce_conductor_job.PerforceConductorJob.get_perforce_workspace_specification_template()`)

        :return: List of local OS upload paths
        :rtype: list[str]
        """
        upload_paths = []

        if self._queue_manifest_file_path:
            upload_paths.append(self._queue_manifest_file_path)

        upload_paths.extend(self._get_extra_uploads())

        if os.getenv('CIO_DIR') and os.path.exists(os.getenv('CIO_DIR')):
            upload_paths.append(os.environ['CIO_DIR'])

        if os.getenv('UE_CONDUCTOR_PLUGIN_PATH') and os.path.exists(os.getenv('UE_CONDUCTOR_PLUGIN_PATH')):
            upload_paths.append(os.environ['UE_CONDUCTOR_PLUGIN_PATH'])

        upload_paths.append(self._perforce_workspace_specification_template_path)

        job_dependencies = self._get_mqr_job_dependency_paths(sync_missing=False)
        job_dependencies_descriptor_path = f'{unreal_utils.get_project_directory()}/Saved/{self._mrq_job.job_name}_dependencies.json'
        with open(job_dependencies_descriptor_path, 'w') as f:
            json.dump({'job_dependencies': job_dependencies}, f, indent=4)

        upload_paths.append(job_dependencies_descriptor_path)

        self.environment.extend(
            env_list=[
                {
                    'name': 'JOB_DEPENDENCIES_DESCRIPTOR_PATH',
                    'value': job_dependencies_descriptor_path,
                    'merge_policy': 'exclusive'
                }
            ]
        )

        return upload_paths
