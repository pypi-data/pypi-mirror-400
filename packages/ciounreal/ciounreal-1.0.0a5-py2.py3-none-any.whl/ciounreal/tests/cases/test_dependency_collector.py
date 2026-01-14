#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.


import unreal
import unittest
from pathlib import Path

from ciounreal.common import dependency_collector

UNREAL_PROJECT_DIRECTORY = str(
    Path(
        unreal.Paths.convert_relative_path_to_full(unreal.Paths.get_project_file_path())
    ).parent
).replace('\\', '/')

# Set here your asset and dependencies
UNREAL_ASSET_PATH = '/Game/Assets/Set/Desert/Lookdev'
UNREAL_ASSET_DEPENDENCIES_PATHS = [
    '/Game/Assets/Sel/Cube/Cube',
    '/Game/Assets/Sel/Cube/NewMaterial'
]


class TestUnrealDependencyCollector(unittest.TestCase):

    def test_dependency_filter_in_game_folder(self):
        for case in [
            ('/Game/Test/MyAsset', True),
            ('/Engine/Basic/Cube', False),
            ('Game/Test/MyAsset', False),
            ('Engine/Game/MyAsset', True)
        ]:
            self.assertEqual(
                dependency_collector.DependencyFilters.dependency_in_game_folder(case[0]),
                case[1]
            )

    def test_search_options_as_dict_representation(self):
        expected_search_options = dict(
            include_hard_package_references=False,
            include_soft_package_references=False,
            include_hard_management_references=False,
            include_soft_management_references=False,
            include_searchable_names=False,
        )

        self.assertEqual(
            dependency_collector.DependencyOptions(
                False, False, False, False, False
            ).as_dict(),
            expected_search_options
        )

    def test_dependency_collector(self):
        collector = dependency_collector.DependencyCollector()

        dependencies = collector.collect(
            UNREAL_ASSET_PATH, filter_method=dependency_collector.DependencyFilters.dependency_in_game_folder
        )

        for d in UNREAL_ASSET_DEPENDENCIES_PATHS:
            assert d in dependencies

        assert len(dependencies) >= len(UNREAL_ASSET_DEPENDENCIES_PATHS)
