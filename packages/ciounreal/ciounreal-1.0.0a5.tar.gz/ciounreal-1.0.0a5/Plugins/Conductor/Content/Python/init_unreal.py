# Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

import os
import sys

import unreal
from ciounreal.common import unreal_utils

unreal_utils.log('Initialize Conductor plugin')

from p4utilsforunreal import perforce
from ciounreal.common import conductor_data
from ciounreal.render_executors.remote_render_executor import MoviePipelineConductorRemoteExecutor
from ciounreal.render_executors.local_editor_render_executor import MoviePipelineConductorLocalEditorExecutor


os.environ['UE_CONDUCTOR_PLUGIN_PATH'] = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            __file__
        )
    )
).replace('\\', '/')
 
if os.environ.get("CONDUCTOR_DISABLE_PLUGIN") == '1':
    unreal.log("Skipping optional Conductor plugin login.")
else: 
    conductor_data.ConductorData.get_ciocore_data() # init plugin data

def refresh_conductor_data():
    with unreal.ScopedSlowTask(1, "Refresh Conductor data") as slow_task:
        slow_task.make_dialog(True)
        conductor_data.ConductorData.get_ciocore_data()
        slow_task.enter_progress_frame(1, "Refresh Conductor data")

@unreal.uclass()
class ConductorSettingsLibraryImplementation(unreal.ConductorSettingsLibrary):

    """
    Python implementation of the unreal.ConductorSettingsLibrary C++ class
    which perform retrieving settings options for the Conductor Job
    """

    @unreal.ufunction(override=True)
    def get_job_title(self):
        """
        Return Conductor Job title. By default equals to `{job_name}-{level_sequence}`

        :return: Conductor Job title as string
        :rtype: str
        """

        return "{job_name}-{level_sequence}"

    @unreal.ufunction(override=True)
    def get_instance_types(self):
        return [instance_type['description'] for instance_type in conductor_data.ConductorData.get_instance_types()]

    @unreal.ufunction(override=True)
    def get_env_merge_policy(self):
        return ["append", "prepend", "exclusive"]

    @unreal.ufunction(override=True)
    def get_projects(self):
        return conductor_data.ConductorData.get_projects()

    @unreal.ufunction(override=True)
    def get_default_task_template(self):
        return 'UnrealEditor-Cmd.exe "{project_path}" ' \
               '-windowed -log -stdout -FullStdOutLogOutput -unattended ' \
               '-RenderOffscreen -noloadingscreen -allowstdoutlogverbosity ' \
               '-QueueManifest="{queue_manifest}" ' \
               '-LevelSequence="{level_sequence}" ' \
               '-Level="{map_path}" ' \
               '-execcmds="r.HLOD 0, py mrq_cli.py"'

    @unreal.ufunction(override=True)
    def get_perforce_server(self):
        return perforce.PerforceConnection().p4.port
    
    @unreal.ufunction(override=True)
    def get_perforce_username(self):
        return perforce.PerforceConnection().p4.user

    @unreal.ufunction(override=True)
    def reconnect(self):
        refresh_conductor_data()


def add_toolbar_menu():
    command = 'refresh_conductor_data()'

    menus = unreal.ToolMenus.get()
    toolbar = menus.find_menu('LevelEditor.LevelEditorToolBar.PlayToolBar')
    toolbar.add_section(section_name='Conductor', label='Conductor')

    entry = unreal.ToolMenuEntry(type=unreal.MultiBlockType.TOOL_BAR_BUTTON)
    entry.set_label('Conductor')
    entry.set_tool_tip('Refresh conductor data')
    entry.set_icon('ConductorStyle', 'Conductor.Icon')
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name(''),
        string=command
    )
    toolbar.add_menu_entry('Conductor', entry)
    menus.refresh_all_widgets()


unreal_utils.log("Add Conductor toolbar menu")
add_toolbar_menu()
