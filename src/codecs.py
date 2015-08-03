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

from gi.repository import Gst, GstPbutils, GLib

from gettext import gettext as _

from lollypop.define import Lp


class Codecs:
    """
        Handle missing gstreamer codecs
    """
    def __init__(self):
        """
            Init installer
        """
        GstPbutils.pb_utils_init()
        self._messages = []

    def install(self):
        """
            Install missing plugins
        """
        try:
            context = GstPbutils.InstallPluginsContext.new()
            try:
                context.set_desktop_id('lollypop.desktop')
            except:
                pass  # Not supported by Ubuntu VIVID
            details = []
            for message in self._messages:
                detail = \
                    GstPbutils.missing_plugin_message_get_installer_detail(
                        message)
                details.append(detail)
            GstPbutils.install_plugins_async(
                details,
                context,
                self._null)
            if Lp.notify is not None:
                GLib.timeout_add(
                    10000,
                    Lp.notify.send,
                    _("Restart lollypop after installing codecs"))
        except Exception as e:
            print("Codecs::__init__(): %s" % e)

    def append(self, message):
        """
            Append a message
            @param message as Gst.Message
        """
        self._messages.append(message)

    def is_missing_codec(self, message):
        """
            Check if codec is missing
            @return missing as bool
        """
        error, debug = message.parse_error()
        if error.matches(Gst.CoreError.quark(),
                         Gst.CoreError.MISSING_PLUGIN):
            return True
        return False

    def _null(self, arg):
        pass
