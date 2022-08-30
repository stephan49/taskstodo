#!/usr/bin/env python3

import pickle

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CACHE_FILE = 'tasklists.dat'


def create_tasklist_cache(creds):
    """
    Get task list IDs and titles from server and dump results to cache file.

    Return dictionary of task list IDs and titles.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        results = service.tasklists().list(maxResults=100).execute()
        items = results.get('items')
        tasklists_id_title = {}
        for item in items:
            tasklists_id_title[item['id']] = item['title']

        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(tasklists_id_title, f)

        return tasklists_id_title
    except HttpError as err:
        print(err)


def load_tasklist_cache():
    """
    Load task list IDs and titles from cache file.

    Return dictionary of task list IDs and titles.
    """

    tasklists_id_title = {}
    try:
        with open(CACHE_FILE, 'rb') as f:
            tasklists_id_title = pickle.load(f)

        return tasklists_id_title
    except FileNotFoundError:
        pass


def print_duplicates(tasklist_ids):
    """
    Print task lists with duplicate titles
    """

    print('Multiple task lists with duplicate titles found:')
    for i in range(len(tasklist_ids)):
        print('{0}. ID: {1}'.format(i, tasklist_ids[i]))
    print('\nUse -s option to select match')


def get_tasklist_ids(creds, title):
    """
    Get task list IDs matching title.

    Return list of task list IDs.
    """

    tasklists_id_title = load_tasklist_cache()
    if not tasklists_id_title:
        tasklists_id_title = create_tasklist_cache(creds)

    tasklist_ids = []
    for tasklist_id in tasklists_id_title:
        if tasklists_id_title[tasklist_id] == title:
            tasklist_ids.append(tasklist_id)

    if not tasklist_ids:
        # Refresh cache and try again if title not found
        tasklists_id_title = create_tasklist_cache(creds)
        for tasklist_id in tasklists_id_title:
            if tasklists_id_title[tasklist_id] == title:
                tasklist_ids.append(tasklist_id)

    return tasklist_ids


def get_all_tasklists(creds, num_lists, verbose):
    """
    Print out all task lists.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        results = service.tasklists().list(maxResults=num_lists).execute()
        items = results.get('items')

        if not items:
            print('No task lists found.')
            return

        for item in items:
            print('- {0}'.format(item['title']))
            if verbose:
                print('  - ID: {0}'.format(item['id']))
                print('  - Updated: {0}'.format(item['updated']))
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def get_tasklist(creds, title, select, verbose):
    """
    Print out specific task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_ids = get_tasklist_ids(creds, title)
        if not tasklist_ids:
            print('Task list does not exist')
        elif len(tasklist_ids) > 1 and select == -1:
            # Show duplicate titled lists when no selection made
            print_duplicates(tasklist_ids)
        else:
            if len(tasklist_ids) == 1 or select == -1:
                select = 0
            results = service.tasklists().get(
                    tasklist=tasklist_ids[select]).execute()
            tasklist_ids = results.get('id')
            tasklist_updated = results.get('updated')

            print('ID: {0}'.format(tasklist_ids))
            print('Updated: {0}'.format(tasklist_updated))
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def create_tasklist(creds, title, verbose):
    """
    Create a new task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist = {"title": title}
        results = service.tasklists().insert(body=tasklist).execute()
        tasklist_id = results.get('id')

        # Update cache file
        tasklists_id_title = load_tasklist_cache()
        if tasklists_id_title is not None:
            tasklists_id_title[tasklist_id] = title
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(tasklists_id_title, f)
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def delete_tasklist(creds, title, select, verbose):
    """
    Delete a task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_ids = get_tasklist_ids(creds, title)
        if not tasklist_ids:
            print('Task list does not exist')
        elif len(tasklist_ids) > 1 and select == -1:
            # Show duplicate titled lists when no selection made
            print_duplicates(tasklist_ids)
        else:
            if len(tasklist_ids) == 1 or select == -1:
                select = 0
            service.tasklists().delete(tasklist=tasklist_ids[select]).execute()

            # Update cache file
            tasklists_id_title = load_tasklist_cache()
            tasklists_id_title.pop(tasklist_ids[select])
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(tasklists_id_title, f)
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def update_tasklist(creds, title, new_title, select, verbose):
    """
    Update title of task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_ids = get_tasklist_ids(creds, title)
        if not tasklist_ids:
            print('Task list does not exist')
        elif len(tasklist_ids) > 1 and select == -1:
            # Show duplicate titled lists when no selection made
            print_duplicates(tasklist_ids)
        else:
            if len(tasklist_ids) == 1 or select == -1:
                select = 0
            new_tasklist = {"title": new_title}
            service.tasklists().patch(tasklist=tasklist_ids[select],
                                      body=new_tasklist).execute()

            # Update cache file
            tasklists_id_title = load_tasklist_cache()
            tasklists_id_title[tasklist_ids[select]] = new_title
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(tasklists_id_title, f)
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())
