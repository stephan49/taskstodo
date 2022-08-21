#!/usr/bin/env python3

from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_all_tasklists(creds, num_lists):
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

        print('Task lists:')
        for item in items:
            print('  - {0} (ID: {1})'.format(item['title'], item['id']))
    except HttpError as err:
        print(err)


def get_tasklist(creds, taskl):
    """
    Print out specific task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        results = service.tasklists().get(tasklist=taskl).execute()
        title = results.get('title')
        updated = results.get('updated')

        print('Title: {0}'.format(title))
        print('Updated: {0}'.format(updated))
    except HttpError as err:
        print(err)
