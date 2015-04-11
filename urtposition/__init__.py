#
# UrTPosition Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 Daniele Pantaleone <fenix@bigbrotherbot.net>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# CHANGELOG
#
# 2015/04/04 - 1.0 - Fenix - initial version
# 2015/04/11 - 1.1 - Fenix - fixed mixed missing configuration file header

__author__ = 'Fenix'
__version__ = '1.1'

import b3
import b3.clients
import b3.plugin
import b3.events
import re

from b3 import TEAM_SPEC
from b3.cron import PluginCronTab
from b3.exceptions import MissingRequirement
from ConfigParser import NoOptionError
from .position import Position
from .position import ORIGIN


class UrtpositionPlugin(b3.plugin.Plugin):

    requiresParsers = ['iourt42']

    def __init__(self, console, config=None):
        """
        Build the plugin object.
        """
        b3.plugin.Plugin.__init__(self, console, config)

        self.position_re = re.compile(r"""^(?P<cid>\d+)\s*-\s*(?P<x>[-+]?[0-9]*\.?[0-9]+)\s*-\s*(?P<y>[-+]?[0-9]*\.?[0-9]+)\s*-\s*(?P<z>[-+]?[0-9]*\.?[0-9]+)""")
        self.position_update_ignore_till = self.console.time() + 30
        self.position_update_interval = 10
        self.position_update_crontab = None

        if not 'position' in self.console.write('cmdlist position'):
            raise MissingRequirement('you need a custom server modification to run this plugin')

    def onLoadConfig(self):
        """
        Load plugin configuration
        """
        try:
            self.position_update_interval = self.config.getint('settings', 'position_update_interval')
        except (NoOptionError, ValueError), e:
            self.warning("missing or bad value for settings/position_update_interval: %s", e)
        else:
            if not 5 <= self.position_update_interval <= 60:
                self.warning("settings/position_update_interval must be in range 5-60: setting default value")
                self.position_update_interval = 10
        self.info('settings/position_update_interval: %s sec' % self.position_update_interval)

    def onStartup(self):
        """
        Initialize plugin.
        """
        # register the events needed
        self.registerEvent('EVT_GAME_EXIT', self.on_game_exit)
        self.registerEvent('EVT_CLIENT_CONNECT', self.on_origin)
        self.registerEvent('EVT_CLIENT_JOIN', self.on_update)
        self.registerEvent('EVT_CLIENT_TEAM_CHANGE', self.on_update)
        self.registerEvent('EVT_CLIENT_JUMP_RUN_START', self.on_update)
        self.registerEvent('EVT_CLIENT_JUMP_RUN_STOP', self.on_update)
        self.registerEvent('EVT_CLIENT_JUMP_RUN_CANCEL', self.on_update)

        # we already parse position data on such events so use them
        self.registerEvent('EVT_CLIENT_POS_SAVE', self.on_save_load)
        self.registerEvent('EVT_CLIENT_POS_LOAD', self.on_save_load)

        # create our custom events so other plugins can react on those
        self.console.createEvent('EVT_CLIENT_MOVE', 'Event client move')
        self.console.createEvent('EVT_CLIENT_STANDING', 'Event client standing')

        # setup automatic position refresh
        self.position_update_crontab = PluginCronTab(self, self._update, 0, '*/%s' % self.position_update_interval)
        self.console.cron + self.position_update_crontab

    ####################################################################################################################
    #                                                                                                                  #
    #   EVENTS                                                                                                         #
    #                                                                                                                  #
    ####################################################################################################################

    def on_game_exit(self, _):
        """
        Handle EVT_GAME_EXIT
        """
        self.position_update_ignore_till = self.console.time() + 30

    def on_origin(self, event):
        """
        Set client position to origin
        """
        self._set_client_position(event.client, ORIGIN)

    def on_update(self, event):
        """
        Set the client position by retrieving the value from the server
        """
        self._set_client_position(event.client)

    def on_save_load(self, event):
        """
        Handle EVT_CLIENT_POS_SAVE and EVT_CLIENT_POS_LOAD
        """
        data = event.data['position']
        self._set_client_position(event.client, Position(data[0], data[1], data[2]))

    ####################################################################################################################
    #                                                                                                                  #
    #   OTHER METHODS                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    @staticmethod
    def _get_client_position(client):
        """
        Return the position of the given client
        :param client: The client whose position we want to retrieve
        """
        return getattr(client, 'position', None) or ORIGIN

    def _set_client_position(self, client, position_new=None):
        """
        Update the client position.
        :param client: The client whose position we want to update
        :param position_new: Optional position (will perform new retrieval if not provided)
        """
        if not position_new:
            position_new = ORIGIN
            if client.team != TEAM_SPEC:
                rv = self.console.write('position %s' % client.cid)
                match = self.position_re.match(rv)
                if not match:
                    self.warning('could not parse client <%s> position: line did not match format: %s' % (client.cid, rv))
                else:
                    position_new = Position(match.group('x'), match.group('y'), match.group('z'))

        # get the old position value
        position_old = self._get_client_position(client)

        # store always the value in the client
        client.position = position_new
        self.verbose('updated client %s position: %s' % (client.cid, client.position))

        if position_old != position_new:
            if position_old != ORIGIN and position_new != ORIGIN:
                self.console.queueEvent(self.console.getEvent('EVT_CLIENT_MOVE', {'from': position_old, 'to': position_new}, client))
        else:
            if position_old != ORIGIN and position_new != ORIGIN:
                self.console.queueEvent(self.console.getEvent('EVT_CLIENT_STANDING', {'where': client.position}, client))

    ####################################################################################################################
    #                                                                                                                  #
    #   CRON                                                                                                           #
    #                                                                                                                  #
    ####################################################################################################################

    def _update(self):
        """
        Scheduled execution
        """
        if self.console.time() > self.position_update_ignore_till:
            self.debug('refreshing clients positions...')
            rv = self.console.write('position all')
            for line in rv.split('\n'):
                m = self.position_re.match(line)
                if not m:
                    self.warning('could not parse client position: line did not match format: %s' % line)
                else:
                    client = self.console.clients.getByCID(m.group('cid'))
                    if not client:
                        self.warning('retrieved position for client <%s> but no b3 client instance is found' % m.group('cid'))
                    else:
                        if client.team != TEAM_SPEC:
                            position_new = Position(m.group('x'), m.group('y'), m.group('z'))
                        else:
                            position_new = ORIGIN
                        # update client position using the new value: this won't trigger per player
                        # position retrieval since we already parsed the value (prevent server flooding)
                        self._set_client_position(client, position_new)
