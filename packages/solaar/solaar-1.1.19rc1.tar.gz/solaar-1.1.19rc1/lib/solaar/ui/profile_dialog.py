## Copyright (C) Solaar Contributors
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

## Dialog Window to show, edit, load, store, read, and write new-style profiles
## The window shows a tree view of a profile and allows editing it
## The profile can be read from a device or written to a device
## The profile can be loaded from the Solaar profiles configuration or saved to it
## The profile can be edited,
## - changing the profile name
## - adding new fields
## - editing a field
## The profile can be a generic one or specialized for a particular on-line device
## - specializing to a device adds the device model id to the profile name

# import abc
import copy
import dataclasses
import logging
import os

from contextlib import contextmanager as contextlib_contextmanager
from enum import Enum
from typing import Any

from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk
from logitech_receiver import profile

from solaar.i18n import _

logger = logging.getLogger(__name__)

_profile_dialog = None
_XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser(os.path.join("~", ".config"))
_profile_file_path = os.path.join(_XDG_CONFIG_HOME, "solaar", "profiles.yaml")
_saved_profiles = None
_saved_profiles_dialog = None
_device_profiles_dialogs = {}
_profile_component_clipboard = None


class GtkSignal(Enum):
    ACTIVATE = "activate"
    BUTTON_RELEASE_EVENT = "button-release-event"
    CHANGED = "changed"
    CLICKED = "clicked"
    DELETE_EVENT = "delete-event"
    KEY_PRESS_EVENT = "key-press-event"
    NOTIFY_ACTIVE = "notify::active"
    TOGGLED = "toggled"
    VALUE_CHANGED = "value_changed"


# holds the information needed to show and edit a profile or a part of a profile
class BaseUI:
    widgets = None

    def __init__(self, component, dialog):
        print("UI Init", self, component, dialog)
        self.component = component  # normally the thing that is being edited
        self.dialog = dialog  # to use in signal handlers
        self._ignore_changes = 0
        self.create_widgets()

    def _populate_model(self, dialog, model, it, pos=-1):
        wrapped = ProfileComponentWrapper(self, True)
        return model.insert(it, pos, (wrapped,))

    def show(self, panel, editable=True):
        self.show_widgets(panel, editable)

    def show_widgets(self, panel, editable):
        for c in panel.get_children():
            panel.remove(c)
        if self.widgets is not None:
            for widget, coord in self.widgets.items():
                panel.attach(widget, *coord)
                widget.set_sensitive(True)
                widget.show()

    def create_widgets(self):
        pass

    def _on_update(self, *args):
        print("ON _UPDATE", self.field.get_text())
        if not self._ignore_changes:
            self.on_update(args)
            self.dialog.on_update()
            return True
        return None

    @contextlib_contextmanager
    def ignore_changes(self):
        self._ignore_changes += 1
        yield None
        self._ignore_changes -= 1

    def left_label(self) -> str:
        return type(self.component).__name__

    def right_label(self) -> str:
        return ""

    @classmethod
    def icon_name(cls) -> str:
        return "format-justify-fill"


class ProfileUI(BaseUI):
    CLASS = profile.Profile

    def _populate_model(self, dialog, model, it, pos=-1):
        print("PM Profile", self, model, it, pos, getattr(self.component, "Name", None))
        wrapped = ProfileComponentWrapper(self, False)
        it = model.insert(it, pos, (wrapped,))
        for attribute_name, ui_class in FIELD_UI_CLASSES.items():
            value = getattr(self.component, attribute_name, None)
            if value is not None:
                ui_class(value, dialog)._populate_model(dialog, model, it)
        return it

    def left_label(self) -> str:
        if hasattr(self.component, "ID"):
            return type(self.component).__name__ + " #" + str(self.component.ID.id)
        else:
            return type(self.component).__name__

    def right_label(self) -> str:
        return ""

    @classmethod
    def icon_name(cls):
        return "format-justify-fill"


class FieldUI(BaseUI):
    pass


class NameUI(FieldUI):
    CLASS = profile.Name

    def create_widgets(self):
        self.widgets = {}
        self.label = Gtk.Label(valign=Gtk.Align.CENTER, hexpand=True)
        self.label.set_text(_("Profile name (maximum 63 characters)."))
        self.widgets[self.label] = (0, 0, 1, 1)
        self.field = Gtk.Entry(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, hexpand=True)
        self.field.connect(GtkSignal.CHANGED.value, self._on_update)
        self.field.set_size_request(600, 0)
        self.widgets[self.field] = (0, 1, 1, 1)

    def on_update(self, *args):
        self.component.name = self.field.get_text()[:63]

    def show(self, panel, editable=True):
        super().show(panel, editable)
        with self.ignore_changes():
            self.field.set_text(self.component.name)

    def right_label(self) -> str:
        return self.component.name

    @classmethod
    def icon_name(cls):
        return "text-x-preview"


class IndexUI(FieldUI):
    CLASS = profile.Index

    def create_widgets(self):
        self.widgets = {}
        self.label = Gtk.Label(valign=Gtk.Align.CENTER, hexpand=True)
        self.label.set_text(_("Profile device index, min 1, max 254."))
        self.widgets[self.label] = (0, 0, 1, 1)
        self.field = Gtk.SpinButton(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, hexpand=True)
        self.field.set_adjustment(Gtk.Adjustment(lower=1, upper=254, step_increment=1))
        self.field.connect(GtkSignal.CHANGED.value, self._on_update)
        self.field.set_size_request(100, 0)
        self.widgets[self.field] = (0, 1, 1, 1)

    def on_update(self, *args):
        try:
            index = max(1, min(254, int(self.field.get_text())))
            self.component.index = index
            self.field.set_value(index)
        except Exception:
            self.field.set_value(self.component.index)

    def show(self, panel, editable=True):
        super().show(panel, editable)
        with self.ignore_changes():
            self.field.set_value(self.component.index)

    def right_label(self) -> str:
        return str(self.component.index)

    @classmethod
    def icon_name(cls):
        return "text-x-preview"


class KeyMappingUI(FieldUI):
    CLASS = profile.KeyMapping

    def _populate_model(self, dialog, model, it, pos=-1):
        print("PM KeyMapping", self, model, it, self.component)
        print("PM KeyMapping", self, model, it, self.component, self.component.keys)
        kit = super()._populate_model(dialog, model, it, pos)
        for key, mapped in self.component.keys.items():
            print("KEY", key, mapped, type(mapped))
            ui = KEY_UI_CLASSES.get(type(mapped))(key, self.component.keys, dialog)
            ui._populate_model(dialog, model, kit)
        return kit

    @classmethod
    def icon_name(cls) -> str:
        return "folder"


class FnKeyMappingUI(KeyMappingUI):
    CLASS = profile.FnKeyMapping


FIELD_UI_CLASSES = {
    profile.Tag.Index.name: IndexUI,
    profile.Tag.Name.name: NameUI,
    profile.Tag.FnKeyMapping.name: FnKeyMappingUI,
    profile.Tag.KeyMapping.name: KeyMappingUI,
}


# holds the entire mapping dictionary and the key (the component)
class KeyUI(BaseUI):
    def __init__(self, key, mapping, dialog):
        super().__init__(key, dialog)
        self.mapping = mapping
        print("KEYUI", self.component, self.mapping)

    def _populate_model(self, dialog, model, it, pos=-1):
        wrapped = ProfileComponentWrapper(self, True)
        it = model.insert(it, pos, (wrapped,))
        return it

    def left_label(self) -> str:
        return str(self.component)

    @classmethod
    def icon_name(cls):
        return "go-next"


class KeyOneUI(KeyUI):
    CLASS = profile.KeyOne

    def right_label(self) -> str:
        mapped = self.mapping[self.component]
        return (mapped.modifiers.name + ": " if mapped.modifiers else "") + str(mapped.code)


class KeyTwoUI(KeyUI):
    CLASS = profile.KeyTwo

    def right_label(self) -> str:
        mapped = self.mapping[self.component]
        return (mapped.modifiers.name + ": " if mapped.modifiers else "") + str(mapped.code) + ", " + str(mapped.code2)


class KeyControlUI(KeyUI):
    CLASS = profile.KeyControl

    def right_label(self) -> str:
        return self.mapping[self.component].control.name


KEY_UI_CLASSES = {
    profile.KeyOne: KeyOneUI,
    profile.KeyTwo: KeyTwoUI,
    profile.KeyControl: KeyControlUI,
}


@dataclasses.dataclass
class AllowedActions:
    c: Any
    copy: bool
    insert_profile: bool
    insert_field: bool


def allowed_actions(m: Gtk.TreeStore, it: Gtk.TreeIter) -> AllowedActions:
    row = m[it]
    wrapped = row[0]
    ui = wrapped.ui
    print("AA", row, wrapped, ui, type(_profile_component_clipboard), _profile_component_clipboard)

    can_copy = isinstance(ui, ProfileUI) or isinstance(ui, FieldUI)
    can_insert_profile = isinstance(_profile_component_clipboard, profile.Profile)
    can_insert_field = isinstance(_profile_component_clipboard, profile.Field)

    return AllowedActions(ui, can_copy, can_insert_profile, can_insert_field)


class ActionMenu:
    def __init__(self, window, tree_view, profiles, dialog):
        self.window = window
        self.tree_view = tree_view
        self.profiles = profiles
        self.dialog = dialog

    def create_menu_event_button_released(self, v, e):
        if e.button == Gdk.BUTTON_SECONDARY:  # right click
            print("Set up Action Menu")
            menu = Gtk.Menu()
            m, it = v.get_selection().get_selected()
            enabled_actions = allowed_actions(m, it)
            print("CMEBR", enabled_actions)
            if enabled_actions.copy:
                menu.append(self._menu_copy(m, it))
            if enabled_actions.insert_profile:
                menu.append(self._menu_insert_profile(m, it))
            if enabled_actions.insert_field:
                menu.append(self._menu_insert_field(m, it))
            menu.append(self._menu_cut(m, it))
            menu.append(self._menu_delete(m, it))
            if menu.get_children():
                menu.popup_at_pointer(e)

    def menu_do_delete(self, _mitem, m, it):
        c = m[it][0].ui.component
        if isinstance(c, profile.Profile):  # remove profile
            m.remove(it)
            self.profiles.remove(c)
        elif isinstance(new_c, profile.Field):  # remove field from profile
            pos = m.get_path(it)[0]
            profile_it = m.get_iter([pos])
            delattr(m[parent_it][0].ui.component, c.profile_tag)
            m.remove(it)
        return c

    def _menu_delete(self, m, it) -> Gtk.MenuItem:
        menu_delete = Gtk.MenuItem(_("Delete"))
        menu_delete.connect(GtkSignal.ACTIVATE.value, self.menu_do_delete, m, it)
        menu_delete.show()
        return menu_delete

    def menu_do_cut(self, _mitem, m, it):
        global _rule_component_clipboard
        c = self.menu_do_delete(_mitem, m, it)
        _rule_component_clipboard = c
        return c

    def _menu_cut(self, m, it):
        menu_cut = Gtk.MenuItem(_("Cut"))
        menu_cut.connect(GtkSignal.ACTIVATE.value, self.menu_do_cut, m, it)
        menu_cut.show()
        return menu_cut

    def menu_do_copy(self, _mitem: Gtk.MenuItem, m: Gtk.TreeStore, it: Gtk.TreeIter):
        global _profile_component_clipboard
        c = m[it][0].ui.component
        _profile_component_clipboard = copy.deepcopy(c)
        return c

    def _menu_copy(self, m, it):
        menu_copy = Gtk.MenuItem(_("Copy"))
        menu_copy.connect(GtkSignal.ACTIVATE.value, self.menu_do_copy, m, it)
        menu_copy.show()
        return menu_copy

    def _menu_do_insert(self, _mitem, m, it, new_c):
        pos = m.get_path(it)[0]
        if isinstance(new_c, profile.Profile):  # insert profile after current profile
            self.profiles.insert(pos, new_c)
            new_it = ProfileUI(new_c, self.dialog)._populate_model(self.dialog, m, None, pos + 1)
            profile_it = m.iter_nth_child(None, pos + 1)
        elif isinstance(new_c, profile.Field):  # insert field into current profile
            tag = new_c.profile_tag
            profile_it = m.get_iter([pos])
            child_it = m.iter_children(profile_it)
            while child_it:
                child_c = m[child_it][0].ui.component
                if child_c.profile_tag == tag:
                    m.remove(child_it)
                child_it = m.iter_next(child_it)
            m[profile_it][0].ui.component.set_field(tag, new_c)
            new_it = FIELD_UI_CLASSES[tag.name](new_c, self.dialog)._populate_model(self.dialog, m, profile_it)
        self.tree_view.get_selection().select_iter(new_it)
        self.tree_view.expand_row(m.get_path(new_it), True)

    def menu_do_insert(self, _mitem, m, it, below=False):
        global _profile_component_clipboard
        c = _profile_component_clipboard
        _profile_component_clipboard = None
        if c:
            _profile_component_clipboard = copy.deepcopy(c)
            self._menu_do_insert(_mitem, m, it, new_c=c)
            self.dialog.on_update()

    def _menu_insert_profile(self, m, it, below=False):
        menu_insert = Gtk.MenuItem(_("Paste Profile"))
        menu_insert.connect(GtkSignal.ACTIVATE.value, self.menu_do_insert, m, it, below)
        menu_insert.show()
        return menu_insert

    def _menu_insert_field(self, m, it, below=False):
        menu_insert = Gtk.MenuItem(_("Paste Field"))
        menu_insert.connect(GtkSignal.ACTIVATE.value, self.menu_do_insert, m, it, below)
        menu_insert.show()
        return menu_insert


class ProfileComponentWrapper(GObject.GObject):
    def __init__(self, ui, editable=False):
        self.ui = ui
        self.editable = editable
        GObject.GObject.__init__(self)

    def display_left(self):
        if self.ui is None:
            return ""
        return "  " + self.ui.left_label()

    def display_right(self):
        if self.ui is None:
            return ""
        return self.ui.right_label()

    def display_icon(self):
        if self.ui is None:
            return ""
        return self.ui.icon_name()


def _populate_model(dialog, model: Gtk.TreeStore, it: Gtk.TreeIter, profs):
    if profs:
        for prof in profs:
            ProfileUI(prof, dialog)._populate_model(dialog, model, it)


def button(label, icon_name, show_image, sensitive, clicked):
    btn = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    btn.set_label(label)
    btn.set_always_show_image(show_image)
    btn.set_sensitive(sensitive)
    btn.set_valign(Gtk.Align.CENTER)
    btn.connect(GtkSignal.CLICKED.value, clicked)
    return btn


class ProfileDialog:
    dirty = False

    def __init__(self, profiles, device=None):
        self.profiles = profiles
        self.device = device

        button_box = Gtk.HBox(spacing=20)
        if device is None:
            self.save_btn = button(_("Save changes"), "document-save-as", True, False, lambda *_args: self._save_profiles())
            button_box.pack_start(self.save_btn, False, False, 0)
        self.discard_btn = button(_("Discard changes"), "document-revert", True, False, lambda *_args: self._reload_profiles())
        button_box.pack_start(self.discard_btn, False, False, 0)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_valign(Gtk.Align.CENTER)
        button_box.set_size_request(0, 50)

        grid = Gtk.Grid()
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        grid.set_size_request(0, 120)
        self.edit_panel = grid
        print("EP", self, self.__dict__)

        view = Gtk.TreeView()
        view.set_headers_visible(False)
        view.set_enable_tree_lines(True)
        view.set_reorderable(False)
        view.connect(GtkSignal.KEY_PRESS_EVENT.value, self._event_key_pressed)
        view.connect(GtkSignal.BUTTON_RELEASE_EVENT.value, self._event_button_released)
        view.get_selection().connect(GtkSignal.CHANGED.value, self._selection_changed)
        cell_icon = Gtk.CellRendererPixbuf()
        cell1 = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Type")
        col1.pack_start(cell_icon, False)
        col1.pack_start(cell1, True)
        col1.set_cell_data_func(cell1, lambda _c, c, m, it, _d: c.set_property("text", m.get_value(it, 0).display_left()))
        cell2 = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Summary")
        col2.pack_start(cell2, True)
        col2.set_cell_data_func(cell2, lambda _c, c, m, it, _d: c.set_property("text", m.get_value(it, 0).display_right()))
        col2.set_cell_data_func(
            cell_icon, lambda _c, c, m, it, _d: c.set_property("icon-name", m.get_value(it, 0).display_icon())
        )
        view.append_column(col1)
        view.append_column(col2)
        self.view = view

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        sw.add(view)
        sw.set_size_request(0, 500)  # don't ask for so much height

        self.model = _create_model(profiles, self)
        self.view.set_model(self.model)
        #        self.view.expand_all()

        vbox = Gtk.VBox()
        vbox.pack_start(button_box, False, False, 0)
        vbox.pack_start(sw, True, True, 10)
        vbox.pack_start(self.edit_panel, False, False, 10)

        window = Gtk.Window()
        window.set_title(_("Solaar Profile Editor") + ": " + (device.name if device else _("Saved Profiles")))
        window.add(vbox)
        geometry = Gdk.Geometry()
        geometry.min_width = 600  # don't ask for so much space
        geometry.min_height = 400
        window.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.show_all()
        style = window.get_style_context()
        style.add_class("solaar")
        window.connect(GtkSignal.DELETE_EVENT.value, self._closing)
        window.connect(GtkSignal.DELETE_EVENT.value, lambda w, e: w.hide_on_delete() or True)

        self.window = window
        self._action_menu = ActionMenu(self.window, self.view, self.profiles, self)

    def _save_profiles(self):  # save profiles to configuration profile file
        try:
            profile.save_profiles_to_yaml(_profile_file_path, _saved_profiles)
            if hasattr(self, "save_btn"):
                self.save_btn.set_sensitive(False)
            self.discard_btn.set_sensitive(False)
            self.dirty = False
            return True
        except Exception as e:
            logger.error("failed to save profiles to %s: %s", _profile_file_path, e)
        print("SAVED", _saved_profiles)

    def _reload_profiles(self):  # reload profiles from configuration profile file
        print("RELOAD PROFILES", self.device)
        global _saved_profiles
        if hasattr(self, "save_btn"):
            self.save_btn.set_sensitive(False)
        self.discard_btn.set_sensitive(False)
        self.dirty = False
        if self.device is None:
            profiles = _saved_profiles = _load_profiles()
        else:
            device_profiles = self.device.profiles_new
            profiles = [device_profiles.get_profile(id, False) for id in device_profiles.get_profile_ids()]
            print("RELOAD PROFILES FROM", self.device, profiles)
        self.model = _create_model(profiles, self)
        self.view.set_model(self.model)

    #        self.view.expand_all()

    def _closing(self, window: Gtk.Window, e: Gdk.Event):
        window.hide()

    def _selection_changed(self, selection):
        print("SC", self, self.__dict__)
        self.edit_panel.set_sensitive(False)
        (model, it) = selection.get_selected()
        if it is None:
            return
        wrapped = model[it][0]
        ui = wrapped.ui
        print("SELECTION CHANGED", it, ui, ui.component)
        ui.show(self.edit_panel)
        self.edit_panel.set_sensitive(True)

    def _event_key_pressed(self, v, e):
        """Shortcuts:?"""
        print("EVENT KEY PRESSED")
        pass

    def _event_button_released(self, v, e):
        print("EVENT BUTTON RELEASED")
        self._action_menu.create_menu_event_button_released(v, e)

    def on_update(self):
        self.view.queue_draw()
        self.dirty = True
        if hasattr(self, "save_btn"):
            self.save_btn.set_sensitive(True)
        self.discard_btn.set_sensitive(True)


def _create_model(profiles, dialog):
    model = Gtk.TreeStore(ProfileComponentWrapper)
    print("CM", model, profiles, dialog)
    _populate_model(dialog, model, None, profiles)
    return model


def edit_device_profiles(device):
    GObject.type_register(ProfileComponentWrapper)
    global _device_profiles_dialogs
    device_profiles = device.profiles_new
    if device not in _device_profiles_dialogs and device_profiles:
        profiles = [device_profiles.get_profile(id) for id in device_profiles.get_profile_ids()]
        print("EDP P", profiles)
        dialog = ProfileDialog(profiles, device)
        _device_profiles_dialogs[device] = dialog
        dialog.window.present()
    else:
        _device_profiles_dialogs[device].window.present()


def _load_profiles():  # load profiles from configuration profile file
    if True:  # pfps try:
        profiles = profile.load_profiles_from_yaml(_profile_file_path)
    #    except Exception as e:
    #        logger.error("failed to load profiles from %s: %s", _profile_file_path, e)
    #        profiles = []
    print("LOADED", profiles)
    return profiles


def edit_saved_profiles():
    GObject.type_register(ProfileComponentWrapper)
    global _saved_profiles
    global _saved_profiles_dialog
    if _saved_profiles is None:
        _saved_profiles = _load_profiles()
    if _saved_profiles_dialog is None:
        _saved_profiles_dialog = ProfileDialog(_saved_profiles)
    _saved_profiles_dialog.window.present()
