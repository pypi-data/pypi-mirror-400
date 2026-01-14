from __future__ import annotations
from typing import Callable, Any

from nicegui import Client, ui
from nicegui.events import GenericEventArguments

from dataclasses import dataclass

from ..layout.sortable import SortableRow


@dataclass
class Chip:
    label: str
    icon: str | None = None
    selected: bool = True
    color: str | None = None
    description: str | None = None
    info: dict[str, Any] | None = None

    _parent = None


class ChipElement(ui.row):
    def __init__(self, chips: Chips | None, chip: Chip):
        super().__init__(wrap=False, align_items="center")
        self._chips = chips
        self._chip = chip
        self._build()
        self.refresh()

    @property
    def color(self) -> str:
        color = self._chip.color
        if color is None:
            if self._chips is not None:
                color = self._chips.default_chip_color
            else:
                color = "#444"
        return color

    def refresh(self):
        if self._chip.selected:
            self._style["background-color"] = self.color
        else:
            self._style["background-color"] = None

        self.update()

    def _build(self):
        self.classes("p-[.5em] gap-1")
        with self as r:
            r._style["border-color"] = self.color
            r._style["border-width"] = "1px"
            r._style["border-radius"] = "50vh"
            r.on(
                "click",
                lambda event: self._chips is not None
                and self._chips._on_chip_click(self._chip, event),
            )

            tooltiped = None
            if self._chip.icon:
                self.icon = ui.icon(self._chip.icon, size="xs").props("xsize=1rem")
                tooltiped = self.icon

            if self._chips is not None:
                cursor = self._chips._toggleable and "cursor-pointer" or "cursor-grab"
            else:
                cursor = ""
            label = ui.label(self._chip.label).classes(
                cursor + " text-white opacity-70"
            )

            if self._chip.description:
                with tooltiped or label:
                    with ui.tooltip():
                        ui.markdown(self._chip.description).classes("text-white")


class Chips(ui.element):
    def __init__(
        self,
        chips: list[str] | list[Chip] = [],
        on_order_changed: Callable[[], None] | None = None,
        on_selection_changed: Callable[[], None] | None = None,
        on_click: Callable[[int, bool, bool, bool], None] | None = None,
        default_chip_color: str = "#444",
        toggleable: bool = True,
    ) -> None:
        super().__init__()
        self._on_order_changed = on_order_changed
        self._on_selection_changed = on_selection_changed
        self._on_click = on_click
        self._chips: list[Chip] = []
        self._chip_elems: dict[ChipElement, Chip] = {}
        self._toggleable = toggleable

        self.default_chip_color = default_chip_color
        for chip in chips:
            if not isinstance(chip, Chip):
                chip = Chip(label=chip)
            self._chips.append(chip)

        with self:
            with SortableRow(on_change=self._order_change_handler).classes(
                "gap-1"
            ) as self._root:
                pass

        self._update_chips()

    @property
    def toggleable(self) -> bool:
        return self._toggleable

    def _order_change_handler(
        self, new_index: int, old_index: int, new_list: int, old_list: int
    ):
        if new_list != old_list:
            raise Exception("Transfert drop not supported.")

        # update element order:
        chip = self._root.default_slot.children.pop(old_index)
        self._root.default_slot.children.insert(new_index, chip)
        # udpate chips data order:
        chip = self._chips.pop(old_index)
        self._chips.insert(new_index, chip)

        if self._on_order_changed is not None:
            self._on_order_changed()

    def _selection_change_handler(self):
        if self._on_click is None and self._on_selection_changed is not None:
            self._on_selection_changed()

    def _on_chip_click(self, chip: Chip, event: GenericEventArguments):
        if self._toggleable:
            chip.selected = not chip.selected
            self._refresh_chips()

        if self._on_click is None:
            return

        clicked_index = self._chips.index(chip)

        self._on_click(
            clicked_index,
            event.args["ctrlKey"],
            event.args["shiftKey"],
            event.args["altKey"],
        )

    def _update_chips(self):
        self._root.clear()
        self._chip_elems.clear()
        with self._root:
            for chip in self._chips:
                chip_elem = ChipElement(self, chip)
                self._chip_elems[chip_elem] = chip

    def _refresh_chips(self):
        for chip_elem in self._chip_elems.keys():
            chip_elem.refresh()

    def set_selected(self, *index: int):
        for i, chip in enumerate(self._chips):
            chip.selected = i in index
        self._refresh_chips()

    def get_selected_indexes(self) -> list[int]:
        ret = []
        for i, chip in enumerate(self._chips):
            if chip.selected:
                ret.append(i)
        return ret

    def get_selected(self) -> list[str]:
        ret = []
        for chip in self._chips:
            if chip.selected:
                ret.append(chip.label)
        return ret
