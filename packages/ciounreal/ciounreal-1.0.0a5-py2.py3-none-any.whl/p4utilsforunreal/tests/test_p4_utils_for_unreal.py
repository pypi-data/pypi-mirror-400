#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import json
import socket
import unittest
from unittest.mock import patch, call, MagicMock

import pytest

from p4utilsforunreal.app import (
    get_workspace_specification_template_from_file,
    create_perforce_workspace_from_template,
    initial_workspace_sync,
    configure_project_source_control_settings
)
from p4utilsforunreal import perforce


def mocked_p4_sync(filepath: str = None):
    print(f'Mock sync file: {filepath}')


class TestP4UtilsForUnreal(unittest.TestCase):

    def test_get_perforce_specification_template_from_file(self):
        valid_content = dict(key1='value1', key2='value2')
        template_path = f'{os.path.dirname(__file__)}/specification_template.json'

        # Check valid template
        with open(template_path, 'w') as f:
            json.dump(valid_content, f)
        assert get_workspace_specification_template_from_file(template_path) == valid_content
        os.remove(template_path)

        # Check not existed template
        self.assertRaises(
            FileNotFoundError,
            get_workspace_specification_template_from_file,
            'not existed template.json'
        )

        # Check empty template
        open(template_path, 'w').close()
        self.assertRaises(
            json.decoder.JSONDecodeError,
            get_workspace_specification_template_from_file,
            template_path
        )
        os.remove(template_path)

    @patch('p4utilsforunreal.perforce.PerforceClient.save', new_callable=MagicMock)
    def test_create_perforce_workspace_from_template(self):
        spec = perforce.get_perforce_workspace_specification()
        spec_template = {
            'Client': '{workspace_name}',
            'Root': spec['Root'],
            'Stream': spec['Stream'],
            'View': [v.replace(spec['Client'], '{workspace_name}') for v in spec['View']]
        }

        project_name = 'CoreweaveConductorTest'

        client = create_perforce_workspace_from_template(
            specification_template=spec_template,
            project_name=project_name,
            perforce_server=perforce.PerforceConnection().p4.port
        )

        workspace_name = f'{os.getlogin()}_{socket.gethostname()}_{project_name}_conductor'

        assert client.spec['Client'] == workspace_name
        assert client.name == workspace_name
        assert client.spec['Stream'] == spec['Stream']
        assert client.spec['Root'] == spec['Root']
        for view in client.spec['View']:
            assert workspace_name in view

    @patch('p4utilsforunreal.perforce.PerforceClient.save', new_callable=MagicMock)
    @patch('p4utilsforunreal.perforce.PerforceClient.sync', side_effect=mocked_p4_sync)
    def test_initial_workspace_sync(self, mock_workspace_sync, mock_workspace_save):
        spec = perforce.get_perforce_workspace_specification()
        spec_template = {
            'Client': '{workspace_name}',
            'Root': spec['Root'],
            'Stream': spec['Stream'],
            'View': [v.replace(spec['Client'], '{workspace_name}') for v in spec['View']]
        }

        project_name = 'CoreweaveConductorTest'

        client = create_perforce_workspace_from_template(
            specification_template=spec_template,
            project_name=project_name,
            perforce_server=perforce.PerforceConnection().p4.port
        )

        initial_workspace_sync(client, 'ConductorTest/ConductorTest.uproject')
        mock_workspace_sync.assert_has_calls(
            [
                call(f'{client.spec["Root"]}/ConductorTest/ConductorTest.uproject'),
                call(f'{client.spec["Root"]}/ConductorTest/Binaries...'),
                call(f'{client.spec["Root"]}/ConductorTest/Config...'),
            ]
        )

        initial_workspace_sync(client, 'ConductorTest.uproject')
        mock_workspace_sync.assert_has_calls(
            [
                call(f'{client.spec["Root"]}/ConductorTest.uproject'),
                call(f'{client.spec["Root"]}/Binaries...'),
                call(f'{client.spec["Root"]}/Config...'),
            ]
        )
