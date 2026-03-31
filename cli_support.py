import argparse
import task_manager

parser = argparse.ArgumentParser("Basic task manager app")
subparsers = parser.add_subparsers(dest="command", required=True)

create_parser = subparsers.add_parser("create", help="Create a task")
create_parser.add_argument("--create-title", required=True, help="Name of the task to create (required)")
create_parser.add_argument("--create-priority", type=int, default=3, help="The priority of the created task")
create_parser.add_argument("--create-tag1", default="", help="One of the tags for the created task")
create_parser.add_argument("--create-tag2", default="", help="One of the tags for the created task")
create_parser.add_argument("--create-tag3", default="", help="One of the tags for the created task")
create_parser.add_argument("--allow-duplicates", action="store_true", help="Allow duplicates of the created task")

delete_parser = subparsers.add_parser("delete", help="Delete a task that shares the same title and tags")
delete_parser.add_argument("--delete-title", required=True, help="Name of the task to delete (required)")
delete_parser.add_argument("--delete-tag1", default="", help="One of the tags of the task to delete")
delete_parser.add_argument("--delete-tag2", default="", help="One of the tags of the task to delete")
delete_parser.add_argument("--delete-tag3", default="", help="One of the tags of the task to delete")
delete_parser.add_argument("--delete-all", action="store_true", help="Delete all tasks that meet the criteria")
delete_parser.add_argument("--delete-all-but-one", action="store_true", help="Delete all but one of the tasks that meet the criteria")

delete_all_parser = subparsers.add_parser("delete-all-tasks", help="Delete all tasks")
delete_done_parser = subparsers.add_parser("delete-done", help="Delete all completed tasks")
fix_save_parser = subparsers.add_parser("fix-save", help="Wipe the save data and start clean (if the save data is corrupted)")

filter_parser = subparsers.add_parser("filter", help="Filter the tasks")
filter_parser.add_argument("--filter-by-priority", type=int, default=3, help="Filter tasks by a specific minimum priority")
filter_parser.add_argument("--filter-by-tag", default="", help="Filter tasks by a specific tag")
filter_parser.add_argument("--filter-done", action="store_true", help="Include tasks that have been completed")

overview_parser = subparsers.add_parser("overview", help="Get an overview of the tasks")
overview_parser.add_argument("--general-overview", action="store_true", help="Get a general overview of the tasks")
overview_parser.add_argument("--sorted-overview", action="store_true", help="Get a sorted overview of the tasks")
overview_parser.add_argument("--overview-done", action="store_true", help="Include tasks that have been completed")

mark_done_parser = subparsers.add_parser("mark-done", help="Mark a task as done")
mark_done_parser.add_argument("--done-title", required=True, help="Title of the task to be marked as done")
mark_done_parser.add_argument("--done-tag1", default="", help="One of the tags of the task to mark as done")
mark_done_parser.add_argument("--done-tag2", default="", help="One of the tags of the task to mark as done")
mark_done_parser.add_argument("--done-tag3", default="", help="One of the tags of the task to mark as done")
mark_done_parser.add_argument("--mark-all", action="store_true", help="Mark all the tasks that fit the criteria as done")

mark_undone_parser = subparsers.add_parser("mark-undone", help="Mark a task as undone") 
mark_undone_parser.add_argument("--undone-title", required=True, help="Name of the task to mark as undone")
mark_undone_parser.add_argument("--undone-tag1", default="", help="One of the tags of the task to mark as undone")
mark_undone_parser.add_argument("--undone-tag2", default="", help="One of the tags of the task to mark as undone")
mark_undone_parser.add_argument("--undone-tag3", default="", help="One of the tags of the task to mark as undone")
mark_undone_parser.add_argument("--unmark-all", action="store_true", help="Mark all the tasks that fit the criteria as undone")

args = parser.parse_args()

task_manager.default_json_write()

tasks_lst = task_manager.load_tasks() 

show_successful_message = True

if task_manager.load_tasks(show_error=True):
    if args.command == "create":
        create_tags_lst = [args.create_tag1, args.create_tag2, args.create_tag3]
        create_tags_lst = sorted([tag.strip().lower() for tag in create_tags_lst if tag.strip()], key=str.lower)

        task = task_manager.create_task(args.create_title.strip().lower(), args.create_priority, create_tags_lst)

        if args.allow_duplicates:
            tasks_lst.append(task)
        elif not task_manager.is_duplicate_task(tasks_lst, task):
            tasks_lst.append(task)
        elif task_manager.is_duplicate_task(tasks_lst, task):
            show_successful_message = False
            print("\nDuplicate task already exists.")

    if args.command == "filter":
        print("\nFiltered tasks:\n")
        filtered_tasks_list = task_manager.filter_tasks(tasks_lst, args.filter_by_priority, args.filter_by_tag.strip().lower()) if args.filter_by_tag.strip().lower() else task_manager.filter_tasks(tasks_lst, args.filter_by_priority)
        for task in filtered_tasks_list:
            if not task["done"]:
                print(f"[] Task: {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")
            elif args.filter_done and task["done"]:
                print(f"[√] Task: {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")
    if args.command == "overview":
        if args.general_overview or (not args.general_overview and not args.sorted_overview):
            print("\nGeneral overview:\n")
            tasks_lst = sorted(tasks_lst, key=lambda task: task['priority'], reverse=True) 
            for task in tasks_lst:
                if not task["done"]:
                    print(f"[] Task: {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")
                elif args.overview_done and task["done"]:
                    print(f"[√] Task: {task['title']} | Priority: {task['priority']} | Tags: {task['tags']}")

        if args.sorted_overview:
            print("\nSorted overview:")
            grouped_tasks = task_manager.group_tasks_by_tag(tasks_lst)
            for tag, tasks in grouped_tasks.items():
                for task in tasks:
                    if not task["done"]:
                        print(f"\nTag: {tag}")
                        print(f"    Task: {task['title']} | Priority: {task['priority']}")
                    elif args.overview_done and task["done"]:
                        print(f"\nTag: {tag}")
                        print(f"    [√] Task: {task['title']} | Priority: {task['priority']}")

    if args.command == "mark-done":
        done_tags_lst = [args.done_tag1, args.done_tag2, args.done_tag3]
        done_tags_lst = sorted([tag.strip().lower() for tag in done_tags_lst if tag.strip()], key=str.lower)

        if not done_tags_lst:
            tasks_lst = task_manager.mark_tasks(tasks_lst=tasks_lst, task_to_mark=args.done_title.strip().lower(), mark_done=True, mark_all=True) if args.mark_all else task_manager.mark_tasks(tasks_lst=tasks_lst, mark_done=True, task_to_mark=args.done_title.strip().lower(), mark_all=False)
        if done_tags_lst:
            tasks_lst = task_manager.mark_tasks(tasks_lst=tasks_lst, task_to_mark=args.done_title.strip().lower(), mark_done=True, tags=done_tags_lst, mark_all=True) if args.mark_all else task_manager.mark_tasks(tasks_lst=tasks_lst, mark_done=True, task_to_mark=args.done_title.strip().lower(), tags=done_tags_lst, mark_all=False)

    if args.command == "mark-undone":
        undone_tags_lst = [args.undone_tag1, args.undone_tag2, args.undone_tag3]
        undone_tags_lst = sorted([tag.strip().lower() for tag in undone_tags_lst if tag.strip()], key=str.lower)

        if not undone_tags_lst:
            tasks_lst = task_manager.mark_tasks(tasks_lst=tasks_lst, task_to_mark=args.undone_title.strip().lower(), mark_done=False, mark_all=True) if args.unmark_all else task_manager.mark_tasks(tasks_lst=tasks_lst, mark_done=False, task_to_mark=args.undone_title.strip().lower(), mark_all=False)
        if undone_tags_lst:
            tasks_lst = task_manager.mark_tasks(tasks_lst=tasks_lst, task_to_mark=args.undone_title.strip().lower(), mark_done=False, tags=undone_tags_lst, mark_all=True) if args.unmark_all else task_manager.mark_tasks(tasks_lst=tasks_lst, mark_done=False, task_to_mark=args.undone_title.strip().lower(), tags=undone_tags_lst, mark_all=False)

    if args.command == "delete":
        delete_tags_lst = [args.delete_tag1, args.delete_tag2, args.delete_tag3]
        delete_tags_lst = sorted([tag.strip().lower() for tag in delete_tags_lst if tag.strip()], key=str.lower)
        task_to_delete = {"title": args.delete_title.strip().lower(), "tags": delete_tags_lst}

        if args.delete_all and not args.delete_all_but_one:
            if delete_tags_lst:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, True, True)
            else:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, False, True)

        elif args.delete_all_but_one:
            if delete_tags_lst:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, True, False, True)
            else:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, False, False, True)

        else:
            if delete_tags_lst:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, True)
            else:
                tasks_lst = task_manager.delete_task(tasks_lst, task_to_delete, False)

    if args.command == "delete-done":
        tasks_lst = task_manager.delete_finished_task(tasks_lst) 

    if args.command == "delete-all-tasks":
        tasks_lst = []

    if args.command == "fix-save":
        print("\nNo invalid save data. If you want to delete your tasks use the delete (controlled) or the delete-all (delete everything) command instead")
        show_successful_message = False

    task_manager.save_tasks(tasks_lst)

    if show_successful_message:
        print("\nSuccessfully finished operations!")

elif args.command == "fix-save":
    task_manager.default_json_write(write_safety_data=True)
    print("\nDeleted corrupted save data.")

else:
    print("\nOperations may have failed. Use the error message above (if it's there) for more details.")
    print("You can try running fix-save if you suspect corrupted save data (warning: running fix-save will delete virtually every task, so only use it if necessary)")