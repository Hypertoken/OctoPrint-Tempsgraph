# coding=utf-8
from __future__ import absolute_import
from flask.ext.babel import gettext
import re

import octoprint.plugin


class TempsgraphPlugin(octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.TemplatePlugin):
    def __init__(self):
        self.speed = "N/A"

        ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            backgroundPresets=[
                dict(
                    name="Default",
                    value=None),
                dict(
                    name="Discorded",
                    value="#36393f"),
                dict(
                    name="Custom",
                    value="#fffff")],
            axisesPresets=[
                dict(
                    name="Default",
                    value=None),
                dict(
                    name="Discorded",
                    value="#dadadc"),
                dict(
                    name="Custom",
                    value="#fffff")],
            color=dict(
                backgroundColor='Default',
                axisesColor="Default"
            ),
            showBackgroundImage=True

        )

    ##~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/tempsgraph.js", "js/plotly-latest.min.js"],
            css=["css/tempsgraph.css"]
            #			less=["less/tempsgraph.less"]
        )

    def process_gcode_received(self, comm, line, *args, **kwargs):
        if "Fanspeed" not in line:
            return line

        fan_response = re.search("(\d*\.?\d+?)", line)
        if fan_response and fan_response.group(1):
            fan_response = fan_response.group(1)
            if float(fan_response) == 0:
                self.speed = gettext('Off')
            else:
                self.speed = str(int(float(fan_response) * 100.0 / 255.0)) + "%"
            self._plugin_manager.send_plugin_message(self._identifier, dict(speed=self.speed))
        return line

    def process_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if gcode and gcode.startswith('M106'):
            s = re.search("S(.+)", cmd)
            if s and s.group(1):
                s = s.group(1)
                if float(s) == 0:
                    self.speed = gettext('Off')
                else:
                    self.speed = str(int(float(s) * 100.0 / 255.0)) + "%"
                self._plugin_manager.send_plugin_message(self._identifier, dict(speed=self.speed))
        if gcode and gcode.startswith('M107'):
            self.speed = gettext('Off')
            self._plugin_manager.send_plugin_message(self._identifier, dict(speed=self.speed))

        return None

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            tempsgraph=dict(
                displayName="Tempsgraph Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="k13",
                repo="OctoPrint-Tempsgraph",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/1r0b1n0/OctoPrint-Tempsgraph/archive/{target_version}.zip"
            )
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True)
        ]


__plugin_name__ = "Tempsgraph Plugin"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TempsgraphPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.process_gcode,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.process_gcode_received,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
