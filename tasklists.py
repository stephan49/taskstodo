#!/usr/bin/env python3

import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CACHE_FILE = 'tasklists.json'


def create_tasklist_cache(creds):
    """
    Get task list details from server and dump results to cache file.

    Return list of dictionaries of task lists.
    """

    service = build('tasks', 'v1', credentials=creds)
    try:
        results = service.tasklists().list(maxResults=100).execute()
    except HttpError as err:
        print(err)
        return

    items = results.get('items')
    tasklists = []
    for i in range(len(items)):
        tasklists.append({"id": items[i]['id']})
        tasklists[i]["title"] = items[i]['title']
        tasklists[i]["updated"] = items[i]['updated']

    with open(CACHE_FILE, 'w') as f:
        json.dump(tasklists, f, indent=4)

    return tasklists


def load_tasklist_cache():
    """
    Load task list IDs and titles from cache file.

    Return list of dictionaries of task lists.
    """

    tasklists = []
    try:
        with open(CACHE_FILE, 'r') as f:
            tasklists = json.load(f)

        return tasklists
    except FileNotFoundError:
        pass


def get_duplicates(tasklist_ids):
    """
    Print task lists with duplicate titles
    """

    print('Multiple task lists with duplicate titles found:')
    for i in range(len(tasklist_ids)):
        print('{0}. ID: {1}'.format(i, tasklist_ids[i]))
    print('\nUse -l option to select list number')


def get_tasklist_ids(creds, title):
    """
    Get task list IDs matching title.

    Return list of task list IDs.
    """

    tasklists = load_tasklist_cache()
    if not tasklists:
        tasklists = create_tasklist_cache(creds)

    tasklist_ids = []
    for tasklist in tasklists:
        if tasklist['title'] == title:
            tasklist_ids.append(tasklist['id'])

    if not tasklist_ids:
        # Refresh cache and try again if title not found
        tasklists = create_tasklist_cache(creds)
        for tasklist in tasklists:
            if tasklist['title'] == title:
                tasklist_ids.append(tasklist['id'])

    return tasklist_ids


def get_all_tasklists(creds, num_lists, verbose):
    """
    Print out all task lists.
    """

    service = build('tasks', 'v1', credentials=creds)
    try:
        # Get all task lists
        results = service.tasklists().list(maxResults=num_lists).execute()
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())
        return

    items = results.get('items')
    if not items:
        print('No task lists found.')
        return

    for item in items:
        print('- {0}'.format(item['title']))
        if verbose:
            print('  - ID: {0}'.format(item['id']))
            print('  - Updated: {0}'.format(item['updated']))


def get_tasklist(creds, title, list_num, verbose):
    """
    Print out specific task list and its tasks.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = get_tasklist_ids(creds, title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        try:
            # Get task list
            tasklist_results = service.tasklists().get(
                    tasklist=tasklist_ids[list_num]).execute()
            # Get tasks for task list
            task_results = service.tasks().list(
                    tasklist=tasklist_ids[list_num]).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return

        if verbose:
            tasklist_id = tasklist_results.get('id')
            tasklist_updated = tasklist_results.get('updated')
            print('ID: {0}'.format(tasklist_id))
            print('Updated: {0}'.format(tasklist_updated))
            print()

        print('Tasks:')
        task_items = task_results.get('items')
        for i in range(len(task_items)):
            if verbose:
                print('{0}. {1} (ID: {2})'.format(i, task_items[i]['title'],
                                                  task_items[i]['id']))
            else:
                print('{0}. {1}'.format(i, task_items[i]['title']))
        # TODO: cache results to file


def create_tasklist(creds, title, verbose):
    """
    Create a new task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist = {"title": title}
    try:
        # Create task list
        results = service.tasklists().insert(body=tasklist).execute()
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())
        return
    new_tasklist = {'id': results.get('id'), 'title': title,
                    'updated': results.get('updated')}

    # Update cache file
    tasklists = load_tasklist_cache()
    if tasklists is not None:
        tasklists.append(new_tasklist)
        with open(CACHE_FILE, 'w') as f:
            json.dump(tasklists, f, indent=4)


def delete_tasklist(creds, title, list_num, verbose):
    """
    Delete a task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = get_tasklist_ids(creds, title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        try:
            # Delete task list
            service.tasklists().delete(
                    tasklist=tasklist_ids[list_num]).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return

        # Update cache file
        tasklists = load_tasklist_cache()
        for tasklist in tasklists:
            if tasklist['id'] == tasklist_ids[list_num]:
                tasklists.remove(tasklist)
                break
        with open(CACHE_FILE, 'w') as f:
            json.dump(tasklists, f, indent=4)


def update_tasklist(creds, title, new_title, list_num, verbose):
    """
    Update title of task list.
    """

    service = build('tasks', 'v1', credentials=creds)
    tasklist_ids = get_tasklist_ids(creds, title)
    if not tasklist_ids:
        print('Task list does not exist')
    elif len(tasklist_ids) > 1 and list_num == -1:
        # Show duplicate titled lists when no selection made
        get_duplicates(tasklist_ids)
    else:
        if len(tasklist_ids) == 1 or list_num == -1:
            list_num = 0
        new_tasklist = {"title": new_title}
        try:
            # Update task list
            service.tasklists().patch(tasklist=tasklist_ids[list_num],
                                      body=new_tasklist).execute()
        except HttpError as err:
            if verbose:
                print(err)
            else:
                print(err._get_reason())
            return

        # Update cache file
        tasklists = load_tasklist_cache()
        for tasklist in tasklists:
            if tasklist['id'] == tasklist_ids[list_num]:
                tasklist['title'] = new_title
                break
        with open(CACHE_FILE, 'w') as f:
            json.dump(tasklists, f, indent=4)
