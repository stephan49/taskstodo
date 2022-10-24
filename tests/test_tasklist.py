#!/usr/bin/env python3

import unittest
import os
import sys
import tasklists

from io import StringIO
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class TestTasklistFunctions(unittest.TestCase):
    """Test task list functions."""

    def authUser(self):
        """Setup credentials to access API."""

        SCOPES = ['https://www.googleapis.com/auth/tasks']

        self.creds = None
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json',
                                                               SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def setUp(self):
        """Setup test environment."""
        self.authUser()
        self.title = 'test list'

        # Capture stdout to check correctness of output
        self.output = StringIO()
        sys.stdout = self.output

    def test_create_tasklist(self):
        """Create task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        lists = self.output.getvalue().splitlines()
        lists = [lst.removeprefix('- ') for lst in lists]

        self.assertIn(self.title, lists)

    def test_delete_tasklist(self):
        """Delete task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.delete_tasklist(self.creds, self.title, -1, False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        lists = self.output.getvalue().splitlines()
        lists = [lst.removeprefix('- ') for lst in lists]

        self.assertNotIn(self.title, lists)


if __name__ == '__main__':
    unittest.main()
