# Copyright (c) 2014-2015 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk

from lollypop.define import Lp, ArtSize
from lollypop.pop_menu import TrackMenu
from lollypop.widgets_rating import RatingWidget
from lollypop.utils import seconds_to_string, rgba_to_hex
from lollypop.objects import Track, Album
from lollypop import utils



class Row(Gtk.ListBoxRow):
    """
        A row
    """

    def __init__(self):
        """
            Init row widgets
        """
        Gtk.ListBoxRow.__init__(self)
        self._object_id = None
        self._number = 0
        self._row_widget = self._builder.get_object('row')
        self._title_label = self._builder.get_object('title')
        self._title_label.set_property('has-tooltip', True)
        self._duration_label = self._builder.get_object('duration')
        self._num_label = self._builder.get_object('num')
        self._icon = self._builder.get_object('icon')
        self.add(self._row_widget)
        self.get_style_context().add_class('trackrow')
        self.show()

    def show_cover(self, show):
        """
            Show cover
            @param show as bool
        """
        pass

    def show_menu(self, show):
        """
            Show menu
        """
        pass

    def show_icon(self, show):
        """
            Show play icon
            @param widget name as str
            @param show as bool
        """
        if show:
            self._icon.set_from_icon_name('media-playback-start-symbolic', 1)
            self.get_style_context().remove_class('trackrow')
            self.get_style_context().add_class('trackrowplaying')
        else:
            self._icon.clear()
            self.get_style_context().remove_class('trackrowplaying')
            self.get_style_context().add_class('trackrow')

    def set_num_label(self, label):
        """
            Set num label
            @param label as string
        """
        self._num_label.set_markup(label)

    def set_title_label(self, label):
        """
            Set title label
            @param label as string
        """
        self._title_label.set_markup(label)

    def set_duration_label(self, label):
        """
            Set duration label
            @param label as string
        """
        self._duration_label.set_text(label)

    def set_object_id(self, object_id):
        """
            Store current object id
            @param object id as int
        """
        self._object_id = object_id

    def get_object_id(self):
        """
            Get object id
            @return Current object id as int
        """
        return self._object_id

    def set_number(self, num):
        """
            Set track number
            @param num as int
        """
        self._number = num

    def get_number(self):
        """
            Get track number
            @return num as int
        """
        return self._number

    def set_cover(self, pixbuf, tooltip):
        """
            Set cover
            @param cover as Gdk.Pixbuf
            @param tooltip as str
        """
        pass

#######################
# PRIVATE             #
#######################
    def _on_title_query_tooltip(self, widget, x, y, keyboard, tooltip):
        """
            Show tooltip if needed
            @param widget as Gtk.Widget
            @param x as int
            @param y as int
            @param keyboard as bool
            @param tooltip as Gtk.Tooltip
        """
        layout = self._title_label.get_layout()
        if layout.is_ellipsized():
            label = self._title_label.get_label()
            self._title_label.set_tooltip_markup(label)
        else:
            self._title_label.set_tooltip_text('')


class AlbumRow(Row):
    """
        A track row with album cover
    """

    def __init__(self):
        """
            Init row widget
        """
        self._builder = Gtk.Builder()
        self._builder.add_from_resource('/org/gnome/Lollypop/AlbumRow.ui')
        self._builder.connect_signals(self)
        self._cover = self._builder.get_object('cover')
        self._header = self._builder.get_object('header')
        self._artist = self._builder.get_object('artist')
        self._album = self._builder.get_object('album')
        Row.__init__(self)

    def set_object_id(self, object_id):
        """
            Store current object id and object
            @param object id as int
        """
        Row.set_object_id(self, object_id)
        self._object = Album(self._object_id)

    def show_header(self, show):
        """
            Show header
            @param show as bool
        """
        if show:
            self._header.show()
        else:
            self._header.hide()

    def set_cover(self, surface, tooltip):
        """
            Set cover
            @param cover as cairo.Surface
            @param tooltip as str
        """
        self._cover.set_from_surface(surface)
        self._cover.set_tooltip_text(tooltip)

    def set_album_and_artist(self, album_id):
        """
            Set artist and album labels
            @param album id as int
        """
        artist = Lp.albums.get_artist_name(album_id)
        album = Lp.albums.get_name(album_id)
        self._artist.set_text(artist)
        self._album.set_text(album)


class TrackRow(Row):
    """
        A track row
    """

    def __init__(self):
        """
            Init row widget
        """
        self._builder = Gtk.Builder()
        self._builder.add_from_resource('/org/gnome/Lollypop/TrackRow.ui')
        self._builder.connect_signals(self)
        self._loved_img = self._builder.get_object('loved')
        self._menu_btn = self._builder.get_object('menu')
        Row.__init__(self)

    def set_object_id(self, object_id):
        """
            Store current object id and object
            @param object id as int
        """
        Row.set_object_id(self, object_id)
        self._object = Track(self._object_id)

    def set_loved(self, loved):
        """
            Set loved
        """
        self._loved_img.set_opacity(0.6 if loved else 0.1)

    def show_menu(self, show):
        """
            Show menu
        """
        if show:
            self._menu_btn.show()
        else:
            self._menu_btn.hide()

#######################
# PRIVATE             #
#######################
    def _on_button_press(self, widget, event):
        """
            Popup menu for track relative to track row
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        if event.button != 1:
            window = widget.get_window()
            if window == event.window:
                self._popup_menu(widget, event.x, event.y)
            # Happens when pressing button over menu btn
            else:
                self._popup_menu(self._menu_btn)
            return True

    def _on_menu_btn_clicked(self, widget):
        """
            Popup menu for track relative to button
            @param widget as Gtk.Button
        """
        self._popup_menu(widget)

    def _popup_menu(self, widget, xcoordinate=None, ycoordinate=None):
        """
            Popup menu for track
            @param widget as Gtk.Button
            @param xcoordinate as int (or None)
            @param ycoordinate as int (or None)
        """
        menu = TrackMenu(self._object_id, None)
        popover = Gtk.Popover.new_from_model(widget, menu)
        if xcoordinate is not None and ycoordinate is not None:
            rect = widget.get_allocation()
            rect.x = xcoordinate
            rect.y = ycoordinate
            rect.width = 1
            rect.height = 1
            popover.set_pointing_to(rect)
        rating = RatingWidget(self._object)
        rating.set_property('margin_top', 5)
        rating.set_property('margin_bottom', 5)
        rating.show()
        # Hack to add two widgets in popover
        # Use a Gtk.PopoverMenu later (GTK>3.16 available on Debian stable)
        stack = Gtk.Stack()
        grid = Gtk.Grid()
        grid.set_orientation(Gtk.Orientation.VERTICAL)
        stack.add_named(grid, 'main')
        stack.show_all()
        menu_widget = popover.get_child()
        menu_widget.reparent(grid)
        separator = Gtk.Separator()
        separator.show()
        grid.add(separator)
        grid.add(rating)
        popover.add(stack)
        popover.connect('closed', self._on_closed)
        self.get_style_context().add_class('track-menu-selected')
        popover.show()

    def _on_closed(self, widget):
        """
            Remove selected style
            @param widget as Gtk.Popover
        """
        self.get_style_context().remove_class('track-menu-selected')


class TracksWidget(Gtk.ListBox):
    """
        A list of tracks
    """

    __gsignals__ = {
        'activated': (GObject.SignalFlags.RUN_FIRST, None, (int,))
    }

    def __init__(self, show_menu):
        """
            Init track widget
            @param show_menu as bool if menu need to be displayed
        """
        Gtk.ListBox.__init__(self)
        self._signal_id = None
        self._show_menu = show_menu
        self.connect("row-activated", self._on_activate)
        self.get_style_context().add_class('trackswidget')
        self.set_property('hexpand', True)
        self.set_property('selection-mode', Gtk.SelectionMode.NONE)

    def add_track(self, track_id, num, title, length, pos):
        """
            Add track to list
            @param track id as int
            @param track number as int
            @param title as str
            @param length as str
            @param pos as int
            @param show cover as bool
        """
        track_row = TrackRow()
        track_row.show_menu(self._show_menu)
        if Lp.player.current_track.id == track_id:
            track_row.show_icon(True)
        if utils.is_loved(track_id):
            track_row.set_loved(True)
        if pos:
            track_row.set_num_label(
                '''<span foreground="%s"
                font_desc="Bold">%s</span>''' %
                (rgba_to_hex(Lp.window.get_selected_color()),
                 str(pos)))
        elif num > 0:
            track_row.set_num_label(str(num))
        track_row.set_number(num)
        track_row.set_title_label(title)
        track_row.set_duration_label(seconds_to_string(length))
        track_row.set_object_id(track_id)
        track_row.show()
        self.add(track_row)

    def add_album(self, track_id, album_id, num, title, length, pos):
        """
            Add album row to the list
            @param track id as int
            @param album id as int or None
            @param track number as int
            @param title as str
            @param length as str
            @param pos as int
            @param show cover as bool
        """
        album_row = AlbumRow()
        album_row.show_menu(self._show_menu)
        if Lp.player.current_track.id == track_id:
            album_row.show_icon(True)
        if pos:
            album_row.set_num_label(
                '''<span foreground="%s"
                font_desc="Bold">%s</span>''' %
                (rgba_to_hex(Lp.window.get_selected_color()),
                 str(pos)))
        elif num > 0:
            album_row.set_num_label(str(num))
        album_row.set_number(num)
        album_row.set_title_label(title)
        album_row.set_duration_label(seconds_to_string(length))
        album_row.set_object_id(track_id)
        if album_id is not None:
            album_row.set_album_and_artist(album_id)
            album_id = Lp.tracks.get_album_id(track_id)
            surface = Lp.art.get_album(
                        album_id,
                        ArtSize.MEDIUM*album_row.get_scale_factor())
            album_row.set_cover(surface, Lp.albums.get_name(album_id))
            del surface
            album_row.show_header(True)
        album_row.show()
        self.add(album_row)

    def update_playing(self, track_id):
        """
            Update playing track
            @param track id as int
        """
        for row in self.get_children():
            if row.get_object_id() == track_id:
                row.show_icon(True)
            else:
                row.show_icon(False)

    def do_show(self):
        """
            Set signals callback
        """
        self._signal_id = Lp.player.connect("queue-changed",
                                            self._update_pos_label)
        Gtk.ListBox.do_show(self)

    def do_hide(self):
        """
            Clean signals callback
        """
        if self._signal_id:
            Lp.player.disconnect(self._signal_id)
            self._signal_id = None
        Gtk.ListBox.do_hide(self)

#######################
# PRIVATE             #
#######################
    def _update_pos_label(self, widget):
        """
            Update position label
            @param player
            @param track id as int
        """
        for row in self.get_children():
            track_id = row.get_object_id()
            if Lp.player.is_in_queue(track_id):
                pos = Lp.player.get_track_position(track_id)
                row.set_num_label(
                    '''<span foreground="%s"
                    font_desc="Bold">%s</span>''' %
                    (rgba_to_hex(Lp.window.get_selected_color()),
                     str(pos)))
            elif row.get_number() > 0:
                row.set_num_label(str(row.get_number()))
            else:
                row.set_num_label('')

    def _on_activate(self, widget, row):
        """
            Play activated item
            @param widget as TracksWidget
            @param row as TrackRow
        """
        self.emit('activated', row.get_object_id())
