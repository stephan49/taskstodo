#!/usr/bin/env python3

"""
Synchronize Google Tasks and calcurse TODO lists.
"""

import os.path
import hashlib
import threading
import time

from . import tasklists
from . import tasks
import pprint

#DATA_DIR = os.path.expanduser('~/.local/share/calcurse')


def get_calcurse_tasks(data_dir=DATA_DIR):
    """
    Read in tasks from calcurse todo file and return tasks as a list.
    """

    with open(os.path.join(data_dir, 'todo')) as f:
        task_lines = f.readlines()

    tasks = []
    task_slice = slice(4, -1)

    for task_line in task_lines:
        task = {}

        # Check for task note
        if task_line[3] == '>':
            note_id = task_line.split()[0][4:]
            task_line = task_line[task_slice].split()[1:]
            task_line = ' '.join(task_line)
            with open(os.path.join(data_dir, 'notes', note_id)) as f:
                note = f.read().rstrip('\n')

            task['title'] = task_line
            task['note'] = note
        else:
            task['title'] = task_line[task_slice]

        tasks.append(task)

    return tasks


def add_calcurse_tasks(new_tasks, data_dir=DATA_DIR):
    """
    Add missing tasks to calcurse.
    """

    with open(os.path.join(data_dir, 'todo'), 'a') as f:
        for task in new_tasks:
            if task.get('note'):
                # Compute and add hash of note
                note_bytes = bytes(f"{task['note']}\n", 'utf-8')
                note_hash = hashlib.sha1(note_bytes).hexdigest()
                f.write(f"[0]>{note_hash} {task['title']}\n")

                with open(os.path.join(data_dir, 'notes', note_hash), 'w') as f:
                    f.write(task['note'] + '\n')
            else:
                f.write(f"[0] {task['title']}\n")


def get_google_tasks(creds, list_title, list_num):
    """
    Get Google Tasks from server and return tasks as list.

    Formats data to allow for comparison with calcurse.
    """

    tasks = tasklists.get_tasklist(creds, list_title, list_num)
    if tasks:
        tasks = tasks['tasks']
        for task in tasks:
            task.pop('id')
            task.pop('updated')
            task.pop('position')
            if not task['note']:
                task.pop('note')

        return tasks


def add_google_tasks(creds, list_title, list_num, new_tasks):
    """
    Add missing tasks to Google Tasks.
    """

    for t, new_task in enumerate(list(reversed(new_tasks))):
        t = threading.Thread(target=tasks.create_task,
                             args=(creds, list_title, new_task['title'],
                                   new_task.get('note'), list_num, False))
        time.sleep(0.1)  # Helps keep insertion order of tasks
        t.start()


def sync_tasks(creds, list_title, list_num, data_dir=DATA_DIR):
    """
    Sync Google and calcurse tasks.
    """

    # Read in Google Tasks list
    print('Google Tasks:')
    g_tasks = get_google_tasks(creds, list_title, list_num)
    pprint.pp(g_tasks)
    print()

    # Read in calcurse todo list
    print('calcurse:')
    c_tasks = get_calcurse_tasks(data_dir)
    pprint.pp(c_tasks)
    print()

    # Compare Google Tasks to calcurse and get missing tasks to add
    new_c_tasks = []
    print('Google Tasks not in calcurse:')
    for g_task in g_tasks:
        if g_task not in c_tasks:
            new_c_tasks.append(g_task)
            pprint.pp(g_task)

    add_calcurse_tasks(new_c_tasks, data_dir)

    print()

    # Compare calcurse to Google Tasks and get missing tasks to add
    new_g_tasks = []
    print('calcurse tasks not in Google Tasks:')
    for c_task in c_tasks:
        if c_task not in g_tasks:
            new_g_tasks.append(c_task)
            pprint.pp(c_task)

    add_google_tasks(creds, list_title, list_num, new_g_tasks)
