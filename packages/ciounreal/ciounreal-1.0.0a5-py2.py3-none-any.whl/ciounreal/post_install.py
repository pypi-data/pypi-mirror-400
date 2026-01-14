#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import json
import os
import re
import sys
import shlex
import subprocess
import errno
import shutil
import zipfile
from pathlib import Path


def fslash(path):
    return path.replace("\\", "/")


PACKAGE_DIR = fslash(os.path.dirname(os.path.abspath(__file__)))  # ciounreal
CIO_DIR = os.path.dirname(PACKAGE_DIR)  # ~/Conductor/unreal
HOME = fslash(os.path.expanduser("~"))
PLUGIN_NAME = "Conductor"

BASE_PATH = os.getenv("UNREAL_BASE_PATH") or r"C:\Program Files\Epic Games"
UNREAL_LAUNCHER_DATA = os.path.join(
    os.getenv("ProgramData", r"C:\ProgramData"), "Epic", "UnrealEngineLauncher", "LauncherInstalled.dat"
)
UNREAL_VERSIONS = ["5.2", "5.3", "5.4", "5.5"]

INIT_SCRIPT_CONTENT = f"""
import sys
import os

CIO_DIR = "{CIO_DIR}"
os.environ['CIO_DIR'] = CIO_DIR

if CIO_DIR not in sys.path:
    sys.path.append(CIO_DIR)

"""


def main(project_path=None):
    ue_plugin_directories = []
    if project_path:
        if not os.path.exists(project_path):
            print(f"The provided project path does not exist: {project_path}")
            print("Plugin will not be installed.")
            return
        project_plugins = UnrealPlugin.get_unreal_project_plugins(project_path)
        project_plugins.install_conductor()
    else:
        install_ciounreal()

        engine_plugins_list = UnrealPlugin.get_unreal_engine_plugins()
        for engine_plugins in engine_plugins_list:
            engine_plugins.install_conductor()

    print("Completed Unreal tool setup!")


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise

def install_ciounreal():
    #  Loop through each UE Version and see if directory exists
    for ue_ver in UNREAL_VERSIONS:
        ue_dir = "UE_{}".format(ue_ver)
        ue_dir_path = os.path.join(BASE_PATH, ue_dir)

        # If the directory exists, pip install ciounreal with UE native python
        if os.path.isdir(ue_dir_path):
            ue_python_path = os.path.join(ue_dir_path, "Engine", "Binaries", "ThirdParty", "Python3", "Win64", "python.exe")
            try:
                cmd = "\"{}\" -m pip install ciounreal --target \"{}\" --verbose".format(ue_python_path, CIO_DIR) 
                subprocess.run(shlex.split(cmd))
                print("Successful ciounreal install to {}!".format(ue_dir))
            except Exception:
                print("Failed ciounreal install to {}. Continuing...".format(ue_dir))
                continue

class UnrealPlugin:
    def __init__(self, version: str, plugins_path: str = None):
        self.version = version
        self.plugins_path = plugins_path

    def install_conductor(self):
        zipped = os.path.join(CIO_DIR, "Plugins", f"Conductor{self.version}.zip")
        zipped = zipped.replace("\\", "/")
        target = os.path.join(self.plugins_path, "Conductor")

        print(f"Installing Conductor Plugin {self.version} to {target}")
        # Create or empty a folder for the plugin.
        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
        except Exception as e:
            print(f"Failed to remove existing {target}. Reason: {e}")
            return

        ensure_directory(target)
        with zipfile.ZipFile(zipped, "r") as zip_ref:
            zip_ref.extractall(target)

        with open(os.path.join(target, "Content", "Python", "init_unreal.py"), "r+") as f:
            content = f.read()
            f.seek(0, 0)
            content = INIT_SCRIPT_CONTENT + content
            f.write(content)

        print(f"Plugin installation completed! Conductor Plugin {self.version} installed to {target}")

    @staticmethod
    def get_base_path_engine_paths():
        if not os.path.exists(BASE_PATH):
            print("The Unreal Engine search base path does not exist.")
            return []
        engine_paths = [
            os.path.join(BASE_PATH, d) for d in os.listdir(BASE_PATH)
            if os.path.isdir(os.path.join(BASE_PATH, d)) and d.startswith("UE_5")
        ]
        return engine_paths

    @staticmethod
    def get_launcher_engine_paths():
        if not os.path.exists(UNREAL_LAUNCHER_DATA):
            print("Unreal Launcher data does not exist")
            return []

        with open(UNREAL_LAUNCHER_DATA, 'r') as f:
            ue_paths = []
            ue_launcher_installed = json.load(f)
            for app in ue_launcher_installed["InstallationList"]:
                if app["AppName"].startswith("UE_5") and app["NamespaceId"] == "ue":
                    ue_paths.append(app["InstallLocation"])
            return ue_paths

    @staticmethod
    def get_unreal_engine_plugins():
        launcher_engine_paths = [
            path.replace('/', '\\') for path in UnrealPlugin.get_launcher_engine_paths()
        ]
        base_engine_paths = [
            path.replace('/', '\\') for path in UnrealPlugin.get_base_path_engine_paths()
        ]
        all_engine_paths = list(set(launcher_engine_paths + base_engine_paths))

        unreal_plugins = [
            UnrealPlugin(
                os.path.basename(engine_path),
                os.path.join(engine_path, "Engine", "Plugins")
            )
            for engine_path in all_engine_paths
        ]
        print(f"Found {len(unreal_plugins)} Unreal Engine plugin directories")

        return unreal_plugins

    @staticmethod
    def get_unreal_project_plugins(project_path: str):
        uproject_path = next(
            (uproject_path for uproject_path in Path(project_path).glob('*.uproject')),
            None
        )
        if uproject_path:
            with open(uproject_path, "r") as f:
                uproject = json.load(f)
                engine_version = uproject.get("EngineAssociation")
                return UnrealPlugin("UE_" + engine_version, os.path.join(project_path, "Plugins"))
        return None


if __name__ == "__main__":
    # give a path to a project to install into. If not provided, it will install into the default Unreal Engine plugins directory.

    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(project_path=project_path)
