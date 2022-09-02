#!/usr/bin/env python3

import tasklists

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_task(creds, tasklist_title, task_title, select, verbose):
    """
    Create new task on specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, tasklist_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and select == -1:
        # Show duplicate titled lists when no selection made
        tasklists.print_duplicates(tasklist_ids)
    else:
        task = {'title': task_title}
        if len(tasklist_ids) == 1 or select == -1:
            select = 0
        try:
            # Create task
            service.tasks().insert(tasklist=tasklist_ids[select],
                                   body=task).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return
