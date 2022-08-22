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


def get_tasklist(creds, task_list):
    """
    Print out specific task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        results = service.tasklists().get(tasklist=task_list).execute()
        task_title = results.get('title')
        task_updated = results.get('updated')

        print('Title: {0}'.format(task_title))
        print('Updated: {0}'.format(task_updated))
    except HttpError as err:
        print(err)


def create_tasklist(creds, title):
    """
    Create a new task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        tasklist = {"title": title}
        results = service.tasklists().insert(body=tasklist).execute()
        task_title = results.get('title')
        task_id = results.get('id')

        print('Task list created: {0} (ID: {1})'.format(task_title, task_id))
    except HttpError as err:
        print(err)


def delete_tasklist(creds, task_list):
    """
    Delete a task list.
    """

    try:
        service = build('tasks', 'v1', credentials=creds)
        service.tasklists().delete(tasklist=task_list).execute()
    except HttpError as err:
        print(err)
