#!/usr/bin/env python3

import unittest
import os
import sys

from .. import tasklists
from .. import tasks
from .. import calcurse

from io import StringIO
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

DATA_DIR = os.path.join(os.getcwd(), 'caldurse')


class TestSyncFunctions(unittest.TestCase):
    """Test calcurse sync functions."""

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

        # Create calcurse tasks file and tasks
        todo_file = os.path.join(DATA_DIR, 'todo')
        with open(todo_file, 'w') as f:
            f.write('[0] test task 1\n[0] test task 2\n[0] test task 3\n')

        # Capture stdout to check correctness of output
        self.output = StringIO()
        sys.stdout = self.output

    def test_get_calcurse_tasks(self):
        """Get tasks from calcurse."""
        calcurse_tasks = calcurse.get_calcurse_tasks(DATA_DIR)
        calcurse_task = {'title': 'test task 1'}
        self.assertIn(calcurse_task, calcurse_tasks)

    def test_add_calcurse_tasks(self):
        """Add tasks to calcurse."""
        task_name = 'test task 4'
        new_task = [{'title': task_name}]
        calcurse.add_calcurse_tasks(new_task, DATA_DIR)

        calcurse_tasks = calcurse.get_calcurse_tasks(DATA_DIR)
        self.assertIn(new_task[0], calcurse_tasks)

    def tearDown(self):
        """Cleanup test environment"""
        self.output.truncate(0)

        tasklists.print_all_tasklists(self.creds, 100, False)
        num_lists = self.output.getvalue().splitlines().count(
                f'- {self.list_title}')

        self.output.close()

        for _ in range(num_lists):
            tasklists.delete_tasklist(self.creds, self.list_title, 0, False)
