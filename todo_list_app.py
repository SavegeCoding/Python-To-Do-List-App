from functools import wraps
from typing import Optional
from functools import reduce
from itertools import groupby
from collections import defaultdict
import json

default_json_code = [
                    {
                        "title": "example task",
                        "priority": 3,
                        "tags": ["evening", "weekend"],
                        "done": False
                    }
                ]

#function for handling an empty task_manager.json file
def default_json_write(filename: str = "todo_list_app.json", write_safety_data = False):
    try:
        if write_safety_data:
            with open(filename, "w") as f:
                json.dump(default_json_code, f)

        else:
            with open(filename, "r+") as f:
                lines = f.read().rstrip()
                f.seek(0)

                if not lines:
                    json.dump(default_json_code, f)
    except FileNotFoundError:
        with open(filename, "w") as f:
            json.dump(default_json_code, f)
    except:
        pass

#function for saving tasks
def save_tasks(tasks_lst, filename: str = "todo_list_app.json") -> None:
    with open(filename, "w") as f:
        json.dump(tasks_lst, f, indent=4)

#function for loading tasks
def load_tasks(filename = "todo_list_app.json", show_error = False):
    try:
        with open(filename, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("tasks data must be a list")

        for task in data:
            if not isinstance(task, dict):
                raise ValueError("each task must be a dictionary")
            if "title" not in task or "priority" not in task or "tags" not in task or "done" not in task:
                raise ValueError("missing required task fields")
            
        if not data:
            default_json_write(write_safety_data=True)

        return data
    
    except FileNotFoundError:
        with open(filename, "w") as f:
            json.dump(default_json_code, f)

    except Exception as e:
        if show_error:
            print(f"Cannot load tasks from todo_list_app.json. The error was {e}")
            return False
        else:
            return False
    
#function for creating tasks    
def create_task(title: str, priority: int, tags: list) -> dict:
    #handle the priority range (1-5)
    if priority < 1:
        priority = 1
    elif priority > 5:
        priority = 5

    #add the task
    task = {"title": title, "priority": priority, "tags": tags, "done": False}
    return task

#function for filtering tasks
def filter_tasks(tasks_lst, min_priority: int, tag: Optional[str] = None) -> list[dict]:
    filtered_tasks = [
        task for task in tasks_lst
        if task["priority"] >= min_priority and (tag is None or tag in task["tags"])
    ]

    return sorted(filtered_tasks, key=lambda task: task["priority"], reverse=True)

#function for grouping tasks by their tags
def group_tasks_by_tag(tasks_lst) -> dict[str, list[dict]]:
    groups = defaultdict(list)

    for task in tasks_lst:
        tags = task.get("tags", [])

        for tag in tags:
            groups[tag if tag else "untagged"].append(task)

    # sorting rules
    def sort_key(tag):
        if tag == "urgent":
            return (0, tag)
        elif tag == "untagged":
            return (2, tag)
        else:
            return (1, tag)

    return_groups = dict(sorted(groups.items(), key=lambda item: sort_key(item[0])))

    for tag, tasks in return_groups.items():
        tasks.sort(key=lambda task: task["priority"], reverse=True)

    return return_groups

def is_duplicate_task(tasks_lst, task: dict) -> bool:
    for existing_task in tasks_lst:
        if (
            existing_task["title"] == task["title"]
            and existing_task["priority"] == task["priority"]
            and existing_task["tags"] == task["tags"]
        ):
            return True

    return False

def delete_task(tasks_lst, task_to_delete: dict, delete_by_tags: bool, delete_all = False, leave_one = False):
    if delete_all:
        tasks_lst = [task for task
                  in tasks_lst if not (task["title"] == task_to_delete["title"]
                                        and (not delete_by_tags or task["tags"] == task_to_delete["tags"]))]
    
    elif leave_one:
        seen = False
        new_tasks = []

        for task in tasks_lst:
            match = (
                task["title"] == task_to_delete["title"] and
                (not delete_by_tags or task["tags"] == task_to_delete["tags"])
            )

            if match:
                if not seen:
                    new_tasks.append(task)  # keep the first one
                    seen = True
            else:
                new_tasks.append(task)

        tasks_lst = new_tasks

    else:
        for task in tasks_lst:
            if (task["title"] == task_to_delete["title"] and task["tags"] == task_to_delete["tags"] and delete_by_tags) or (
                task["title"] == task_to_delete["title"] and not delete_by_tags
            ):
                tasks_lst.remove(task)
                break
    
    
    return tasks_lst

def delete_finished_task(tasks_lst):
    tasks_lst = [task for task
                 in tasks_lst if not task["done"]]
    
    return tasks_lst

def mark_tasks(tasks_lst, task_to_mark, mark_done, tags = None, mark_all = False):
    if tags is not None:
        tags = sorted(tags)

    for task in tasks_lst:
        if task["title"] == task_to_mark and tags is None and mark_done and not task["done"]:
            task["done"] = True

            if not mark_all:
                break
        elif task["title"] == task_to_mark and sorted(task["tags"]) == tags and not task["done"]:
            task["done"] = True

            if not mark_all:
                break

        if task["title"] == task_to_mark and tags is None and not mark_done and task["done"]:
            task["done"] = False

            if not mark_all: 
                break

    return tasks_lst