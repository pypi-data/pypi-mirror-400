#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
import unreal
import logging
from pathlib import Path


content_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
saved_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()).rstrip('/')


def get_project_file_path() -> str:
    """
    Returns the Unreal project OS path

    :return: the Unreal project OS path
    :rtype: str
    """

    if unreal.Paths.is_project_file_path_set():
        project_file_path = unreal.Paths.convert_relative_path_to_full(
            unreal.Paths.get_project_file_path()
        )
        return project_file_path
    else:
        raise RuntimeError(
            "Failed to get a project name. Please set a project!"
        )


def get_project_directory() -> str:
    """
    Returns the Unreal project directory OS path

    :return: the Unreal project directory OS path
    :rtype: str
    """

    project_file_path = get_project_file_path()
    project_directory = str(Path(project_file_path).parent).replace('\\', '/')
    return project_directory


def get_project_name() -> str:
    """
    Returns the Unreal project name without extension

    :return: Unreal project name
    :rtype: str
    """

    return Path(get_project_file_path()).stem


def soft_obj_path_to_str(soft_obj_path: unreal.SoftObjectPath) -> str:
    """
    Converts the given unreal.SoftObjectPath to the Unreal path

    :param soft_obj_path: unreal.SoftObjectPath instance

    :return: the Unreal path, e.g. /Game/Path/To/Asset
    :rtype: str
    """

    obj_ref = unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(soft_obj_path)
    return unreal.SystemLibrary.conv_soft_object_reference_to_string(obj_ref)


def os_path_from_unreal_path(unreal_path, with_ext: bool = False):
    """
    Convert Unreal path to OS path, e.g. /Game/Assets/MyAsset to C:/UE_project/Content/Assets/MyAsset.uasset.

    if parameter with_ext is set to True, tries to get type of the asset by unreal.AssetData and set appropriate extension:

    - type World - .umap
    - other types - .uasset

    If for some reason it can't find asset data (e.g. temporary level's actors don't have asset data), it will set ".uasset"

    :param unreal_path: Unreal Path of the asset, e.g. /Game/Assets/MyAsset
    :param with_ext: if True, build the path with extension (.uasset or .umap), set asterisk "*" otherwise.

    :return: the OS path of the asset
    :rtype: str
    """

    os_path = str(unreal_path).replace('/Game/', content_dir)

    if with_ext:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(unreal_path)
        asset_class_name = asset_data.asset_class_path.asset_name \
            if hasattr(asset_data, 'asset_class_path') \
            else asset_data.asset_class  # support older version of UE python API

        if not asset_class_name.is_none():  # AssetData not found - asset not in the project / on disk
            os_path += '.umap' if asset_class_name == 'World' else '.uasset'
        else:
            os_path += '.uasset'
    else:
        os_path += '.*'

    return os_path


def get_engine_version_number() -> str:
    """
    Get the engine version number in format `major.minor.patch`, for example `5.3.2`

    :return: Unreal Engine version number as string
    :rtype: str
    """

    return re.findall(r'\d\.\d\.\d', unreal.SystemLibrary.get_engine_version())[0]

def log(message: str, level: int = logging.INFO):
    """
    Log a message to the Unreal log with the specified level.

    :param message: The message to log.
    :param level: The logging library log level.
    :return: Formatted log message.
    :rtype: str
    """

    if level == logging.DEBUG:
        unreal.log(f"Debug: {message}")
    elif level == logging.INFO:
        unreal.log(message)
    elif level == logging.WARNING:
        unreal.log_warning(message)
    elif level == logging.ERROR:
        unreal.log_error(message)
    elif level == logging.CRITICAL:
        unreal.log_error(f"Critical: {message}")
    else:
        raise ValueError(f"Unreal Utils: Unsupported log level: {level}")