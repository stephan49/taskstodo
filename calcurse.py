#!/usr/bin/env python3

"""
Synchronize Google Tasks and calcurse TODO lists.
"""

import os.path


DATA_DIR = os.path.expanduser('~/.local/share/calcurse/')


def get_calcurse_tasks():
    """
    Read in tasks from calcurse todo file and return tasks as a list.
    """

    TODO_FILE = os.path.join(DATA_DIR, 'todo')

    with open(TODO_FILE) as f:
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
            note = get_calcurse_note(note_id)

            task['title'] = task_line
            task['note'] = note
        else:
            task['title'] = task_line[task_slice]

        tasks.append(task)

    return tasks


def get_calcurse_note(note_id):
    """
    Read in note file of associated calcurse task and return as a string.
    """

    NOTE_FILE = os.path.join(DATA_DIR, 'notes', note_id)

    with open(NOTE_FILE) as f:
        return f.read()


def sync_tasks():
    cc_tasks = get_calcurse_tasks()
    print(cc_tasks)
