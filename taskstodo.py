#!/usr/bin/env python3

import sys
import os.path
import argparse
import tasklists

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/tasks']

# Parse command line arguments
parser = argparse.ArgumentParser(description="Manage Google Tasks")
parser.add_argument('-a', '--all-task-lists', metavar='number', nargs='?',
                    const=10, type=int,
                    help='list all task lists (default: %(const)s)')
parser.add_argument('-l', '--task-list', metavar='ID', nargs=1, type=str,
                    help='list specificied task list')
parser.add_argument('-c', '--create-task-list', metavar='name', nargs=1,
                    type=str, help='create task list with specified name')
parser.add_argument('-d', '--delete-task-list', metavar='ID', nargs=1,
                    type=str, help='delete specified task list')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='show verbose messages')
args = parser.parse_args()


def auth_user():
    """
    Authenticate user with credentials.
    Return valid credentials for use with services.
    """

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials available, let user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def main():
    creds = auth_user()

    if args.all_task_lists:
        tasklists.get_all_tasklists(creds, args.all_task_lists, args.verbose)
    if args.task_list:
        tasklists.get_tasklist(creds, args.task_list[0], args.verbose)
    if args.create_task_list:
        tasklists.create_tasklist(creds, args.create_task_list[0], args.verbose)
    if args.delete_task_list:
        tasklists.delete_tasklist(creds, args.delete_task_list[0], args.verbose)
    if len(sys.argv) == 1:
        parser.print_usage()


if __name__ == '__main__':
    main()
