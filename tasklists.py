#!/usr/bin/env python3

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_tasklist_id(creds, title):
    """
    Get task list ID from title
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        results = service.tasklists().list(maxResults=100).execute()
        items = results.get('items')

        for item in items:
            if item['title'] == title:
                return item['id']
    except HttpError as err:
        print(err)


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
