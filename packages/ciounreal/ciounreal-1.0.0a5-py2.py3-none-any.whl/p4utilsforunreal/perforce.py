#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
from typing import Optional
from P4 import P4, P4Exception

from p4utilsforunreal.log import get_logger


logger = get_logger()


class PerforceConnection:
    """
    Wrapper around the P4 object of p4python package

    P4 connection can be created by passing port, user, password and charset to the constructor
    or setting appropriate P4PORT, P4USER and P4PASSWD environment variables.

    .. note::
       Current connection properties will be used by default
    """

    def __init__(self, port: str = None, user: str = None, password: str = None, charset="none", required_connection=False):
        p4 = P4()
        p4.charset = charset
        self.p4_connection = False

        p4_port = port or os.getenv('P4PORT')
        if p4_port:
            p4.port = p4_port

        p4_user = user or os.getenv('P4USER')
        if p4_user:
            p4.user = p4_user

        p4_password = password or os.getenv('P4PASSWD')

        if required_connection:
            self._required_connection(p4, p4_port, p4_user, p4_password)
        else:
            self._connection(p4, p4_password)
        
    def _required_connection(self, p4, p4_port, p4_user, p4_password):
        """
        Attempt to connect to Perforce. Raise any exceptions to block
        Perforce-enabled MRQ submissions.

        :param p4: P4 connection object
        :param p4_port: Perforce port
        :param p4_user: Perforce username
        :param p4_password: Perforce password
        """

        if not all([p4_port, p4_user, p4_password]):
            p4_fields = {"Perforce Port": p4_port, "Perforce Username": p4_user, "Perforce Password": p4_password}
            p4_missing_fields = ", ".join([k for k, v in p4_fields.items() if v is None])
            raise Exception(f'Could not connect to Perforce server. Missing field(s) under Conductor Settings: {p4_missing_fields}.')

        try:
            p4.password = p4_password
            p4.connect()

            p4.input = 'y'
            p4.run('trust', ['-y'])
            p4.run_login()
        except Exception as e:
            p4e = str(e).lower()
            if "not connected" in p4e or "connect to server failed" in p4e:
                raise Exception(f'Could not connect to Perforce server. Invalid port ({p4.port}).')
            elif "password invalid" in p4e:
                raise Exception(f'Could not connect to Perforce server. Invalid username ({p4.user}) or password ({p4.password}).')
            raise Exception(e)

        self.p4 = p4
        self.p4_connection = True

    def _connection(self, p4, p4_password):
        """
        Attempt to connect to Perforce. Quietly log if any issues
        occur to not interefere with standard MRQ submissions.

        :param p4: P4 connection object
        :param p4_password: Perforce password
        """

        try:
            p4.connect()
        except P4Exception as e:
            logger.info(f'Could not connect Perforce server {p4.port} as user {p4.user}\n{str(e)}')

        p4.input = 'y'
        p4.run('trust', ['-y'])

        if p4_password:
            p4.password = p4_password
            p4.run_login()
            self.p4_connection = True

        self.p4 = p4

class PerforceClient:
    """
    Wrapper around the P4 workspace (client)
    """

    def __init__(self, connection: PerforceConnection, name: str, specification: dict = None):
        self.p4 = connection.p4
        self.name = name
        self.spec = self.p4.fetch_client(name)
        if specification:
            self.spec.update(specification)

    def save(self):
        """
        Save the perforce client (workspace) on the P4 server
        """

        self.p4.save_client(self.spec)

    def sync(self, filepath: str = None):
        """
        Execute `p4 sync` on the given file path. If no path given, will sync the whole workspace

        :param filepath: File path to sync
        """

        self.p4.client = self.name
        if filepath:
            self.p4.run('sync', filepath)
        else:
            self.p4.run('sync')


def get_perforce_workspace_specification(port: str = None, user: str = None, client: str = None) -> Optional[dict]:
    """
    Get perforce workspace specification using provided port, user and client.
    If some of the parameters are missing, defaults will be used

    :param port: P4 server address
    :param user: P4 user name
    :param client: P4 client (workspace) name

    :return: P4 workspace specification dictionary if successful, None otherwise
    :rtype: Optional[dict]
    """

    p4 = PerforceConnection(port=port, user=user).p4
    if client:
        p4.client = client

    try:
        workspace_specification = p4.fetch_client(p4.client)
        return workspace_specification
    except P4Exception as e:
        logger.info(str(e))


if __name__ == '__main__':
    p4 = PerforceConnection().p4
    print(p4.user)
