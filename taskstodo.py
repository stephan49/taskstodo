#!/usr/bin/env python3

import sys
import os.path
import argparse
import tasklists
import tasks

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/tasks']
CMDS = ['show-lists', 'list', 'task']

# Parse command line arguments
parser = argparse.ArgumentParser(description="Manage Google Tasks")
subparsers = parser.add_subparsers()

parser_show_lists = subparsers.add_parser(CMDS[0], help='show all task lists')
parser_show_lists.add_argument('-m', '--max-results', metavar='number',
                               default=10, type=int,
                               help='''max number of lists to return
                               (default: %(default)s)''')
parser_show_lists.add_argument('-v', '--verbose', action='store_true',
                               help='show verbose messages')

parser_list = subparsers.add_parser(CMDS[1], help='manage a task list')
group_list = parser_list.add_mutually_exclusive_group()
group_list.add_argument('-c', '--create', action='store_true',
                        help='create new task list')
group_list.add_argument('-d', '--delete', action='store_true',
                        help='delete existing task list')
group_list.add_argument('-u', '--update', metavar='title', type=str,
                        help='update title of task list')
parser_list.add_argument('-l', '--list', metavar='number', default=-1,
                         type=int, dest='list_num', help='select task list')
parser_list.add_argument('-v', '--verbose', action='store_true',
                         help='show verbose messages')
parser_list.add_argument('list_title', type=str,
                         help='title of task list to use')

parser_task = subparsers.add_parser(CMDS[2], help='manage tasks')
group_task = parser_task.add_mutually_exclusive_group()
group_task.add_argument('-c', '--create', metavar='title', type=str,
                        help='create new task')
group_task.add_argument('-d', '--delete', action='store_true',
                        help='delete existing task')
group_task.add_argument('-u', '--update', metavar='title', type=str,
                        help='update title of task')
parser_task.add_argument('-t', '--task', metavar='number', default=-1,
                         dest='task_num', type=int, help='select task')
parser_task.add_argument('-l', '--list', metavar='number', default=-1,
                         dest='list_num', type=int, help='select task list')
parser_task.add_argument('-v', '--verbose', action='store_true',
                         help='show verbose messages')
parser_task.add_argument('list_title', type=str,
                         help='title of task list to use')

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

    if len(sys.argv) == 1:
        parser.print_usage()
        return

    if sys.argv[1] == CMDS[0]:
        tasklists.get_all_tasklists(creds, args.max_results, args.verbose)
        return

    if sys.argv[1] == CMDS[1]:
        if args.create:
            tasklists.create_tasklist(creds, args.list_title, args.verbose)
        elif args.delete:
            tasklists.delete_tasklist(creds, args.list_title, args.list_num,
                                      args.verbose)
        elif args.update:
            tasklists.update_tasklist(creds, args.list_title, args.update,
                                      args.list_num, args.verbose)
        else:
            tasklists.get_tasklist(creds, args.list_title, args.list_num,
                                   args.verbose)
        return

    if sys.argv[1] == CMDS[2]:
        if args.create:
            tasks.create_task(creds, args.list_title, args.create,
                              args.list_num, args.verbose)
        elif args.delete:
            tasks.delete_task(creds, args.list_title, args.task_num,
                              args.list_num, args.verbose)
        elif args.update:
            tasks.update_task(creds, args.list_title, args.update,
                              args.task_num, args.list_num, args.verbose)
        else:
            tasks.get_task(creds, args.list_title, args.task_num,
                           args.list_num, args.verbose)
        return


if __name__ == '__main__':
    main()
