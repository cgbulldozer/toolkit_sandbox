import datetime
import os
import pprint
import re
import shutil
import sys
import traceback

from contextlib import contextmanager

import tank
from tank.platform.qt import QtCore, QtGui
from .playblast_dialog import PlayblastDialog
# from .huds import HeadUps

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

class PlayblastManager(object):
    __uploadToShotgun = True

    """
    Main playblast functionality
    """
    def __init__(self, app, context=None):
        """
        Construction
        """
        self._app = app
        self._context = context if context else self._app.context

    def showDialog(self):
        try:
            self._app.engine.show_dialog("Playblast %s" % self._app.version,
                                         self._app, PlayblastDialog, self._app, self)
            print '-'*50
            # self._app.log_info(pprint.pprint(dir(self._context)) )
            # self._app.log_info(self._context.user )
            print '-'*50

        except:
            traceback.print_exc()

    def doPlayblast(self, **overridePlayblastParams):
        template_work = self._app.get_template("template_work")
        template_shot = self._app.get_template("template_shot")
        print '\ntemplate_work:', template_work
        # print 'template_work:', template_work

        sceneName = pm.sceneName()
        fields = template_work.get_fields(sceneName)
        self.shotPlayblastPath = template_shot.apply_fields(fields)

        # Get value of optional config field "temp_directory". If path is
        # invalid or not absolute, use default tempdir.
        temp_directory = os.path.normpath( self._app.get_setting("temp_directory", "default") )
        if not os.path.isabs(temp_directory):
            import tempfile
            temp_directory = tempfile.gettempdir()

        # make sure it is exists
        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)
        # use the basename of generated names
        self.localPlayblastPath = os.path.join(temp_directory, os.path.basename(self.shotPlayblastPath))
        
        print ' Local Playblast Path : ', self.localPlayblastPath
        print temp_directory, self.shotPlayblastPath
        print '-'*50

        # run actual playblast routine
        self.__createPlayblast(**overridePlayblastParams)
        self._app.log_info("Playblast for %s succesful" % sceneName)
        
    def __createPlayblast(self, **overridePlayblastParams):
        localPlayblastPath = self.localPlayblastPath
        
        # setting playback range
        originalPlaybackRange = ( pm.playbackOptions( query=True, minTime=True ), 
                                  pm.playbackOptions( query=True, maxTime=True ))
        startTime = pm.playbackOptions( query=True, animationStartTime=True )
        endTime = pm.playbackOptions( query=True, animationEndTime=True )
        pm.playbackOptions( edit=True, minTime=startTime, maxTime=endTime )
        
        # get playblast parameters from hook

        playblastParams = self._app.execute_hook("hook_setup_window", 
            action="playblast_params", data=localPlayblastPath)



        # get window and editor parameters from hook
        createWindow = self._app.execute_hook("hook_setup_window", action='create_window')

        # with the created window, do a playblast
        with createWindow():
            playblastParams.update(overridePlayblastParams)
            playblastSuccessful = False
            while not playblastSuccessful:
                try:
                    # set required visibleHUDs from hook
                    visibleHUDs = self._app.execute_hook("hook_setup_window", action="hud_set")
                    print '\nparameters:', playblastParams

                    resultPlayblastPath = pm.playblast( **playblastParams )

                    playblastSuccessful = True
                except RuntimeError, e:
                    result = QtGui.QMessageBox.critical(None, u"Playblast Error",
                                                        "%s\n\n... or just close your QuickTime player, and Retry." % unicode(e),
                                                        QtGui.QMessageBox.Retry | QtGui.QMessageBox.Abort)
                    if result==QtGui.QMessageBox.Abort:
                        self._app.log_error("Playblast aborted")
                        return
                finally:
                    # restore HUD state
                    self._app.execute_hook("hook_setup_window", action="hud_unset", 
                        data='visibleHUDs')
                    # restore playback range
                    originalMinTime, originalMaxTime = originalPlaybackRange
                    pm.playbackOptions( edit=True, minTime=originalMinTime, maxTime=originalMaxTime )

        # do post playblast process, copy files and other necessary stuff
        # result = self._app.execute_hook("hook_post_playblast", action="copy_file", data=localPlayblastPath)
        # if result:
            # self._app.log_info("Playblast local file created: %s" % localPlayblastPath)
        

        # sequence_mask = localPlayblastPath
        movie_path = localPlayblastPath+'.mp4'

        data_seq = {'st':startTime,
                    'path':localPlayblastPath,'movie_path':movie_path}

        movie_file, thumbnail_file = self._app.execute_hook("hook_post_playblast", 
                                        action="assemble_movie", 
                                        data=data_seq)

        
        # register new Version entity in shotgun or update existing version, minimize shotgun data
        # playblast_movie = self.shotPlayblastPath
        # playblast_movie = localPlayblastPath
        playblast_movie = movie_path
        project = self._app.context.project
        entity = self._app.context.entity
        task = self._app.context.task

        data = { 'project': project,
                 'code': os.path.basename(playblast_movie),
                 'description': self.__messageText,
                 'sg_path_to_movie': playblast_movie,
                 'entity': entity,
                 'sg_task': task,
               }
        self._app.log_debug("Version-creation hook data:\n" + pprint.pformat(data))
        result = self._app.execute_hook("hook_post_playblast", 
                                        action="create_version", 
                                        data=data)


        # upload QT file if creation or update process run succesfully
        self._app.log_debug("Version-creation hook result:\n" + pprint.pformat(result))
        self._app.log_info("Upload to Shotgun:")
        self._app.log_info( data )


        if result and self.__uploadToShotgun:
            result = self._app.execute_hook("hook_post_playblast", 
                                            action="upload_movie",
                                            data=dict(path=data["sg_path_to_movie"],
                                                      project=project,
                                                      version_id=result["id"],
                                                      thumb=thumbnail_file
                                                      ))

        remove_mask = localPlayblastPath+'.*.png'
        self._app.log_info(remove_mask)

        self._app.execute_hook("hook_post_playblast", action="cleanup", 
                                        data=remove_mask)


        self._app.log_info("Playblast finished")

    def setUploadToShotgun(self, value):
        self._app.log_debug("Upload to Shotgun set to %s" % value)
        self.__uploadToShotgun = value

    def setMessageText(self,text):
        self._app.log_debug("Message to Shotgun set to %s" % text)
        self.__messageText = text
        
