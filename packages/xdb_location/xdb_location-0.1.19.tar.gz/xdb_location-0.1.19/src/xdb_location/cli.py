"""Console script for xdb_location."""

import typer
from rich.console import Console

from xdb_location import utils

app = typer.Typer()
console = Console()


@app.command()
def main(src: str,dst: str):
    """Console script for xdb_location."""
    # console.print("Replace this message by putting your code into "
    #            "xdb_location.cli.main")
    # console.print("See Typer documentation at https://typer.tiangolo.com/")
    # utils.do_something_useful()
    utils.gen_db(src,dst)



if __name__ == "__main__":
    app()
