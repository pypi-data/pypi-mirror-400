#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import argparse

if os.getenv('CIO_DIR'):
    if os.environ['CIO_DIR'] not in sys.path:
        sys.path.append(os.environ['CIO_DIR'])

from p4utilsforunreal import app


def parse_args():
    argparser = argparse.ArgumentParser('p4utils-for-unreal')
    argparser.add_argument('command', choices=['create_workspace', 'delete_workspace'])
    argparser.add_argument('-UnrealProjectRelativePath', required=False, help='Relative path to the workspace root')
    argparser.add_argument('-PerforceWorkspaceSpecificationTemplate', required=False, help='P4 spec JSON file path')
    argparser.add_argument('-PerforceServer', required=False, help='P4 Server address')
    argparser.add_argument('-OverriddenWorkspaceRoot', required=False, help='New workspace root to create (Optional)')

    return argparser.parse_args()


def main():

    args = parse_args()

    if args.command == 'create_workspace':
        app.create_workspace(
            perforce_specification_template_path=args.PerforceWorkspaceSpecificationTemplate,
            unreal_project_relative_path=args.UnrealProjectRelativePath,
            perforce_server=args.PerforceServer,
            overridden_workspace_root=args.OverriddenWorkspaceRoot
        )

    if args.command == 'delete_workspace':
        app.delete_workspace(
            unreal_project_relative_path=args.UnrealProjectRelativePath
        )


if __name__ == '__main__':
    main()
