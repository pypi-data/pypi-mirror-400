import inquirer
from rich.console import Console  # type: ignore

console = Console()


def info(text: str):
    console.print(f'[bold]ℹ︎[/bold] {text}', soft_wrap=True)


def succeed(text: str):
    console.print(f'[green]✔[/green] {text}', soft_wrap=True)


def fail(text: str):
    console.print(f'[red]⨯[/red] {text}', soft_wrap=True)


def read_input(message: str, choices: list[str] | None = None, default: str | None = None) -> str | None:
    if choices:
        questions = [
            inquirer.List('name', message, choices)
        ]
    else:
        questions = [
            inquirer.Text('name', message, default)
        ]
    answer = inquirer.prompt(questions)
    if not answer:
        return None
    value = answer['name']
    if value == '':
        return default if default is not None else None
    return value
