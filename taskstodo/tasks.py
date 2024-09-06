#!/usr/bin/env python3

"""
Create, read, update or delete tasks.
"""

from . import tasklists

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_task_id(creds, list_id, task_num):
    """
    Get task ID from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    try:
        # Get all tasks in list
        results = service.tasks().list(
                tasklist=list_id, maxResults=100).execute()

        # Ensure task number is within range
        if task_num is None or task_num > len(
                results['items']) - 1 or task_num < 0:
            return None
    except HttpError as err:
        print(err)

    items = results.get('items')
    # Sort task items by position key instead of update time
    items.sort(key=lambda items: items['position'])
    return items[task_num]['id']


def get_task(creds, list_title, task_num, list_num, verbose):
    """
    Print out task details.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num is None:
            list_num = 0

        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        if task_id is None:
            print('Invalid task number')
            return

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
        task_note = results.get('notes')
        print('Title: {}'.format(task_title))
        print('Updated: {}'.format(task_updated))
        print('Note: {}'.format(task_note))

        # Update cache file
        tasklists.create_tasklist_cache(creds)


def create_task(creds, list_title, task_title, note, list_num, verbose):
    """
    Create new task on specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        task = {'title': task_title}

        if note:
            task['notes'] = note

        if len(tasklist_ids) == 1 or list_num is None:
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

        # Update cache file
        tasklists.create_tasklist_cache(creds)


def delete_task(creds, list_title, task_num, list_num, verbose):
    """
    Delete task from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num is None:
            list_num = 0

        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        if task_id is None:
            print('Invalid task number')
            return

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

        # Update cache file
        tasklists.create_tasklist_cache(creds)


def update_task(creds, list_title, task_title, task_num, list_num, verbose):
    """
    Update task title from specified task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num is None:
            list_num = 0

        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        if task_id is None:
            print('Invalid task number')
            return

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

        # Update cache file
        tasklists.create_tasklist_cache(creds)


def move_task(creds, list_title, new_pos, task_num, list_num, verbose):
    """
    Move task to new position in task list.
    """

    if new_pos == task_num:
        return

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num is None:
            list_num = 0

        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        if task_id is None:
            print('Invalid task number')
            return

        out_of_range = False
        if new_pos >= 0:
            # Check if task is moving up or down
            if new_pos < task_num:
                new_pos = new_pos - 1
            # ID of task that will be previous to moved task
            prev_id = get_task_id(creds, tasklist_ids[list_num], new_pos)

            if prev_id is None and new_pos != -1:
                out_of_range = True
        else:
            out_of_range = True

        if out_of_range:
            print("New position is out of range")
            return

        try:
            # Move task
            service.tasks().move(tasklist=tasklist_ids[list_num],
                                 task=task_id, previous=prev_id).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return

        # Update cache file
        tasklists.create_tasklist_cache(creds)


def create_note(creds, list_title, note, task_num, list_num, verbose):
    """
    Create note for specified task.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = tasklists.get_tasklist_ids(creds, list_title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and (list_num is None or list_num < 0
                                    or list_num > len(tasklist_ids) - 1):
        tasklists.print_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num is None:
            list_num = 0

        task_id = get_task_id(creds, tasklist_ids[list_num], task_num)
        if task_id is None:
            print('Invalid task number')
            return

        # Accept new line character
        note = note.replace('\\n', '\n')
        new_task = {'notes': note}
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

        # Update cache file
        tasklists.create_tasklist_cache(creds)
