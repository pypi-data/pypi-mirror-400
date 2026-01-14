from textual.app import ComposeResult
from textual.widgets import Tree, Static
from textual.containers import VerticalScroll
from rich.json import JSON
from typing import Any

class JsonTree(Tree):
    """A tree widget that represents a JSON structure."""
    
    def populate(self, data: Any) -> None:
        self.clear()
        self.root.label = "Lume Root"
        self.root.data = data
        self._add_json_node(self.root, data)
        self.root.expand()

    def _add_json_node(self, node, data: Any) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                child = node.add(f"[bold #bb86fc]{key}[/]", data=value)
                if isinstance(value, (dict, list)):
                    self._add_json_node(child, value)
                else:
                    child.label = f"[bold #bb86fc]{key}[/]: [green]{repr(value)}[/]"
        elif isinstance(data, list):
            for index, value in enumerate(data):
                child = node.add(f"[yellow][{index}][/]", data=value)
                if isinstance(value, (dict, list)):
                    self._add_json_node(child, value)
                else:
                    child.label = f"[yellow][{index}][/]: [green]{repr(value)}[/]"

class DetailsPanel(VerticalScroll):
    """Panel for displaying pretty-printed JSON details."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = Static()

    def compose(self) -> ComposeResult:
        yield self.content

    def update_content(self, data: Any) -> None:
        if data is None:
            self.content.update("[italic gray]Select a node to view details[/]")
        else:
            self.content.update(JSON.from_data(data))
