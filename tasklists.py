#!/usr/bin/env python3

import pickle

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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

        with open('tasklists.dat', 'wb') as f:
            pickle.dump(tasklists_id_title, f)

        return tasklists_id_title
    except HttpError as err:
        print(err)


def get_tasklist_id(creds, title):
    """
    Get task list ID from title.
    """

    tasklists_id_title = {}
    try:
        # Read in any cached task lists file
        with open('tasklists.dat', 'rb') as f:
            tasklists_id_title = pickle.load(f)
    except FileNotFoundError:
        tasklists_id_title = create_tasklist_cache(creds)

    for tasklist_id in tasklists_id_title:
        if tasklists_id_title[tasklist_id] == title:
            return tasklist_id

    # Refresh cache and try again if title not found
    tasklists_id_title = create_tasklist_cache(creds)
    for tasklist_id in tasklists_id_title:
        if tasklists_id_title[tasklist_id] == title:
            return tasklist_id


def get_all_tasklists(creds, num_lists, verbose=False):
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


def get_tasklist(creds, title, verbose=False):
    """
    Print out specific task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_id = get_tasklist_id(creds, title)
        if not tasklist_id:
            print('Task list does not exist')
            return
        results = service.tasklists().get(tasklist=tasklist_id).execute()
        tasklist_id = results.get('id')
        tasklist_updated = results.get('updated')

        print('ID: {0}'.format(tasklist_id))
        print('Updated: {0}'.format(tasklist_updated))
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def create_tasklist(creds, title, verbose=False):
    """
    Create a new task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist = {"title": title}
        service.tasklists().insert(body=tasklist).execute()
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def delete_tasklist(creds, title, verbose=False):
    """
    Delete a task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_id = get_tasklist_id(creds, title)
        if not tasklist_id:
            print('Task list does not exist')
            return
        service.tasklists().delete(tasklist=tasklist_id).execute()
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())


def update_tasklist(creds, title, new_title, verbose=False):
    """
    Update title of task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist_id = get_tasklist_id(creds, title)
        if not tasklist_id:
            print('Task list does not exist')
            return
        new_tasklist = {"title": new_title}
        service.tasklists().patch(tasklist=tasklist_id,
                                  body=new_tasklist).execute()
    except HttpError as err:
        if verbose:
            print(err)
        else:
            print(err._get_reason())
