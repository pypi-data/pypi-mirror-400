#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Optional

from ciocore import data as coredata
from ciocore.hardware_set import HardwareSet
from ciocore.package_tree import PackageTree

coredata.init('unrealengine', platforms=["windows"])


class ConductorData:
    """
    Helper class for getting useful data from the Conductor API
    """

    @staticmethod
    def get_ciocore_data() -> dict:
        """
        Get all the data from the Conductor API. Filter to only 
        receive singleton GPU instance types. 

        :return: projects, instance types and software package data
        :rtype: dict
        """
        return coredata.data(force=True, instances_filter="gpu.gpu_count=eq:1:int")

    @staticmethod
    def get_projects() -> list[str]:
        """
        Get projects from the Conductor API

        :return: list of the project names
        :rtype: list[str]
        """

        return coredata.data()['projects']

    @staticmethod
    def get_software() -> PackageTree:
        """
        Get software package data from the Conductor API

        :return: software package data object
        :rtype: :class:`ciocore.package_tree.PackageTree`
        """

        return coredata.data().get('software')

    @staticmethod
    def get_supported_software_packages() -> list[dict]:
        """
        Get software package data from the Conductor API
        that supported current product with which conductor was initialized

        :return: list of deserialized software package data objects
        :rtype: list[dict]
        """

        packages = []
        package_tree: PackageTree = ConductorData.get_software()
        if package_tree:
            for host_name in package_tree.supported_host_names():
                package: dict = package_tree.find_by_name(host_name)
                if package:
                    packages.append(package)
        return packages

    @staticmethod
    def get_instance_types() -> list[dict]:
        """
        Get list of instance types that are suitable for running UE render: GPU instances on Windows

        :return: list of instance type descriptors
        :rtype: list[dict]
        """

        result = []
        hardware: HardwareSet = coredata.data().get('instance_types')
        for category in hardware.categories:
            for entry in category['content']:
                if not (entry['operating_system'] == 'windows' and entry.get('gpu')):
                    continue
                result.append(entry)
        return result

    @staticmethod
    def get_instance_type_by_description(instance_type_description: str) -> Optional[dict]:
        """
        Get instance type by the given description

        :param instance_type_description: instance type description, for example 64 core 240GB Mem
               (4 T4 Tensor GPUs 16GB Mem)
        :return: instance type descriptor or None
        :rtype: Optional[dict]
        """

        return next(
            (
                instance_type for instance_type
                in ConductorData.get_instance_types()
                if instance_type['description'] == instance_type_description
            ),
            None
        )
