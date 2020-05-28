# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
An app that syncs the frame range between a scene and a shot in Shotgun.

"""
import os
import traceback

from tank.platform import Application
from tank.platform.qt import QtCore, QtGui
import tank


class BasePlayBlast(Application):
    """
    """
    playblastManager = None
    def init_app(self):
        print '==='*50
        print 'Try initialize BasePlayBlast....'
        print '==='*50

        """
        App entry point
        """
        # make sure that the context has an entity associated - otherwise it wont work!
        if self.context.entity is None:
            raise tank.TankError(
                "Cannot load the Set Frame Range application! "
                "Your current context does not have an entity (e.g. "
                "a current Shot, current Asset etc). This app requires "
                "an entity as part of the context in order to work."
            )

        # We grab the menu name from the settings so that the user is able to register multiple instances
        # of this app with different frame range fields configured.

        self.engine.register_command(self.get_setting("menu_name"), self.run_app)

    @property
    def context_change_allowed(self):
        """
        Specifies that context changes are allowed.
        """
        return True

    def destroy_app(self):
        """
        App teardown
        """
        self.logger.debug("Destroying sg_set_frame_range")

    def run_app(self):
        print '==='*50
        print 'Try run BasePlayBlast....'
        print '==='*50

        try:
            playblastManager = self.get_playblast_manager()
            playblastManager.showDialog()
        except:
            traceback.print_exc()

    ###############################################################################################
    # implementation

    def get_frame_range_from_shotgun(self):
        """
        get_frame-range_from_shotgun will query shotgun for the
            'sg_in_frame_field' and 'sg_out_frame_field' setting values and return a
            tuple of (in, out).

        If the fields specified in the settings do not exist in your Shotgun site, this will raise
            a tank.TankError letting you know which field is missing.

        :returns: Tuple of (in, out)
        :rtype: tuple[int,int]
        :raises: tank.TankError
        """
        # we know that this exists now (checked in init)
        entity = self.context.entity

        sg_entity_type = self.context.entity["type"]
        sg_filters = [["id", "is", entity["id"]]]

        sg_in_field = self.get_setting("sg_in_frame_field")
        sg_out_field = self.get_setting("sg_out_frame_field")
        fields = [sg_in_field, sg_out_field]

        data = self.shotgun.find_one(sg_entity_type, filters=sg_filters, fields=fields)

        # check if fields exist!
        if sg_in_field not in data:
            raise tank.TankError(
                "Configuration error: Your current context is connected to a Shotgun "
                "%s. This entity type does not have a "
                "field %s.%s!" % (sg_entity_type, sg_entity_type, sg_in_field)
            )

        if sg_out_field not in data:
            raise tank.TankError(
                "Configuration error: Your current context is connected to a Shotgun "
                "%s. This entity type does not have a "
                "field %s.%s!" % (sg_entity_type, sg_entity_type, sg_out_field)
            )

        return (data[sg_in_field], data[sg_out_field])

    def get_current_frame_range(self):
        """
        get_current_frame_range will execute the hook specified in the 'hook_frame_operation'
            setting for this app.
        It will record the result of the hook and return the values as a tuple of (in, out).

        If there is an internal exception thrown from the hook, it will reraise the exception as
            a tank.TankError and write the traceback to the log.
        If the data returned is not in the correct format, tuple with two keys, it will
            also throw a tank.TankError exception.

        :returns: Tuple of (in, out) frame range values.
        :rtype: tuple[int,int]
        :raises: tank.TankError
        """
        try:
            result = self.execute_hook_method("hook_frame_operation", "get_frame_range")
        except Exception as err:
            error_message = traceback.format_exc()
            self.logger.error(error_message)
            raise tank.TankError(
                "Encountered an error while getting the frame range: {}".format(
                    str(err)
                )
            )

        if not isinstance(result, tuple) or (
            isinstance(result, tuple) and len(result) != 2
        ):
            raise tank.TankError(
                "Unexpected type returned from 'hook_frame_operation' for operation get_"
                "frame_range - expected a 'tuple' with (in_frame, out_frame) values but "
                "returned '%s' : %s" % (type(result).__name__),
                result,
            )
        return result

    def set_frame_range(self, in_frame, out_frame):
        """
        set_current_frame_range will execute the hook specified in the 'hook_frame_operation'
            setting for this app.
        It will pass the 'in_frame' and 'out_frame' to the hook.

        If there is an internal exception thrown from the hook, it will reraise the exception as
            a tank.TankError and write the traceback to the log.

        :param int in_frame: The value of in_frame that we want to set in the current session.
        :param int out_frame: The value of out_frame that we want to set in the current session.
        :raises: tank.TankError
        """
        try:
            self.execute_hook_method(
                "hook_frame_operation",
                "set_frame_range",
                in_frame=in_frame,
                out_frame=out_frame,
            )
        except Exception as err:
            error_message = traceback.format_exc()
            self.logger.error(error_message)
            raise tank.TankError(
                "Encountered an error while setting the frame range: {}".format(
                    str(err)
                )
            )

    def get_playblast_manager(self):
        """
        Create a singleton PlayblastManager object to be used by any app.
        """
        if self.playblastManager is None:
            tk_maya_playblast = self.import_module("tk_maya_playblast")
            self.playblastManager = tk_maya_playblast.PlayblastManager(self)
        return self.playblastManager
