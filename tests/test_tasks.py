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


class TestTaskFunctions(unittest.TestCase):
    """Test task functions."""

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
        self.list_title = 'test list'
        tasklists.create_tasklist(self.creds, self.list_title, False)

        self.task_title = 'test task'

        # Capture stdout to check correctness of output
        self.output = StringIO()
        sys.stdout = self.output

    def test_create_task(self):
        """Create task with specified title."""
        tasks.create_task(self.creds, self.list_title, self.task_title, None,
                          -1, False)

        tasklists.print_tasklist(self.creds, self.list_title, -1, False)

        self.assertIn(f'0. {self.task_title}',
                      self.output.getvalue().splitlines())

    def test_delete_task(self):
        """Delete task with specified title."""
        tasks.create_task(self.creds, self.list_title, self.task_title, None,
                          -1, False)

        tasks.delete_task(self.creds, self.list_title, -1, -1, False)

        tasklists.print_tasklist(self.creds, self.list_title, -1, False)

        self.assertNotIn(f'0. {self.task_title}',
                         self.output.getvalue().splitlines())

    def test_update_task(self):
        """Update title of task."""
        tasks.create_task(self.creds, self.list_title, self.task_title, None,
                          -1, False)

        new_title = 'new test task'
        tasks.update_task(self.creds, self.list_title, new_title, -1, -1,
                          False)

        tasklists.print_tasklist(self.creds, self.list_title, -1, False)

        self.assertIn(f'0. {new_title}',
                      self.output.getvalue().splitlines())

    def test_create_note(self):
        """Create task note."""
        tasks.create_task(self.creds, self.list_title, self.task_title, None,
                          -1, False)

        note = 'test note'
        tasks.create_note(self.creds, self.list_title, note, -1, -1, False)

        tasklists.print_tasklist(self.creds, self.list_title, -1, False)

        self.assertIn(f'  - Note: {note}',
                      self.output.getvalue().splitlines())

    def test_move_task(self):
        """Move task to new position."""
        tasks.create_task(self.creds, self.list_title, self.task_title, None,
                          -1, False)

        new_task = 'new test task'
        tasks.create_task(self.creds, self.list_title, new_task, None, -1,
                          False)

        tasks.move_task(self.creds, self.list_title, 1, 0, -1, False)

        tasklists.print_tasklist(self.creds, self.list_title, -1, False)

        self.assertEqual(f'1. {new_task}',
                         self.output.getvalue().splitlines()[2])

    def tearDown(self):
        """Cleanup test environment."""
        self.output.truncate(0)

        tasklists.print_all_tasklists(self.creds, 100, False)
        num_lists = self.output.getvalue().splitlines().count(
                f'- {self.list_title}')

        self.output.close()

        for _ in range(num_lists):
            tasklists.delete_tasklist(self.creds, self.list_title, 0, False)


if __name__ == '__main__':
    unittest.main()
