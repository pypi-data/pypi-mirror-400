from typing import Callable, Optional, Literal
from nicegui import ui


class _Sortable(ui.element, component="sortable.js"):
    _COLUMN = False
    sortable_list = {}

    def __init__(
        self,
        *,
        on_change: Callable[[int, int, int, int], None] | None = None,
        group: str | None = None,
        wrap: bool = True,
        align_items: Optional[
            Literal["start", "end", "center", "baseline", "stretch"]
        ] = None,
    ) -> None:
        super().__init__()
        self.on("item-drop", self.drop)
        self.on_change = on_change

        if self._COLUMN:
            self.classes(add="nicegui-column")
        else:
            # NOTE: "row" is for compatibility with Quasar's col-* classes
            self.classes(add="row nicegui-row")

        if align_items:
            self._classes.append(f"items-{align_items}")

        if not wrap:
            self._style["flex-wrap"] = "nowrap"

        self._props["group"] = group
        _Sortable.sortable_list[self.id] = self

    def drop(self, e) -> None:
        if self.on_change:
            self.on_change(
                e.args["new_index"],
                e.args["old_index"],
                _Sortable.sortable_list[e.args["new_list"]],
                _Sortable.sortable_list[e.args["old_list"]],
            )
        else:
            print("No on_change handler", e.args)

    def makeSortable(self) -> None:
        self.run_method("makesortable")


class SortableColumn(_Sortable):
    _COLUMN = True


class SortableRow(_Sortable):
    _COLUMN = False
