# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import shutil
import traceback

import maya.cmds as cmds
import pymel.core as pm
import pprint
import glob

import tank
from tank import Hook
import subprocess as S

from datetime import datetime 
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

class PostPlayblast(Hook):
    """
    Hook called when a file needs to be copied
    """
    
    def execute(self, action="", data=[], **kwargs):
        """
        Main hook entry point
        
        :action:        String
                        copy_file           -> copy QTfiles to locations in config
                        create_version      -> register a new Version entity in Shotgun or update existing Version
                        upload_move         -> upload generated QT file to Shotgun
        """
        # get the application and it's shotgun instance
        app=self.parent
        sg = app.sgtk.shotgun
        
        if action == "copy_file":
            try:
                # get all required template
                template_work = app.get_template("template_work")
                template_shot = app.get_template("template_shot")
                template_sequence = app.get_template("template_sequence")
                # use current scene name to create valid QT file names
                scenename = pm.sceneName()
                fields = template_work.get_fields(scenename)
                destination = [template_shot.apply_fields(fields), 
                               template_sequence.apply_fields(fields)]
                # make sure that destination folder is exists
                for each in destination:
                    if not os.path.exists(os.path.dirname(each)):
                        os.makedirs(os.path.dirname(each))
                # copy local file to destination
                for each in destination:
                    shutil.copy(data, each)
            except:
                print "Error in copying file %s" % data
            return True

        elif action == "assemble_movie":
            # pass
            ffmpeg_bin = 'ffmpeg'
            FPS = str(25)
            AUDIO = ''

            mov_file = data['movie_path']
            start_frame = str(data['st'])
            sequence_mask = data['path']+'.%04d.png'

            mov_file = data['movie_path']
            # '''
            convert_cmd = ffmpeg_bin+\
                          ' -f image2 -start_number '+\
                          start_frame+\
                          ' -r '+FPS+\
                          ' -i '+sequence_mask+\
                          ' -movflags +faststart -pix_fmt yuv420p -y '+\
                          mov_file
            # '''
            SUB_C = convert_cmd.split(' ')
            C = S.Popen(SUB_C , stdout=S.PIPE, stdin=S.PIPE, stderr=S.PIPE)
            OUT = C.communicate()[0]
            # print C
            app.log_debug(pprint.pprint(C))
            
            '''
            ' -i '+AUDIO+\
            ' -c:v libx264 -c:a '+\
            audio_codec+\

            '''
            stf = '%04d' %data['st']

            first_frame_thumbnail = data['path']+'.'+stf+'.png'
            return [ mov_file,first_frame_thumbnail ]


        elif action == "create_version":
            """ 
                Setting up shotgun version entity without uploading the QT file
            """
            # currentDatetime = datetime.now().strftime(TIMESTAMP_FORMAT)
            # descriptionForm = "%(comment)s\n\nPublish by %(username)s at %(hostname)s on %(datetime)s"

            # data['description'] = descriptionForm % dict(
                # comment=data['description'],
                # datetime=currentDatetime,
                # username=os.environ.get("USERNAME", "unknown"),
                # hostname=os.environ.get("COMPUTERNAME", "unknown"))
            
            app.log_debug("Setting up shotgun version entity...")
            
            try:
                filters = [ ["Project", "is", data["project"]],
                            ["code", "is", data["code"]],
                            ]
                # check if a version entity with same code exists in shotgun
                # if none, create a new version Entity with qtfile name as its code
                result=None
                version = sg.find_one("Version", [["code", "is", data["code"]]])
                if version:
                    app.log_debug("Version already exist, updating")
                    result = sg.update('Version', version["id"], data)
                else:
                    app.log_debug("Create a new Version as %s" % data["code"])
                    result = sg.create('Version', data)
            except:
                app.log_debug("Something wrong")
                traceback.print_exc()
            return result

        elif action == "upload_movie":
            """
                Sending it to shotgun
            """
            app.log_debug("Send mp4 file to Shotgun")


            try:
                moviePath = data["path"]
                thb_path = data['thumb']

                filters =[ ["Project", "is", data["project"]],
                           ["id", "is", data["version_id"]],
                           ]
                result=None
                if os.path.exists(moviePath):
                    app.log_debug("\nUploading movie to Shotgun: %s" % moviePath)
                    
                    result=sg.upload("Version", data["version_id"], moviePath, 
                        field_name="sg_uploaded_movie")
                    sg.upload_thumbnail('Version', data["version_id"], thb_path)

                return result
            except:
                app.log_debug("\n..........Something wrong")
                traceback.print_exc()
        
        elif action == 'cleanup':
            path_mask = data
            app.log_debug("..... cleanup data:")
            app.log_debug(data)

            for f in glob.glob(data):
                os.remove(f)
        elif action == 'export_caches':
            pass
        elif action == 'export_camera':
            pass

        else:
            app.log_debug("nothing to do")
