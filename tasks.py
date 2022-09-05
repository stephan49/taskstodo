#!/usr/bin/env python3

import tasklists

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_task_id(creds, list_id, task_num):
    """
    Get task ID from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    try:
        # Get all tasks in list
        results = service.tasks().list(tasklist=list_id).execute()
    except HttpError as err:
        print(err)

    items = results.get('items')
    return items[task_num]['id']


def get_task(creds, list_title, task_num, list_num, verbose):
    """
    Print out task details.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        tasklists.get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        try:
            # Get task
            results = service.tasks().get(tasklist=tasklist_ids[list_num],
                                          task=task_id).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return

        if verbose:
            print('ID: {}'.format(task_id))
        task_title = results.get('title')
        task_updated = results.get('updated')
        task_notes = results.get('notes')
        print('Title: {}'.format(task_title))
        print('Updated: {}'.format(task_updated))
        print('Notes: {}'.format(task_notes))


def create_task(creds, list_title, task_title, list_num, verbose):
    """
    Create new task on specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        tasklists.get_duplicates(tasklist_ids)
    else:
        task = {'title': task_title}
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        try:
            # Create task
            service.tasks().insert(tasklist=tasklist_ids[list_num],
                                   body=task).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return


def delete_task(creds, list_title, task_num, list_num, verbose):
    """
    Delete task from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        tasklists.get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        try:
            # Get task
            service.tasks().delete(tasklist=tasklist_ids[list_num],
                                   task=task_id).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return


def update_task(creds, list_title, task_title, task_num, list_num, verbose):
    """
    Update task title from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        tasklists.get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        new_task = {'title': task_title}
        try:
            # Update task
            service.tasks().patch(tasklist=tasklist_ids[list_num],
                                  task=task_id, body=new_task).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return
