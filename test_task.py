import contextlib
import csv
import io
import unittest

import mock

from . import task


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        data = []
        with open("data.csv") as infile:
            read_object = csv.reader(infile)
            next(read_object)
            for row in read_object:
                data.append(row)
        self.data = data
        with open("fixture_output.txt") as infile:
            self.fixture = infile.read()

    def test_integration_flow(self):
        task.import_data = mock.MagicMock(return_value=self.data)

        f = io.StringIO()

        with contextlib.redirect_stdout(f):
            task.main()

        f.seek(0)
        self.assertEqual(f.read(), self.fixture)

    def test_error_class_creation(self):
        task.import_data = mock.MagicMock(return_value=self.data[0][:-2])
        f = io.StringIO()

        with contextlib.redirect_stderr(f):
            task.main()

        f.seek(0)
        error_message = ("Class initialization failed with exception not enough"
                         " values to unpack (expected at least 4, got 3)\n")
        self.assertEqual(f.read(), error_message)
