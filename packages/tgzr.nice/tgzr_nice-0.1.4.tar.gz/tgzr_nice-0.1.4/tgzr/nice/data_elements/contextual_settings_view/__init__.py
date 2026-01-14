from __future__ import annotations
from typing import Callable, Any

from nicegui import ui

from tgzr.shell.session import Session, Broker
from tgzr.shell.settings.settings import Settings

from ...tgzr_visid import TGZRVisId
from ...controls.chips import Chips, Chip
from ..dict_tree import TreeView, TreeGroup, TreeValue, _TreeItem, ValueSetter


def dict_table(d) -> ui.grid:
    with ui.grid(columns="auto auto") as grid:
        for k, v in d.items():
            with ui.row():
                ui.label(str(k) + ":")
            with ui.row():
                ui.label(str(v))
                ui.space()
    return grid


class SettingHistory:
    def __init__(self, view: ContextualSettingsView) -> None:
        self._view = view
        self._history_data = {}
        self._current_path: list[str] | None = None
        self._active: bool = True

    @property
    def is_active(self) -> bool:
        return self._active

    def toggle_active(self) -> bool:
        self._active = not self._active
        self.render.refresh()
        return self._active

    def set_history_data(self, history_data):
        self._history_data = history_data
        self.render.refresh()

    def set_path(self, setting_path: list[str] | None):
        self._current_path = setting_path
        self.render.refresh()

    def _on_toggle_history_btn(self):
        self._view.toggle_history()

    @ui.refreshable_method
    def render(self):

        with ui.column().classes("p-1"):
            if not self._active:
                ui.button(
                    icon="arrow_left", on_click=self._on_toggle_history_btn
                ).props("dense outline round").tooltip("Show History")
                return

            ui.button(icon="arrow_right", on_click=self._on_toggle_history_btn).props(
                "dense outline round"
            ).tooltip("Hide History")

            with ui.column().classes("gap-0 w-full"):
                if self._current_path is None:
                    ui.label("Select a value to see its history...")
                    return
                ui.label(".".join(self._current_path[-2:])).classes("text-h5")
                this_history = self._history_data
                for name in self._current_path:
                    this_history = this_history.get(name, None)
                    if this_history is None:
                        break
                if this_history is None:
                    ui.label("No history.")
                elif not isinstance(this_history, list):
                    ui.label("Click a value to see its history...")
                else:
                    with ui.column():
                        ui.label(f"{len(this_history)} operation(s) involved:")
                        with ui.grid(columns="auto auto auto auto").classes(
                            "place-content-center"
                        ):
                            for entry in this_history:
                                self.render_history_entry(entry)

    def render_history_entry(self, entry):
        with ui.row(align_items="center"):
            context_name = entry["context_name"]
            context_info = self._view.get_context_info(context_name)

            icon_name = None
            if entry["override_info"]["pinned"]:
                icon_name = "sym_o_keep"
                icon_tootip = "Value Pinned. It has the same value as the base layer, but will not change if the base changes."
            elif entry["override_info"]["overridden"]:
                icon_name = "sym_o_edit"
                icon_tootip = "Value Modified."
            else:
                icon_name = "sym_o_equal"
                icon_tootip = "Value unchanged from base layer."
            if icon_name is not None:
                ui.icon(icon_name, size="2rem", color="neutral-500").tooltip(
                    icon_tootip
                )

            chip = Chip(
                label=context_name,
                color=context_info.get("color"),
                icon=context_info.get("icon") or "sym_o_layers",
                description=context_info.get("description"),
            )
            Chips(
                [chip],
                toggleable=False,
                default_chip_color=self._view.visid.theme.primary,
            )

        with ui.row(align_items="center"):
            with ui.label(entry["summary"]):
                ui.tooltip(entry["op"])
        with ui.row(align_items="center"):
            ui.label(f'{entry["old_value_repr"]} → {entry["new_value_repr"]}')
        with ui.row(align_items="center"):
            apply_info = entry["apply_info"]
            if apply_info:
                dict_table(apply_info)


class SettingsTree:
    def __init__(self, view: ContextualSettingsView) -> None:
        self._view = view

        self._treeview = TreeView(
            visid=self._view.visid,
            input_renderer=self.input_renderer,
            tools_renderer=self.tools_renderer,
            on_clicked=self._view._on_setting_cliked,
            on_edited=self._on_item_edited,
            on_update_request=self._on_update_request,
            auto_expand_groups=self._view.auto_expand_groups,
        )
        self._root_item: _TreeItem | None = None

    def _on_item_edited(
        self,
        tree_item: _TreeItem,
        op: str,
        op_kwargs: dict[str, Any],
    ):
        self._view.do_settings_cmd(op, tree_item.path, **op_kwargs)

    def request_update(self, key):
        print("Request Update on", key)
        if self._root_item is None:
            return
        affected_item_path = key.split(".")
        self._root_item.request_update(affected_item_path)

    def _on_update_request(self, tree_item: _TreeItem, item_path: list[str]):
        if tree_item.path == item_path:
            print("Updating item", tree_item.path, item_path)
            value = self._view.get_current_setting_value(".".join(item_path))
            tree_item.set_value(value)

    @ui.refreshable_method
    def render(self):
        deep = self._view.get_current_settings()
        update_search: Callable[[str], None] | None = None
        if isinstance(deep, dict):
            found = deep
            ti = TreeGroup(
                self._treeview,
                parent_path=[],
                name=None,
                label=None,
                children=found,
                icon="tune",
                expandable=False,
            )
            ti.expand()

            def _update_search(search):
                found = {}
                for k, v in deep.items():
                    if search and not (search in k or search in str(v)):
                        continue
                    found[k] = v
                ti.set_children(found)

            update_search = _update_search
        else:
            ti = TreeValue(
                self._treeview, parent_path=[], name=None, label=None, value=deep
            )

        with ti.header_slot:
            if self._view.allow_scope_change:
                ui.select(
                    self._view.default_scopes,
                    value=self._view.scope,
                    with_input=True,
                    new_value_mode="add-unique",
                    clearable=True,
                    on_change=lambda e: self._view.set_scope(e.value),
                ).classes("grow py-2").props(
                    'dense rounded standout popup-content-style="font-family: \'Advent Pro\'" popup-content-class="tracking-widest"'
                )
            if update_search is not None:
                ui.input(
                    placeholder="Search", on_change=lambda e: update_search(e.value)
                ).classes("xw-full grow py-2").props("clearable rounded outlined dense")

        self._root_item = ti

    def input_renderer(self, tree_item: _TreeItem) -> ValueSetter:
        value = tree_item.value
        # with ui.row(wrap=False).classes("w-full"):

        # -- SWITCH
        if value in (True, False):
            # NB: we can't use switch(on_change) because it is also triggered
            # by switch.set_value() so when the toggle tool changes the value
            # and the switch.set_value() is called to update the UI, it sends
            # a "set" command :'/
            el = (
                ui.switch(
                    value=value,
                    # on_change=lambda e: tree_item.on_edited("set", value=e.value),
                )
                .on(
                    "click",
                    lambda e: tree_item.on_edited("set", value=e.sender.value),  # type: ignore
                )
                .props("dense rounded standout")
                .classes("w-full h-[3em]")
            )
            return el.set_value

        # -- LIST EDITOR
        if isinstance(value, list):

            @ui.refreshable
            def render_items(value):
                # expansion.open()
                try:
                    expansion.set_text(", ".join(str(i) for i in value))
                except Exception as err:
                    # This can happen if the value is not a list anymore after some edits :/
                    expansion.set_text(f"!!! ERROR: {err}")
                    return
                # expansion.clear()
                with ui.column().classes("gap-1 w-full"):
                    for i, v in enumerate(value):

                        def on_item_key(e, i=i):
                            if e.args["key"] == "Enter":
                                tree_item.on_edited(
                                    "set_item", index=i, item_value=e.sender.value
                                )

                        with ui.row(wrap=False, align_items="center").classes(
                            "w-full gap-0"
                        ):
                            ui.input(value=v).props("dense rounded standout").classes(
                                "w-full"
                            ).on("keydown", on_item_key)
                            ui.button(
                                icon="sym_o_close_small",
                                on_click=lambda e, v=v: tree_item.on_edited(
                                    "remove", item=v
                                ),
                            ).props("flat round").tooltip(f'Remove "{v}"')
                            ui.button(
                                icon="sym_o_playlist_remove",
                                on_click=lambda e, i=i: tree_item.on_edited(
                                    "del_item", index=i
                                ),
                            ).props("flat round").tooltip(f"Remove item #{i+1}")
                    with ui.row(wrap=False, align_items="center").classes(
                        "w-full gap-0"
                    ):
                        # ui.space().classes("w-full")
                        ui.button(
                            icon="sym_o_add",
                            on_click=lambda: tree_item.on_edited("add", value=[""]),
                        ).props("flat rounded").classes("w-full").tooltip(
                            "Add an entry"
                        )
                        if 0:
                            # FIXME: implement the 'clear' operation
                            ui.button(
                                icon="sym_o_delete",
                                on_click=lambda: tree_item.on_edited("clear"),
                            ).props("flat round").tooltip("Clear list")

            with ui.expansion().classes("w-full gap-0 p-0").props(
                'dense xlabel-lines=1 content-inset-level=1 header-class="bg-neutral-700 rounded-full min-h-[3em]"'
            ) as expansion:
                render_items(value)
            return render_items.refresh  # pyright: ignore[reportReturnType]

        # -- STR EDITOR
        else:

            def on_key(event):
                if event.args["key"] == "Enter":
                    tree_item.on_edited("set", value=event.sender.value)

            el = (
                ui.input(value=str(value))
                .props("dense rounded standout")
                .classes("w-full")
                .on("keydown", on_key)
            )
            return el.set_value

    def tools_renderer(self, tree_item: _TreeItem):
        value = tree_item.value
        if value in (True, False):

            def toggle():
                tree_item.on_edited("toggle")

            ui.button(icon="swap_horizontal_circle", on_click=toggle).props(
                "flat dense"
            ).tooltip("Toggle")
        elif isinstance(value, list):
            # every tool is provided by the input renderer
            pass
        else:
            pass


class ContextChips:
    def __init__(
        self, view: ContextualSettingsView, on_changed: Callable[[], None]
    ) -> None:
        self._view = view
        self._chips_collection: Chips | None = None
        self._on_changed = on_changed

    @ui.refreshable_method
    def render(self):
        all_context_names = self._view._settings_context

        context_chips = []
        for context_name in all_context_names:
            context_info = self._view.get_context_info(context_name)
            expanded_context_names = self._view.settings.expand_context_name(
                context_name
            )
            context_info["expanded_context_names"] = expanded_context_names

            description = context_info.get("description", "")
            if description:
                description += "\n\n----\n\n"
            if expanded_context_names and expanded_context_names != [context_name]:
                description += "Context name expanded to:\n\n"
                for cn in expanded_context_names:
                    description += f"- **{cn}**\n"
                description += "\n\n----\n\n"
            description += "Left Mouse Button:\n\n"
            description += "- Alone: Toggle this one.\n"
            description += "- +Ctrl:  Toggle only this one / all up to this one.\n"
            description += "- +Ctrl+Alt: Use all up to this one.\n"

            context_chips.append(
                Chip(
                    label=context_name,
                    icon=context_info.get("icon") or "sym_o_layers",
                    color=context_info.get("color"),
                    selected=True,
                    description=description,
                    info=context_info,
                )
            )

        self._chips_collection = Chips(
            context_chips,
            on_order_changed=self._on_order_change,
            on_click=self._on_chip_click,
            default_chip_color=self._view.visid.theme.primary,
        )

    def _on_order_change(self):
        # TODO: detect if selected order has changed? ¯\_(ツ)_/¯
        self._on_changed()

    def _on_chip_click(self, index: int, ctrl: bool, shift: bool, alt: bool):
        if self._chips_collection is None:
            # This cannot happen, but mypy wants that.
            return

        before = self._chips_collection.get_selected_indexes()
        if not (ctrl or shift or alt):
            # normal selection is already done
            selected = before
        elif ctrl and not (shift or alt):
            if not before:
                selected = range(index + 1)
            else:
                selected = [index]
        elif ctrl and (shift or alt):
            selected = range(index + 1)
        else:
            return

        self._chips_collection.set_selected(*selected)
        self._on_changed()

    def get_selected(self) -> list[str]:
        if self._chips_collection is None:
            return []
        return self._chips_collection.get_selected()


class ContextualSettingsView(ui.element):
    def __init__(
        self,
        settings_context: list[str],
        session: Session,
        visid: TGZRVisId,
        scope: str | None = None,
        allow_scope_change: bool = True,
        history_closed: bool = True,
        auto_expand_groups: bool = True,
    ) -> None:
        super().__init__()
        self._default_scopes = {
            None: None,  # "- Show All -",
            "session": "session",
            "studios": "studios",
            "shell_apps": "shell_apps",
            "project": "project",
        }
        self._scope: str | None = scope
        if self._scope not in self._default_scopes:
            self._default_scopes[self._scope] = "Default"
        self.allow_scope_change = allow_scope_change

        self._settings_context = settings_context

        self._visid = visid
        self._session = session

        self.auto_expand_groups = auto_expand_groups

        self._settings_tree = SettingsTree(self)
        self._history_panel = SettingHistory(self)

        self._splitter: ui.splitter | None = None
        self._context_chips = ContextChips(
            self,
            on_changed=self._settings_tree.render.refresh,  # type: ignore
        )

        if history_closed:
            self.toggle_history()

        self._session.broker.subscribe(
            "session.settings.changed", self._on_settings_changed_event
        )

    @property
    def visid(self) -> TGZRVisId:
        return self._visid

    @property
    def session(self) -> Session:
        return self._session

    @property
    def settings(self) -> Settings:
        return self._session.settings

    def current_context(self) -> list[str]:
        return self._context_chips.get_selected()

    def get_context_info(self, context_name: str) -> dict[str, Any]:
        return self._session.settings.get_context_info(context_name)

    def get_current_settings(self):
        context = self.current_context()
        key = self._scope  # TODO: use breadcrumbs ?
        with_history = self._history_panel.is_active
        deep = self._session.settings.get_deep(
            context,
            key=key,
            with_history=with_history,
        )

        if with_history:
            try:
                history_data = deep.pop("__history__", {})
            except AttributeError:
                # deep is not a dict, it may contain a single value
                # FIXME: we should have history even if key leads to a single value!
                self._history_panel.set_history_data({})
            else:
                self._history_panel.set_history_data(history_data)
        return deep

    def get_current_setting_value(self, key) -> Any:
        context = self.current_context()
        flat = self._session.settings.get_flat(context, key)
        return flat[""]

    def _update_splitter(self, open: bool):
        if self._splitter is None:
            return
        if open:
            self._splitter.value = 50
        else:
            self._splitter.value = 95

    def toggle_history(self):
        is_active = self._history_panel.toggle_active()
        self._update_splitter(is_active)

    @ui.refreshable_method
    def render(self):
        with self:
            with ui.row(align_items="center").classes("w-full p-3"):
                self._context_chips.render()

            def on_splitter_change(e):
                if e.value in (50, 95):  # This is ugly AF !!!! (っ- ‸ - ς)
                    return
                if e.value > 98:  # This is ugly too (つ.と)
                    e.sender.value = 95
                    if self._history_panel.is_active:
                        self._history_panel.toggle_active()
                elif not self._history_panel.is_active:
                    self._history_panel.toggle_active()

            with ui.splitter(value=50, on_change=on_splitter_change).classes(
                "w-full gap-4"
            ) as self._splitter:
                with self._splitter.before:
                    self._settings_tree.render()
                with self._splitter.after:
                    self._history_panel.render()
                self._update_splitter(self._history_panel.is_active)

    def _on_setting_cliked(self, tree_item: _TreeItem):
        self._history_panel.set_path(tree_item.path)

    @property
    def default_scopes(self) -> dict[str, str]:
        return self._default_scopes

    @property
    def scope(self) -> str | None:
        return self._scope

    def set_scope(self, new_scope: str):
        self._scope = new_scope
        self._history_panel.set_path(None)
        self._settings_tree.render.refresh()  # type: ignore

    def do_settings_cmd(self, op: str, tree_item_path: list[str], **op_kwargs: Any):
        key = ".".join(tree_item_path)
        if self.scope:
            key = self.scope + "." + key
        context_name = self._context_chips.get_selected()[-1]
        self._session.broker.cmd(
            cmd_name="session.settings.edit",
            op=op,
            key=key,
            context_name=context_name,
            **op_kwargs,
        )

    def _on_settings_changed_event(self, event: Broker.Event):
        context_name, key, more = event.unpack("context_name", "key")
        if more:
            raise Exception("Unknown extra data in settings changed event:", more)
        if context_name not in self.current_context():
            print(
                f"Settings Changed Event skipped because context name is not active: {context_name=}"
            )
            return
        self._settings_tree.request_update(key)
