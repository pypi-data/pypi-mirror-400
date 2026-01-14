#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import glob
import unreal
import unittest


from ciounreal.common import unreal_utils


class TestUnrealUtils(unittest.TestCase):

    @classmethod
    def create_test_asset(cls) -> str:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", unreal.Actor)

        asset_name = 'TestAsset'
        asset_package_path = '/Game'
        asset_path = f'{asset_package_path}/{asset_name}'

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset_tools.create_asset(
            asset_name=asset_name,
            package_path=asset_package_path,
            asset_class=None,
            factory=factory
        )
        unreal.EditorAssetLibrary.save_asset(asset_path)

        return asset_path

    def test_get_project_file_path(self):
        project_file_path = unreal_utils.get_project_file_path()
        assert os.path.exists(project_file_path)

    def test_get_project_directory(self):
        project_directory = unreal_utils.get_project_directory()
        assert os.path.exists(project_directory)

    def test_soft_object_path_to_str(self):
        original_path = '/Game/Assets/TestAsset'
        soft_object_path = unreal.SoftObjectPath(original_path)
        assert original_path == unreal_utils.soft_obj_path_to_str(soft_object_path)

    def test_os_path_from_unreal_path(self):
        asset_path = self.create_test_asset()

        os_path_with_ext = unreal_utils.os_path_from_unreal_path(asset_path, with_ext=True)
        assert os.path.exists(os_path_with_ext)

        os_path_without_ext = unreal_utils.os_path_from_unreal_path(asset_path, with_ext=False)
        assert len(glob.glob(os_path_without_ext)) > 0

        unreal.EditorAssetLibrary.delete_asset(asset_path)

    def test_get_engine_version_number(self):
        engine_version = unreal.SystemLibrary.get_engine_version()
        engine_version_number = unreal_utils.get_engine_version_number()

        assert engine_version.startswith(engine_version_number)

        major_variants = [4, 5]
        minor_variants = [v for v in range(0, 10)]
        patch_variants = [v for v in range(0, 10)]

        major, minor, patch = engine_version_number.split('.')
        assert int(major) in major_variants
        assert int(minor) in minor_variants
        assert int(patch) in patch_variants







