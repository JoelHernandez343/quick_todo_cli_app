import os
import click
import re
from colorama import init, Fore

init(autoreset=True)

TasksDict = list[tuple[str, list[str]]]

tasks: TasksDict = []
message_buffer: str = ""
show_commands: bool = False

delete_pattern = re.compile(r"^d\s+(\d+)(?:\.(?:(\d+|all)))?$")
add_subtask_pattern = re.compile(r"^(\d+)\s+(.+)$")
commands_pattern = re.compile(r"^help\s*(off)?$")
edit_pattern = re.compile(r"^e\s+(\d+)(?:\.(\d+))?\s+(.+)$")

commands_message = (
    Fore.LIGHTBLACK_EX
    + "\nCommands: "
    + "\n- clear to empty tasks"
    + "\n- help (off) to show or hide this info"
    + "\n- <number> <subtask> to add a subtask"
    + "\n- e <number> to edit a task"
    + "\n- e <number>.<subnumber> to edit a subtask"
    + "\n- d <number> to delete a task"
    + "\n- d <number>.<subnumber|all> to delete a subtask or all"
)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def display_tasks() -> None:
    global message_buffer

    if not tasks:
        print(Fore.LIGHTBLACK_EX + "No tasks.")
    else:
        print(Fore.CYAN + "Quick TODO list:")
        for i, (task, subtasks) in enumerate(tasks, 1):
            print(f"{Fore.GREEN}{i}. {Fore.WHITE}{task}")
            for j, subtask in enumerate(subtasks, 1):
                print(f"{Fore.GREEN}   {i}.{j} {Fore.WHITE}{subtask}")
    print()

    if message_buffer:
        print(message_buffer)
        message_buffer = ""  # Clear the buffer after displaying
        print()


def add_task(task: str) -> None:
    tasks.append((task, []))


def add_subtask(task_index: int, subtask: str) -> None:
    global message_buffer
    if 1 <= task_index <= len(tasks):
        (task, subtasks) = tasks[task_index - 1]
        subtasks.append(subtask)
    else:
        message_buffer = (
            Fore.RED + f"Task {task_index} does not exist, subtask couldn't be added."
        )


def delete_all_tasks() -> None:
    global tasks
    tasks = []
    message_buffer = Fore.RED + f"Deleted all tasks"


def delete_task(task_index: int) -> None:
    global message_buffer

    if 1 <= task_index <= len(tasks):
        (deleted_task, _) = tasks.pop(task_index - 1)
        message_buffer = Fore.RED + f"Deleted task: {deleted_task}"

    else:
        message_buffer = Fore.RED + f"Invalid task number: {task_index}"


def delete_subtask(task_index: int, subtask_index: int | str) -> None:
    global message_buffer

    if 1 <= task_index <= len(tasks):
        (task, subtasks) = tasks[task_index - 1]

        if subtask_index == "all":
            tasks[task_index - 1] = (task, [])
            message_buffer = Fore.RED + f"Deleted all subtasks for task: {task}"

        elif isinstance(subtask_index, int) and 1 <= subtask_index <= len(subtasks):
            deleted_subtask = subtasks.pop(subtask_index - 1)
            message_buffer = Fore.RED + f"Deleted subtask: {deleted_subtask}"

        else:
            message_buffer = (
                Fore.RED
                + f"For task {task_index}, invalid subtask number: {subtask_index}"
            )
    else:
        message_buffer = Fore.RED + f"Invalid task number: {task_index}"


def edit_task(task_index: int, new_task: str) -> None:
    global message_buffer

    if 1 <= task_index <= len(tasks):
        (old_task, subtasks) = tasks[task_index - 1]
        tasks[task_index - 1] = (new_task, subtasks)
        message_buffer = Fore.BLUE + f"Edited task: '{old_task}' to '{new_task}'"

    else:
        message_buffer = Fore.RED + "Invalid task number."


def edit_subtask(task_index: int, subtask_index: int, new_subtask: str) -> None:
    global message_buffer

    if 1 <= task_index <= len(tasks):
        (task, subtasks) = tasks[task_index - 1]

        if 1 <= subtask_index <= len(subtasks):
            old_subtask = subtasks[subtask_index - 1]
            subtasks[subtask_index - 1] = new_subtask
            message_buffer = (
                Fore.BLUE + f"Edited subtask: '{old_subtask}' to '{new_subtask}'"
            )

        else:
            message_buffer = (
                Fore.RED
                + f"For task {task_index}, invalid subtask number: {subtask_index}"
            )

    else:
        message_buffer = Fore.RED + f"Invalid task number: {task_index}"


def parse_indexes(
    matches: list[str | None], accept_all=False
) -> list[int | str | None]:
    return [
        m if m == "all" and accept_all else int(m) if m and m.isdecimal() else None
        for m in matches
    ]


def prompt() -> str:
    prompt = Fore.YELLOW + "Start typing to add a task (or type help)"

    if show_commands:
        prompt += commands_message

    print(prompt)

    return click.prompt("")


@click.command()
def todo_app() -> None:
    global show_commands
    global message_buffer

    while True:
        clear_screen()
        display_tasks()

        user_input = prompt().strip()

        delete_match = delete_pattern.match(user_input.lower())
        subtask_match = add_subtask_pattern.match(user_input)
        commands_match = commands_pattern.match(user_input)
        edit_match = edit_pattern.match(user_input)

        if user_input == "clear":
            delete_all_tasks()

        elif delete_match:
            (task_index, subtask_index) = parse_indexes(
                [delete_match.group(1), delete_match.group(2)], accept_all=True
            )

            if subtask_index:
                delete_subtask(task_index, subtask_index)
            else:
                delete_task(task_index)

        elif edit_match:
            (task_index, subtask_index) = parse_indexes(
                [edit_match.group(1), edit_match.group(2)]
            )
            new_content: str = edit_match.group(3)

            if subtask_index:
                edit_subtask(task_index, int(subtask_index), new_content)
            else:
                edit_task(task_index, new_content)

        elif subtask_match:
            task_index: int = int(subtask_match.group(1))
            subtask: str = subtask_match.group(2)
            add_subtask(task_index, subtask)

        elif commands_match:
            switch = commands_match.group(1)
            show_commands = switch != "off"

        elif user_input:
            add_task(user_input)


if __name__ == "__main__":
    todo_app()
