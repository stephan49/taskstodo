# taskstodo

taskstodo is a command-line application for managing Google Tasks, allowing you to view, create, update and delete task lists and their associated tasks. taskstodo can also perform a two-way sync between Google Tasks and [calcurse](https://calcurse.org/).

# Installation

```
pip install taskstodo
```

# Configuration

- Create new Google Cloud [project](https://console.cloud.google.com/projectcreate)
- Enable [Tasks API](https://console.cloud.google.com/apis/library/tasks.googleapis.com)
- Create new OAuth 2.0 client ID [credentials](https://console.cloud.google.com/apis/credentials)
- Download JSON file of credentials
- Copy file to `~/.config/taskstodo/credentials.json`
- Configure [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) as an external user type

# Usage

Create task list:

```
taskstodo list -c <list_title>
```

Create task:

```
taskstodo task -c <task_title> [-n <note>] <list_title>
```

Show task lists:

```
taskstodo show-lists
```

Show tasks:

```
taskstodo list <list_title>
```

Update task list:

```
taskstodo list -u <new_title> -t <task_number> <list_title>
```

Update task:

```
taskstodo task -u <new_title> -t <task_number> <list_title>
```

Move task:

```
taskstodo task -m <new_position> -t <task_number> <list_title>
```

Delete task:

```
taskstodo task -d -t <task_number> <list_title>
```

Delete task list:

```
taskstodo list -d <list_title>
```

Sync calcurse and Google Tasks:

```
taskstodo sync-calcurse <list_title>
```

Show help:

```
taskstodo -h
```
