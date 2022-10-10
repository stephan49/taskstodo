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

        # Capture stdout text to allow checking correctness of output
        self.output = StringIO()
        sys.stdout = self.output

    def test_create_tasklist(self):
        """Create task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        tasks = self.output.getvalue().splitlines()
        tasks = [task.removeprefix('- ') for task in tasks]

        self.assertIn(self.title, tasks)

    def test_delete_tasklist(self):
        """Delete task list with specified title."""
        tasklists.delete_tasklist(self.creds, self.title, 0, False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        tasks = self.output.getvalue().splitlines()
        tasks = [task.removeprefix('- ') for task in tasks]

        self.assertNotIn(self.title, tasks)


if __name__ == '__main__':
    unittest.main()
