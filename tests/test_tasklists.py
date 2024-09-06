#!/usr/bin/env python3

import unittest
import os
import sys

from taskstodo import tasklists
from taskstodo import tasks

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

    def test_get_nonempty_tasklist(self):
        """Get nonempty task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        task_title = 'test task'
        tasks.create_task(self.creds, self.title, task_title, None, None, False)

        tasklists.print_tasklist(self.creds, self.title, None, False)
        self.assertIn(f'1. {task_title}', self.output.getvalue().splitlines())

    def test_get_empty_tasklist(self):
        """Get empty task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.print_tasklist(self.creds, self.title, None, False)
        self.assertEqual(1, len(self.output.getvalue().splitlines()))

    def test_get_duplicate_titled_tasklist(self):
        """Get task list with duplicate title."""
        tasklists.create_tasklist(self.creds, self.title, False)
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.print_tasklist(self.creds, self.title, None, False)
        self.assertIn('Multiple task lists with duplicate titles found:',
                      self.output.getvalue().splitlines())

    def test_delete_tasklist(self):
        """Delete task list with specified title."""
        tasklists.create_tasklist(self.creds, self.title, False)

        tasklists.delete_tasklist(self.creds, self.title, None, False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        lists = self.output.getvalue().splitlines()
        lists = [lst.removeprefix('- ') for lst in lists]

        self.assertNotIn(self.title, lists)

    def test_update_tasklist(self):
        """Update title of task list."""
        tasklists.create_tasklist(self.creds, self.title, False)

        new_title = 'new test list'
        tasklists.update_tasklist(self.creds, self.title, new_title, None,
                                  False)

        tasklists.print_all_tasklists(self.creds, 100, False)

        lists = self.output.getvalue().splitlines()
        lists = [lst.removeprefix('- ') for lst in lists]

        self.assertIn(new_title, lists)

        tasklists.delete_tasklist(self.creds, new_title, 0, False)

    def tearDown(self):
        """Cleanup test environment."""
        self.output.truncate(0)

        tasklists.print_all_tasklists(self.creds, 100, False)
        num_lists = self.output.getvalue().splitlines().count(
                f'- {self.title}')

        self.output.close()

        for _ in range(num_lists):
            tasklists.delete_tasklist(self.creds, self.title, 0, False)


if __name__ == '__main__':
    unittest.main()
