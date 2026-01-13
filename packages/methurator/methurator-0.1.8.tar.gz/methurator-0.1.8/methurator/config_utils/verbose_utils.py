from rich.console import Console

console = Console()


def vprint(msg, verbose=False):
    if verbose:
        console.print(msg)
