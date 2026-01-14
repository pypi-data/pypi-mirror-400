from typing import Callable
from itertools import zip_longest
from dataclasses import dataclass

from nicegui import Client, ui

# TODO: clean all this mess up. clear the shame '^_^


@dataclass
class Crumb:
    label: str
    icon: str | None = None
    cursor: str | None = None


class breadcrumbs(ui.element):
    def __init__(
        self,
        crumbs: list[str | Crumb] | None = None,
        on_changed: Callable[[list[str]], None] | None = None,
        on_crumb_click: Callable[[list[str]], None] | None = None,
        on_add_click: Callable[[list[str]], str | Crumb] | None = None,
        default_icon: str | None = None,
        default_cursor: str = "cursor-pointer",
        tag: str | None = None,
        *,
        _client: Client | None = None,
    ) -> None:
        super().__init__(tag, _client=_client)
        self._default_cursor = default_cursor
        self._default_icon = default_icon

        self._crumbs: list[Crumb] = []
        self._element_to_crumb: dict[ui.element, Crumb] = {}
        self._crumbs_value: dict[ui.element, list[str]] = {}

        self._on_crumb_click = on_crumb_click
        self._on_add_click = on_add_click
        self._on_changed = None

        self._root = self._build()
        if crumbs is not None:
            self.set_crumbs(crumbs)

        # Need to set this one after self.set_crumbs !
        self._on_changed = on_changed

    def _build(self) -> ui.element:
        with self:
            with ui.row(align_items="center"):  # .classes("w-full"):
                with ui.element("q-breadcrumbs") as root:
                    pass
                if self._on_add_click:
                    ui.button(">", on_click=self._add_click_handler).props(
                        "size=md dense"
                    )
        return root

    def _call_on_changed(self):
        if self._on_changed:
            self._on_changed(self.get_path())

    def _add_click_handler(self):
        if self._on_add_click is None:
            return
        path = self.get_path()
        to_add = self._on_add_click(path)
        if not isinstance(to_add, Crumb):
            to_add = Crumb(label=to_add)
        self._crumbs.append(to_add)
        self.update_crumbs()
        self._call_on_changed()

    def _crumb_click_handler(self, event):
        if self._on_crumb_click:
            clicked_value = self._crumbs_value[event.sender]
            self._on_crumb_click(clicked_value)
        else:
            clicked_crumb = self._element_to_crumb[event.sender]
            new_crumbs = []
            for c in self._crumbs:
                new_crumbs.append(c)
                if c == clicked_crumb:
                    break
            self._crumbs = new_crumbs
            self.update_crumbs()
            self._call_on_changed()

    def update_crumbs(self):
        self._root.clear()
        self._element_to_crumb.clear()
        self._crumbs_value.clear()
        with self._root:
            current = []
            for crumb in self._crumbs:
                current.append(crumb.label)
                icon_props = ""

                icon = crumb.icon or self._default_icon
                if icon:
                    icon_props = f" icon={icon}"

                cursor = crumb.cursor or self._default_cursor
                el = (
                    ui.element("q-breadcrumbs-el")
                    .props(f'label="{crumb.label}"{icon_props}')
                    .classes(add=cursor)
                    .on("click", self._crumb_click_handler)
                )
                self._element_to_crumb[el] = crumb
                self._crumbs_value[el] = list(current)

    def set_crumbs(self, crumbs: list[str | Crumb]) -> None:
        self._crumbs.clear()
        for c in crumbs:
            if not isinstance(c, Crumb):
                c = Crumb(label=c)
                self._crumbs.append(c)
        self.update_crumbs()
        self._call_on_changed()

    def crumb(self, index: int) -> Crumb:
        return self._crumbs[index]

    def get_path(self) -> list[str]:
        if not self._crumbs:
            last_value = []
        else:
            last_value = self._crumbs_value[list(self._root)[-1]]
        return last_value

    def set_icons(
        self,
        first: str | None = None,
        last: str | None = None,
        *others: str,
    ):
        crumbs = list(self._crumbs)
        if not crumbs:
            return

        if first:
            crumbs.pop(0).icon = first

        if last and crumbs:
            crumbs.pop(-1).icon = last

        if others:
            for c, i in zip_longest(crumbs, others, fillvalue=None):
                if c is None:
                    break
                c.icon = i or others[0]

        self.update_crumbs()
