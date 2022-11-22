#!/usr/bin/env python3

import sys
import os.path
import argparse

from . import tasklists
from . import tasks
from . import calcurse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/tasks']
CMDS = ['show-lists', 'list', 'task', 'sync-calcurse']

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
group_task.add_argument('-m', '--move', metavar='number', type=int,
                        help='move task to new position')
parser_task.add_argument('-n', '--note', metavar='note', type=str,
                         help='create note for task')
parser_task.add_argument('-t', '--task', metavar='number', default=-1,
                         dest='task_num', type=int, help='select task')
parser_task.add_argument('-l', '--list', metavar='number', default=-1,
                         dest='list_num', type=int, help='select task list')
parser_task.add_argument('-v', '--verbose', action='store_true',
                         help='show verbose messages')
parser_task.add_argument('list_title', type=str,
                         help='title of task list to use')

parser_sync_calcurse = subparsers.add_parser(CMDS[3],
                                             help='sync with calcurse tasks')
parser_sync_calcurse.add_argument('list_title', type=str,
                                  help='title of task list to use')
parser_sync_calcurse.add_argument('-l', '--list', metavar='number', default=-1,
                                  type=int, dest='list_num',
                                  help='select task list')
parser_sync_calcurse.add_argument('-v', '--verbose', action='store_true',
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


def show_lists():
    creds = auth_user()
    tasklists.print_all_tasklists(creds, args.max_results, args.verbose)
    return


def manage_lists():
    creds = auth_user()
    if args.create:
        tasklists.create_tasklist(creds, args.list_title, args.verbose)
    elif args.delete:
        tasklists.delete_tasklist(creds, args.list_title, args.list_num,
                                  args.verbose)
    elif args.update:
        tasklists.update_tasklist(creds, args.list_title, args.update,
                                  args.list_num, args.verbose)
    else:
        tasklists.print_tasklist(creds, args.list_title, args.list_num,
                                 args.verbose)
    return


def manage_tasks():
    creds = auth_user()
    if args.create:
        tasks.create_task(creds, args.list_title, args.create, args.note,
                          args.list_num, args.verbose)
    elif args.delete:
        tasks.delete_task(creds, args.list_title, args.task_num, args.list_num,
                          args.verbose)
    elif args.update:
        tasks.update_task(creds, args.list_title, args.update, args.task_num,
                          args.list_num, args.verbose)
    elif args.note:
        tasks.create_note(creds, args.list_title, args.note, args.task_num,
                          args.list_num, args.verbose)
    elif args.move or args.move == 0:
        tasks.move_task(creds, args.list_title, args.move, args.task_num,
                        args.list_num, args.verbose)
    elif args.task_num != -1:
        tasks.get_task(creds, args.list_title, args.task_num, args.list_num,
                       args.verbose)
    else:
        tasklists.print_tasklist(creds, args.list_title, args.list_num,
                                 args.verbose)
    return


def sync_calcurse():
    creds = auth_user()
    calcurse.sync_tasks(creds, args.list_title, args.list_num, args.verbose)


def main():
    if len(sys.argv) == 1:
        parser.print_usage()
    elif sys.argv[1] == CMDS[0]:
        show_lists()
    elif sys.argv[1] == CMDS[1]:
        manage_lists()
    elif sys.argv[1] == CMDS[2]:
        manage_tasks()
    elif sys.argv[1] == CMDS[3]:
        sync_calcurse()


if __name__ == '__main__':
    main()
