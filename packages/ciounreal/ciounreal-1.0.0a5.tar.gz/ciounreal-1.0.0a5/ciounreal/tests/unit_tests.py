#  Copyright 2024 CoreWeave
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Must be run in Unreal Engine Editor: py ciounreal\tests\unit_tests.py

import os
import sys
import unreal
import unittest

ciodir = os.path.dirname(os.path.dirname(__file__))

if ciodir not in sys.path:
    sys.path.append(ciodir)

from ciounreal.common import unreal_utils
from ciounreal.tests.cases import TestConductorData, TestUnrealUtils, TestUnrealDependencyCollector


if __name__ == '__main__':

    test_results = []

    for test_case in [
        TestConductorData,
        TestUnrealUtils,
        TestUnrealDependencyCollector
    ]:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        result = unittest.TextTestRunner(stream=sys.stdout, buffer=True).run(suite)
        test_results.append((test_case.__name__, result))

    for suite, result in test_results:
        unreal_utils.log(f'Test Case {suite} result:\n'
                   f'Total run: {result.testsRun}\n'
                   f'Successful: {result.wasSuccessful()}\n'
                   f'Errors: {len(result.errors)}\n'
                   f'Failures: {result.failures}\n\n')
