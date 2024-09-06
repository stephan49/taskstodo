#!/usr/bin/env python3

import sys
import os
import argparse

from . import tasklists
from . import tasks
from . import calcurse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from httplib2.error import ServerNotFoundError

SCOPES = ['https://www.googleapis.com/auth/tasks']
CMDS = ['show-lists', 'list', 'task', 'sync-calcurse']
CFG_DIR = os.path.expanduser('~/.config/taskstodo')

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
parser_list.add_argument('-l', '--list', metavar='number', default=None,
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
group_task.add_argument('-m', '--move', metavar='number', default=None,
                        dest='new_pos', type=int,
                        help='move task to new position')
parser_task.add_argument('-n', '--note', metavar='note', type=str,
                         help='create note for task')
parser_task.add_argument('-t', '--task', metavar='number', default=None,
                         dest='task_num', type=int, help='select task')
parser_task.add_argument('-l', '--list', metavar='number', default=None,
                         dest='list_num', type=int, help='select task list')
parser_task.add_argument('-v', '--verbose', action='store_true',
                         help='show verbose messages')
parser_task.add_argument('list_title', type=str,
                         help='title of task list to use')

parser_sync_calcurse = subparsers.add_parser(CMDS[3],
                                             help='sync with calcurse tasks')
parser_sync_calcurse.add_argument('list_title', type=str,
                                  help='title of task list to use')
parser_sync_calcurse.add_argument('-l', '--list', metavar='number',
                                  default=None, type=int, dest='list_num',
                                  help='select task list')
parser_sync_calcurse.add_argument('-v', '--verbose', action='store_true',
                                  help='show verbose messages')

args = parser.parse_args()

# Convert arguments to zero-based numbering
if "list_num" in vars(args) and args.list_num is not None:
    args.list_num = args.list_num - 1
if "task_num" in vars(args) and args.task_num is not None:
    args.task_num = args.task_num - 1
if "new_pos" in vars(args) and args.new_pos is not None:
    args.new_pos = args.new_pos - 1


def auth_user():
    """
    Authenticate user with credentials.
    Return valid credentials for use with services.
    """

    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)

    token_file = os.path.join(CFG_DIR, 'token.json')
    creds_file = os.path.join(CFG_DIR, 'credentials.json')

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no valid credentials available, let user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_file):
                print('Credentials file does not exist.', file=sys.stderr)
                print('Setup credentials on Google Cloud and create:',
                      creds_file, file=sys.stderr)
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(creds_file,
                                                             SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(token_file, 'w') as token:
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
    elif args.new_pos is not None:
        tasks.move_task(creds, args.list_title, args.new_pos, args.task_num,
                        args.list_num, args.verbose)
    elif args.task_num is not None:
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
    else:
        try:
            if sys.argv[1] == CMDS[0]:
                show_lists()
            elif sys.argv[1] == CMDS[1]:
                manage_lists()
            elif sys.argv[1] == CMDS[2]:
                manage_tasks()
            elif sys.argv[1] == CMDS[3]:
                sync_calcurse()
        except ServerNotFoundError:
            print('Failed to connect to server.', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
