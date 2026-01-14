# Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

import os
import json
import socket
import unreal
import logging

from p4utilsforunreal import perforce, app

from ciounreal.common import unreal_utils
from ciounreal.common import dependency_collector
from ciounreal.render_executors import MoviePipelineConductorLocalEditorExecutor

# We need to keep the render executor here to make callbacks being executed after render is complete/failed
render_executor = None


def wait_for_asset_registry():
    unreal_utils.log('MRQ CLI: Waiting for asset registry completion ...')
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry.wait_for_completion()


def set_movie_pipeline_queue(movie_pipeline_queue: unreal.MoviePipelineQueue) -> unreal.MoviePipelineQueue:
    unreal_utils.log('MRQ CLI: setting Movie Pipeline Queue...')
    unreal_utils.log(f'MRQ CLI: original Movie Pipeline Queue: {movie_pipeline_queue}')

    # The queue subsystem behaves like a singleton so lear all the jobs in the current queue.
    pipeline_queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).get_queue()
    pipeline_queue.delete_all_jobs()

    # Replace the contents of this queue with a copy of the contents from another queue.
    pipeline_queue.copy_from(movie_pipeline_queue)

    unreal_utils.log(f'MRQ CLI: Resulted Movie Pipeline Queue: {pipeline_queue}')

    return pipeline_queue


def get_movie_pipeline_queue_from_manifest(mpq_manifest_path: str) -> unreal.MoviePipelineQueue:
    unreal_utils.log(f'MRQ CLI: Getting Movie Pipeline Queue from manifest: {mpq_manifest_path}')
    return unreal.MoviePipelineLibrary.load_manifest_file_from_string(mpq_manifest_path)


def executor_errored_callback(
        pipeline_executor: unreal.MoviePipelineExecutorBase,
        pipeline_with_error: unreal.MoviePipeline,
        is_fatal: bool,
        error_text: unreal.Text
):
    unreal_utils.log(f'''MoviePipelineConductorLocalEditorExecutor {pipeline_executor}: Error handled:
                     Movie Pipeline: {pipeline_with_error}
                     Fatal: {is_fatal}
                     Error: {error_text}''', logging.ERROR)

    global render_executor
    del render_executor

    unreal.SystemLibrary.quit_editor()


def executor_finished_callback(pipeline_executor: unreal.MoviePipelineExecutorBase, success: bool = None):
    unreal_utils.log(f'MoviePipelineConductorLocalEditorExecutor: Rendering is complete')
    if success is not None:
        unreal_utils.log(f'MoviePipelineConductorLocalEditorExecutor: Success: {success}')

    global render_executor
    del render_executor

    unreal.SystemLibrary.quit_editor()


def main():
    """
    UnrealEditor-Cmd.exe "{project_path}"
    -windowed -log -stdout -FullStdOutLogOutput -unattended -RenderOffscreen -noloadingscreen -allowstdoutlogverbosity
    -QueueManifest=”{queue_manifest}” -execcmds=”r.HLOD 0, py mrq_cli.py”
    """

    tokens, switchers, cmd_parameters = unreal.SystemLibrary.parse_command_line(
        unreal.SystemLibrary.get_command_line()
    )
    unreal_utils.log(f'''MRQ CLI: Parsed arguments:
                     Tokens: {tokens}
                     Switchers: {switchers}
                     CMD Parameters: {cmd_parameters}''')

    wait_for_asset_registry()

    original_queue = get_movie_pipeline_queue_from_manifest(cmd_parameters['QueueManifest'])
    pipeline_queue = set_movie_pipeline_queue(original_queue)

    global render_executor
    render_executor = MoviePipelineConductorLocalEditorExecutor()

    p4 = None

    for job in pipeline_queue.get_jobs():
        if job.conductor_settings.perforce_settings.use_perforce and not p4:
            p4_connect = perforce.PerforceConnection(required_connection=True)
            p4 = p4_connect.p4
            p4.client = app.get_workspace_name(project_name=unreal_utils.get_project_name())
            unreal_utils.log('MRQ CLI: Perforce connection established.')
        else:
            print (f"MRQ CLI: Skipping Perforce for the job: {job.job_name}")
    
        unreal_utils.log(f'MRQ CLI: Collecting dependencies for the job: {job.job_name}')
        deps_collector = dependency_collector.DependencyCollector()
        deps_collector.collect(
            asset_path=cmd_parameters['LevelSequence'],
            filter_method=dependency_collector.DependencyFilters.dependency_in_game_folder
        )
        deps_collector.collect(
            asset_path=cmd_parameters['Level'],
            filter_method=dependency_collector.DependencyFilters.dependency_in_game_folder
        )

        job_dependencies_descriptor_path = os.getenv('JOB_DEPENDENCIES_DESCRIPTOR_PATH', '')
        if os.path.exists(job_dependencies_descriptor_path):
            with open(job_dependencies_descriptor_path, 'r') as f:
                job_dependencies_data = json.load(f)
                for job_dependency in job_dependencies_data.get('job_dependencies', []):
                    if os.path.exists(job_dependency):
                        continue
                    synced = unreal.SourceControl.sync_files([job_dependency])
                    if synced:
                        unreal.AssetRegistryHelpers().get_asset_registry().scan_modified_asset_files([job_dependency])
                        unreal.AssetRegistryHelpers().get_asset_registry().scan_paths_synchronous(
                            [job_dependency], True, True
                        )

        if p4:
            job_extra_uploads_files = [p.file_path for p in job.conductor_settings.uploads_settings.files.paths]
            job_extra_uploads_folders = [p.path + '/...' for p in job.conductor_settings.uploads_settings.folders.paths]
            job_extra_uploads = job_extra_uploads_files + job_extra_uploads_folders

            for job_extra_upload in job_extra_uploads:
                try:
                    p4.run('sync', job_extra_upload)
                except Exception as e:
                    unreal_utils.log(f'Sync extra upload error: {str(e)}', logging.ERROR)
                    continue

        render_data_missed = False
        if not unreal.EditorAssetLibrary.does_asset_exist(cmd_parameters['LevelSequence']):
            render_data_missed = True
            unreal_utils.log(f'LevelSequence {cmd_parameters["LevelSequence"]} does not exist, cancel rendering')
        if not unreal.EditorAssetLibrary.does_asset_exist(cmd_parameters['Level']):
            render_data_missed = True
            unreal_utils.log(f'Level {cmd_parameters["Level"]} does not exist, cancel rendering')

        if render_data_missed:
            exit_code = 101
            unreal_utils.log(f'Level or/and LevelSequence assets are missing, exiting with exit code {exit_code}')
            unreal.ConductorMiscFunctionLibrary.request_exit(True, exit_code)

    # Add callbacks on complete and error actions to handle it and provide output
    render_executor.on_executor_finished_delegate.add_callable_unique(executor_finished_callback)
    render_executor.on_executor_errored_delegate.add_callable_unique(executor_errored_callback)

    unreal_utils.log('MRQ CLI: Starting executing Movie Pipeline Queue ...')
    render_executor.execute(pipeline_queue)


if __name__ == '__main__':
    main()
