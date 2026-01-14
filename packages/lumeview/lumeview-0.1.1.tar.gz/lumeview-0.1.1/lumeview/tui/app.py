from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Header, Footer, Tree
from textual.containers import Horizontal, VerticalScroll
from typing import Any

from lumeview.tui.tree_display import JsonTree, DetailsPanel
from lumeview.tui.box_display import BoxView

class LumeApp(App):
    """The main Lume TUI Application."""
    
    TITLE = "LUME"
    
    CSS = """
    Screen {
        background: #120b18;
        color: #e0e0e0;
    }

    Header {
        background: #1e1329;
        color: #bb86fc;
        text-style: bold;
    }

    Footer {
        background: #1e1329;
        color: #bb86fc;
    }

    /* Tree View Styles */
    JsonTree {
        width: 35%;
        height: 100%;
        border-right: tall #3700b3;
        background: #120b18;
    }

    #details-container {
        width: 65%;
        height: 100%;
        padding: 1 2;
        background: #120b18;
    }

    .tree--cursor {
        background: #3700b3;
        color: #ffffff;
    }

    /* Box View Styles */
    BoxView {
        width: 100%;
        height: 100%;
        padding: 1 2;
        background: #120b18;
    }

    .data-card {
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, data: Any = None, source_info: str = "", display_mode: str = "tree"):
        super().__init__()
        self.initial_data = data
        self.source_info = source_info
        self.display_mode = display_mode

    def compose(self) -> ComposeResult:
        yield Header()
        if self.display_mode == "box":
            yield BoxView(id="box-view")
        else:
            with Horizontal():
                yield JsonTree("Root", id="json-tree")
                with VerticalScroll(id="details-container"):
                    yield DetailsPanel(id="details-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.source_info
        if self.initial_data is not None:
            if self.display_mode == "box":
                self.query_one(BoxView).update_data(self.initial_data)
            else:
                self.query_one(JsonTree).populate(self.initial_data)

    @on(Tree.NodeSelected)
    def show_node_details(self, event: Tree.NodeSelected) -> None:
        if self.display_mode == "tree":
            details = self.query_one(DetailsPanel)
            details.update_content(event.node.data)

    def action_refresh(self) -> None:
        self.notify("Refresh requested", title="Lume")
