#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import shlex
import shutil
import subprocess
import time

import setuptools
from setuptools.command.build_py import build_py

NICE_NAME = "Conductor for Unreal"
NAME = "ciounreal"
DESCRIPTION = "Unreal plugin for Conductor Cloud Rendering Platform."
URL = "https://github.com/ConductorTechnologies/ciounreal"
EMAIL = "info@conductortech.com"
AUTHOR = "Conductor"
REQUIRED = [
    "ciocore>=9.0.0,<10.0.0",
    "cioseq>=0.1.14,<1.0.0",
    "p4python==2024.1.2625398"
]
HERE = os.path.abspath(os.path.dirname(__file__))
DEV_VERSION = "dev.999"
UNREAL_BASE_PATH = os.getenv("UNREAL_BASE_PATH") or r"C:\Program Files\Epic Games"


with open(os.path.join(HERE, 'VERSION')) as version_file:
    VERSION = version_file.read().strip()


with open(os.path.join(HERE, 'README.md')) as readme:
    long_description = readme.read().strip()

long_description += "\n\n## Changelog\n\n"
with open(os.path.join(HERE, 'CHANGELOG.md')) as changelog:
    long_description += changelog.read().strip()


class UnrealPlugin:
    def __init__(self, version: str, runuat_path: str = None):
        self.version = version
        self.runuat_path = runuat_path

    def build(self, target: str):
        abs_target = os.path.abspath(target)
        source_folder = os.path.join(os.path.abspath(target), "Plugins", "Conductor")
        source_folder = source_folder.replace("\\", "/")

        target_folder = os.path.join(abs_target, "UAT", "Plugins", "Conductor")
        target_folder = target_folder.replace("\\", "/")

        build_command = f'"{self.runuat_path}" BuildPlugin ' \
                        f'-Plugin={source_folder}/Conductor.uplugin ' \
                        f'-Package={target_folder} ' \
                        f'-Rocket'
        process = subprocess.run(shlex.split(build_command))

        if process.returncode == 0:
            self.version_to_uplugin(f'{target_folder}/Conductor.uplugin')

            destination_zip = os.path.join(target, "Plugins", f"Conductor{self.version}")
            destination_dir = os.path.dirname(destination_zip)
            os.makedirs(destination_dir, exist_ok=True)
            shutil.make_archive(base_name=destination_zip, format='zip', root_dir=target_folder)
        else:
            print(f"Build failed with exitcode={process.returncode}. Check logs above for details")

        try:
            shutil.rmtree(os.path.join(target, "UAT"))
        except:
            pass

    @staticmethod
    def get_unreal_engine_plugins():
        if not os.path.exists(UNREAL_BASE_PATH):
            print("Search path for Unreal Engine not found. Skipping Unreal Engine plugin build.")
            return []

        engine_versions = [
            d for d in os.listdir(UNREAL_BASE_PATH)
            if os.path.isdir(os.path.join(UNREAL_BASE_PATH, d)) and d.startswith("UE_5")
        ]
        unreal_plugins = [
            UnrealPlugin(
                engine_version,
                os.path.join(UNREAL_BASE_PATH, engine_version, "Engine", "Build", "BatchFiles", "RunUAT.bat")
            )
            for engine_version in engine_versions
        ]
        return unreal_plugins

    @classmethod
    def version_to_uplugin(cls, uplugin_file: str):
        merge_data = {
            "IsBetaVersion": "b" in VERSION.lower(),
            "VersionName": VERSION,
            "FriendlyName" : NICE_NAME,
            "Version": 1,
            "Description": "Submit jobs to to the Conductor cloud rendering service.",
            "Category": "Rendering",
            "CreatedBy": AUTHOR,
            "CreatedByURL": "https://www.conductortech.com",
            "DocsURL": "https://docs.conductortech.com",
            "SupportURL": "https://support.conductortech.com/hc/en-us/requests/new",
            "EnabledByDefault": True
        }
        # uplugin_file = os.path.join(target_dir, "Plugins",  "Conductor", "Conductor.uplugin")
        with open(uplugin_file, "r") as f:
            uplugin = json.load(f)

        uplugin.update(merge_data)
        with open(uplugin_file, "w") as f:
            json.dump(uplugin, f, indent=4)

        print(f"Updated {uplugin_file} with version {VERSION}")
        print(f"Result uplugin: {uplugin}")


class BuildCommand(build_py):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        build_py.run(self)
        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, NAME)
            self.write_version_info(target_dir)

            # self.version_to_uplugin(self.build_lib)

            unreal_plugins = UnrealPlugin.get_unreal_engine_plugins()
            for unreal_plugin in unreal_plugins:
                unreal_plugin.build(self.build_lib)

            self.remove_unreal_plugin_source(self.build_lib)

    @classmethod
    def remove_unreal_plugin_source(cls, target_dir):
        abs_target = os.path.abspath(target_dir)
        source_folder = os.path.join(abs_target, "Plugins", "Conductor")
        shutil.rmtree(source_folder)

    @classmethod
    def write_version_info(cls, target_dir: str):
        with open(os.path.join(target_dir, "VERSION"), "w") as f:
            f.write(VERSION)


def gather_package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = gather_package_files("Plugins")
extra_files.extend(gather_package_files("p4utilsforunreal"))
extra_files.extend(
    [
        '..\\VERSION',
        '..\\*.md'
    ]
)


setuptools.setup(
    author=AUTHOR,
    author_email=EMAIL,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
    ],
    cmdclass={"build_py": BuildCommand},
    description=DESCRIPTION,
    install_requires=REQUIRED,
    long_description=long_description,
    long_description_content_type="text/markdown",
    name=NAME,
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    options={"bdist_wheel": {"universal": True}},
    include_package_data=True,
    url=URL,
    version=VERSION,
    zip_safe=False,
    package_data={NAME: extra_files}
)
