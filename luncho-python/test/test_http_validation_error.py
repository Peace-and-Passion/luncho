"""
    Client library for Luncho API. 

    Use luncho.ts and luncho.py rather than LunchoAPI.ts and others.  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import sys
import unittest

import luncho-python
from luncho-python.model.validation_error import ValidationError
globals()['ValidationError'] = ValidationError
from luncho-python.model.http_validation_error import HTTPValidationError


class TestHTTPValidationError(unittest.TestCase):
    """HTTPValidationError unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testHTTPValidationError(self):
        """Test HTTPValidationError"""
        # FIXME: construct object with mandatory attributes with example values
        # model = HTTPValidationError()  # noqa: E501
        pass


if __name__ == '__main__':
    unittest.main()
