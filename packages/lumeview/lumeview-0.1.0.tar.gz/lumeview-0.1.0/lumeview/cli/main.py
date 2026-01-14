import click
import asyncio
from rich.console import Console
from rich.status import Status
from lumeview.core.loader import fetch_json_from_url, load_json_from_file
from lumeview.tui.app import LumeApp

console = Console()

@click.group()
@click.version_option(package_name='lumeview')
def cli():
    """Lume - The beautiful JSON viewer CLI."""
    pass

@cli.command()
@click.argument('url')
@click.option('-X', '--method', default='GET', help='HTTP method to use (default: GET)')
@click.option('-H', '--header', multiple=True, help='HTTP headers to include (e.g., -H "Content-Type: application/json")')
@click.option('-d', '--data', help='HTTP request body data (JSON string or raw text)')
@click.option('--timeout', default=120.0, type=float, help='Request timeout in seconds (default: 120)')
@click.option('--display', default='tree', type=click.Choice(['tree', 'box']), help='Display mode: tree or box (default: tree)')
def fetch(url, method, header, data, timeout, display):
    """Fetch JSON from a URL and display it in Lume."""
    import json
    
    # Parse headers
    header_dict = {}
    for h in header:
        if ':' in h:
            k, v = h.split(':', 1)
            header_dict[k.strip()] = v.strip()

    # Parse data as JSON if possible
    payload = data
    if data:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            pass

    async def run():
        with Status(f"[bold #bb86fc]Fetching {method} {url}...[/]", spinner="dots"):
            try:
                data_result = await fetch_json_from_url(
                    url, 
                    method=method.upper(), 
                    headers=header_dict, 
                    data=payload,
                    timeout=timeout
                )
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                return

        app = LumeApp(data=data_result, source_info=f"{method.upper()} {url}", display_mode=display)
        await app.run_async()

    asyncio.run(run())

@cli.command(name='open')
@click.argument('path', type=click.Path(exists=True))
@click.option('--display', default='tree', type=click.Choice(['tree', 'box']), help='Display mode: tree or box (default: tree)')
def open_json(path, display):
    """Open a local JSON file and display it in Lume."""
    with Status(f"[bold #bb86fc]Loading {path}...[/]", spinner="dots"):
        try:
            data = load_json_from_file(path)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return

    app = LumeApp(data=data, source_info=f"File: {path}", display_mode=display)
    app.run()

if __name__ == "__main__":
    cli()
