from typing import Callable

from nicegui import ui


class BoxSelector(ui.element, component="box_selector.js"):
    """
    A container that enables box selection over its children.
    Renders a canvas overlay for drawing the selection box.
    """

    def __init__(self):
        """
        Create a box selector container.

        Usage:
            with BoxSelector() as selector:
                selector.on_box_selected(my_callback)
                # Add your content here
                ui.label('Some content')

        Controls:
            - Shift + Drag to draw selection box
        """
        super().__init__()
        self.on("box_selected", self._handle_box_selected)
        self._box_selected_callbacks = []

    async def _handle_box_selected(self, e):
        """Internal handler"""
        for callback in self._box_selected_callbacks:
            await callback(e)

    def on_box_selected(self, callback: Callable):
        """
        Register a callback for box selection events.

        Args:
            callback: Function that receives event with args {x, y, width, height}

        Returns:
            self for chaining
        """
        self._box_selected_callbacks.append(callback)
        return self
