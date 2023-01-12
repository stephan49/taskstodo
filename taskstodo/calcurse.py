#!/usr/bin/env python3

"""
Synchronize Google Tasks and calcurse TODO lists.
"""

import os
import sys
import hashlib
import threading
import time
import json
import pprint

from . import tasklists
from . import tasks

DATA_DIR = os.path.expanduser('~/.local/share/calcurse')


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
    Add tasks to calcurse.
    """

    with open(os.path.join(data_dir, 'todo'), 'a') as f:
        for task in new_tasks:
            if task.get('note'):
                # Compute and add hash of note
                note_bytes = bytes(f"{task['note']}\n", 'utf-8')
                note_hash = hashlib.sha1(note_bytes).hexdigest()
                f.write(f"[0]>{note_hash} {task['title']}\n")

                with open(os.path.join(data_dir, 'notes', note_hash), 'w') as n:
                    n.write(task['note'] + '\n')
            else:
                f.write(f"[0] {task['title']}\n")


def delete_calcurse_tasks(old_tasks, data_dir=DATA_DIR):
    """
    Delete tasks from calcurse.
    """

    todo_file = os.path.join(data_dir, 'todo')
    with open(todo_file, 'r') as f:
        cur_tasks = f.readlines()

    old_tasks = [t['title'] for t in old_tasks]
    with open(todo_file, 'w') as f:
        for task in cur_tasks:
            task_string = ' '.join(task.split()[1:])
            if task_string not in old_tasks:
                f.write(task)


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


def delete_google_tasks(creds, list_title, old_tasks):
    """
    Delete tasks from Google.
    """

    cur_tasks = tasklists.get_tasklist(creds, list_title, -1)['tasks']
    cur_tasks = [t['title'] for t in cur_tasks]
    old_tasks = [t['title'] for t in old_tasks]

    # Delete tasks in reverse order to prevent shifting index
    for task in reversed(old_tasks):
        if task in cur_tasks:
            task_num = cur_tasks.index(task)
            tasks.delete_task(creds, list_title, task_num, -1, False)


def add_google_tasks(creds, list_title, list_num, new_tasks):
    """
    Add tasks to Google Tasks.
    """

    for t, new_task in enumerate(list(reversed(new_tasks))):
        t = threading.Thread(target=tasks.create_task,
                             args=(creds, list_title, new_task['title'],
                                   new_task.get('note'), list_num, False))
        time.sleep(0.1)  # Helps keep insertion order of tasks
        t.start()


def sync_tasks(creds, list_title, list_num, verbose, data_dir=DATA_DIR):
    """
    Sync Google and calcurse tasks.
    """

    taskstodo_data_dir = os.path.expanduser('~/.local/share/taskstodo')
    if not os.path.exists(taskstodo_data_dir):
        os.mkdir(taskstodo_data_dir)

    # Check for or create lock file to prevent multiple running instances
    lock = os.path.join(taskstodo_data_dir, 'lock')
    if os.path.exists(lock):
        print('An existing instance is already running or lock was not released.', file=sys.stderr)
        sys.exit(1)
    else:
        os.mknod(lock, mode=0o644)

    # Read in synced task list if available
    sync_file = os.path.join(taskstodo_data_dir, 'calcurse-sync.json')
    synced_tasks = []
    try:
        with open(sync_file, 'r') as f:
            synced_tasks = json.load(f)
    except FileNotFoundError:
        pass

    try:
        # Read in Google Tasks list
        g_tasks = get_google_tasks(creds, list_title, list_num)
        if g_tasks is None:
            return

        # Read in calcurse todo list
        c_tasks = get_calcurse_tasks(data_dir)

        # Compare Google Tasks to calcurse and get tasks to add or delete
        new_c_tasks = []
        old_g_tasks = []
        for g_task in g_tasks:
            if g_task not in c_tasks:
                if g_task not in synced_tasks:
                    new_c_tasks.append(g_task)
                else:
                    old_g_tasks.append(g_task)

        delete_google_tasks(creds, list_title, old_g_tasks)
        add_calcurse_tasks(new_c_tasks, data_dir)

        # Compare calcurse to Google Tasks and get tasks to add or delete
        new_g_tasks = []
        old_c_tasks = []
        for c_task in c_tasks:
            if c_task not in g_tasks:
                if c_task not in synced_tasks:
                    new_g_tasks.append(c_task)
                else:
                    old_c_tasks.append(c_task)

        delete_calcurse_tasks(old_c_tasks, data_dir)
        add_google_tasks(creds, list_title, list_num, new_g_tasks)

        # Updated synced tasks
        synced_tasks = get_calcurse_tasks(data_dir)

        with open(sync_file, 'w') as f:
            json.dump(synced_tasks, f)
    finally:
        os.remove(lock)

    if verbose:
        print('Google tasks:')
        pprint.pp(g_tasks)
        print('\ncalcurse tasks:')
        pprint.pp(c_tasks)
        print('\ncalcurse tasks added:')
        pprint.pp(new_c_tasks)
        print('\nGoogle tasks added:')
        pprint.pp(new_g_tasks)
        print('\ncalcurse tasks deleted:')
        pprint.pp(old_c_tasks)
        print('\nGoogle tasks deleted:')
        pprint.pp(old_g_tasks)
