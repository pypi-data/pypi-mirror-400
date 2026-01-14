from textual.widgets import Static
from textual.containers import VerticalScroll
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
from typing import Any

class BoxView(VerticalScroll):
    """An elegant box-like view for JSON data."""
    
    def update_data(self, data: Any) -> None:
        self.query("Static").remove()
        
        if isinstance(data, list):
            for index, item in enumerate(data):
                content = JSON.from_data(item)
                panel = Panel(
                    content,
                    title=f"[bold #bb86fc]Entry #{index}[/]",
                    border_style="#3700b3",
                    padding=(1, 2)
                )
                self.mount(Static(panel, classes="data-card"))
        elif isinstance(data, dict):
            # Summary Table
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Key", style="bold #bb86fc")
            table.add_column("Value")
            
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    val = "[italic]Complex Object[/]"
                else:
                    val = f"[green]{repr(v)}[/]"
                table.add_row(k, val)
                
            main_panel = Panel(
                table,
                title="[bold #bb86fc]Object Summary[/]",
                border_style="#3700b3",
                padding=(1, 2)
            )
            self.mount(Static(main_panel, classes="data-card"))
            
            # Detailed Boxes
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    self.mount(Static(Panel(
                        JSON.from_data(v),
                        title=f"[bold #bb86fc]{k}[/]",
                        border_style="#3700b3",
                        padding=(1, 2)
                    ), classes="data-card"))
        else:
            self.mount(Static(Panel(repr(data), title="Value", border_style="#3700b3")))
