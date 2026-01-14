#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import random
import unittest


from ciounreal.common import conductor_data


class TestConductorData(unittest.TestCase):

    def test_get_ciocore_data(self):
        ciocore_data = conductor_data.ConductorData.get_ciocore_data()
        assert isinstance(ciocore_data, dict)

    def test_get_projects(self):
        projects = conductor_data.ConductorData.get_projects()
        assert isinstance(projects, list)
        assert len(projects) > 0

    def test_get_software(self):
        software = conductor_data.ConductorData.get_software()
        assert isinstance(software, conductor_data.PackageTree)

    def test_get_supported_software_packages(self):
        supported_software_packages = conductor_data.ConductorData.get_supported_software_packages()
        for package in supported_software_packages:
            assert package['platform'] == 'windows'
            assert package['product'] == 'unrealengine'

    def test_get_instance_types(self):
        isinstance_types = conductor_data.ConductorData.get_instance_types()
        for instance_type in isinstance_types:
            assert instance_type.get('gpu') is not None
            assert instance_type['operating_system'] == 'windows'

    def test_get_instance_type_by_description(self):
        instance_types = conductor_data.ConductorData.get_instance_types()
        random_index = random.randint(0, len(instance_types) - 1)
        instance_type_description = instance_types[random_index]['description']

        instance_type = conductor_data.ConductorData.get_instance_type_by_description(instance_type_description)
        assert instance_type in instance_types
