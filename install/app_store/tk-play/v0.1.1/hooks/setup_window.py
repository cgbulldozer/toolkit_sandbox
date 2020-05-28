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
import re

import maya.cmds as cmds
import pymel.core as pm
import traceback
from contextlib import contextmanager
from pprint import pprint

import tank
from tank import Hook


PLAYBLAST_WINDOW = "Playblast Window"

DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

MODEL_EDITOR_PARAMS = {
    "activeView": True,
    "cameras": False,
    "controlVertices": False,
    "deformers": False,
    "dimensions": False,
    "displayAppearance": "smoothShaded",
    "displayLights": "default",
    "displayTextures": True,
    "dynamicConstraints": False,
    "fogging": False,
    "follicles": False,
    "grid": False,
    "handles": False,
    "headsUpDisplay": True,
    "hulls": False,
    "ignorePanZoom": False,
    "ikHandles": False,
    "imagePlane": False,
    "joints": False,
    "lights": False,
    "locators": False,
    "manipulators": False,
    "nurbsCurves": False,
    "nurbsSurfaces": False,
    "pivots": False,
    "planes": False,
    "selectionHiliteDisplay": False,
    "shadows": False,
    "sortTransparent": True,
    "strokes": True,
    "textures": True,
    "useDefaultMaterial": False,
    "wireframeOnShaded": False,
    }

PLAYBLAST_PARAMS = {
    "forceOverwrite": True,
    "format": "image",
    "framePadding": 4,
    "compression": "png",
    "offScreen": True,
    "percent": 100,
    "showOrnaments": True,
    "viewer": False,
    "sequenceTime": 0,
    "clearCache": True,
    "quality": 100,
    }

class SetupWindow(Hook):
    """
    Hook called when creating playblast
    """
    
    def execute(self, action='', data=[], **kwargs):
        """
        Main hook entry point
        
        :action:        String
                        hud_set             -> set required HUDs
                        hud_unset           -> removed added HUDs, restoring back to original setup
                        playblast_params    -> read playblast parameters
                        create_window       -> return function to create playblast window
        """
        HU = HeadUps()

        if action == 'hud_set':
            user = self.parent.context.user
            # print '-'*50
            # print dir(self.parent)
            # print pprint(dir(self.parent.context))
            # print '-'*50
            visibleHUDs = [f for f in pm.headsUpDisplay(listHeadsUpDisplays=True)
                                   if pm.headsUpDisplay(f, query=True, visible=True)]
            # hide all visible HUDs
            map(lambda f: pm.headsUpDisplay(f, edit=True, visible=False), visibleHUDs)
            
            '''
            # Add required HUD
            # User name
            editExistingHUD = 'HUDUserName' in pm.headsUpDisplay( listHeadsUpDisplays=True )
            
            pm.headsUpDisplay( 'HUDUserName', edit=editExistingHUD,
                               command=lambda: os.getenv("USERNAME", "unknown.user"),
                               event='playblasting', section=1, block=1 )

            pm.headsUpDisplay( 'HUDUserName', edit=True, visible=True, label="User:" )
            
            # Scene name
            editExistingHUD = 'HUDSceneName' in pm.headsUpDisplay( listHeadsUpDisplays=True )
            pm.headsUpDisplay( 'HUDSceneName', edit=editExistingHUD,
                               command=lambda: cmds.file(query=True, location=True, shortName=True).rsplit(".", 1)[0],
                               event='playblasting', section=6, block=1 )
            pm.headsUpDisplay( 'HUDSceneName', edit=True, visible=True, label="Shot:" )
            # Focal length            
            pm.headsUpDisplay( 'HUDFocalLength', edit=True, visible=True, section=3, block=1 )
            pm.headsUpDisplay( 'HUDCurrentFrame', edit=True, visible=True, dataFontSize="large", section=8, block=1 )
            '''
            # return visibleHUDs

            
            HU.HUD_display(user=user['name'])


            
        elif action == 'hud_unset':
            # restore HUD state
            # map(lambda f: pm.headsUpDisplay(f, edit=True, visible=False), pm.headsUpDisplay(listHeadsUpDisplays=True))
            # map(lambda f: pm.headsUpDisplay(f, edit=True, visible=True), data)
            
            HU.HUD_remove()
            return None
            
        elif action == "playblast_params":
            PLAYBLAST_PARAMS["filename"] = data
            # include audio if available
            audioList = pm.ls(type="audio")
            if audioList:
                PLAYBLAST_PARAMS["sound"] = audioList[0]
            return PLAYBLAST_PARAMS
            
        elif action == "create_window":
            # setting up context window for playblast
            @contextmanager
            def createWindow():
                """ try to get data from shotgun project fields
                    need to get context's project
                                context's shotgun instance
                """
                app = self.parent
                project = app.context.project
                sg = app.context.tank.shotgun
                # set filters and search fields for entity type "Project"
                filters=[["id", "is", project['id']],]
                fields=["sg_width", "sg_height"]
                result=sg.find_one("Project", filters, fields)
                # with result, set parameters accordingly or use default otherwise
                if result:
                    videoWidth = result.get("sg_width", DEFAULT_WIDTH)
                    videoHeight = result.get("sg_height", DEFAULT_HEIGHT)

                # Find first camera matching pattern and set as active camera
                # if not use default current active camera
                camera_name_pattern = app.get_setting( "camera_name_pattern", "persp" )
                cameraList = [c.name() for c in pm.ls(type="camera", r=True) if re.search( camera_name_pattern, c.name() )]
                if not "cam" in MODEL_EDITOR_PARAMS.keys() and cameraList:
                    MODEL_EDITOR_PARAMS["cam"] = cameraList[0]
                    
                # Give Viewport 2.0 renderer only for Maya 2015++
                # mayaVersionString = cmds.about(version=True)
                # mayaVersion = int(mayaVersionString[:4]) if len(mayaVersionString) >= 4 else 0
                # if mayaVersion >= 2015:
                #     params[ "rendererName" ] = "vp2Renderer"

                # Create window
                if pm.windowPref( PLAYBLAST_WINDOW, exists=True ):
                    pm.windowPref( PLAYBLAST_WINDOW, remove=True )
                window = pm.window( PLAYBLAST_WINDOW, titleBar=True, iconify=True,
                                      leftEdge = 100, topEdge = 100,
                                      width = videoWidth, height = videoHeight,
                                      sizeable = False)
                # Create editor area
                layout = pm.formLayout()
                editor = pm.modelEditor( **MODEL_EDITOR_PARAMS )
                pm.setFocus( editor )
                pm.formLayout( layout, edit=True,
                               attachForm = ( ( editor, "left", 0 ),
                                              ( editor, "top", 0 ),
                                              ( editor, "right", 0 ),
                                              ( editor, "bottom", 0 ) ) )
                # Show window
                pm.setFocus( editor )
                pm.showWindow( window )
                pm.refresh()
                try:
                    yield True
                except:
                    traceback.print_exc()
                finally:
                    pm.deleteUI(window)

            return createWindow
        else:
            self._app.log_info("nothing to work on")






import maya.cmds as mc
import maya.mel as mel
from time import gmtime, strftime
import os

class HeadUps(object):
    """docstring for HUD"""
    def __init__(self):
        super(HeadUps, self).__init__()

        
    def HUD_display(self, user='',camera='',turntable=None):
        get_user_name=user
        if get_user_name=='':
            import getpass
            get_user_name=getpass.getuser()
        
        if os.sep != '/':    
            host_name = os.environ['COMPUTERNAME']  
        else:
            import socket
            host_name = socket.gethostname()

        current_date = strftime('%y.%m.%d')
        current_time = strftime('%H:%M')

        file_location = mc.file(loc=1,q=1)
        file_name = file_location.split('/')[-1:][0][:-3]
        font_size = 'large'
        if turntable:
            file_name = file_name.split('_')[-1].replace('v','Version - ')
            font_size = 'small'
        #active_camera = mc.lookThru(q=1).split(':')[-1:][0]
        # active_camera = camera.split(':')[0]

        max_time = mc.playbackOptions(max=1,q=1)

        if mc.currentUnit(t=1,q=1)=='film':
            FPS=str(24)
        elif mc.currentUnit(t=1,q=1)=='pal':
            FPS=str(25)
        elif mc.currentUnit(t=1,q=1)=='ntsc':
            FPS=str(30)
        elif mc.currentUnit(t=1,q=1)=='palf':
            FPS=str(50)
        else:
            FPS=mc.currentUnit(t=1,q=1)

        HUD = ['HUDCameraNames','HUDObjDetBackfaces',
        'HUDObjDetSmoothness',
        'HUDObjDetInstance',
        'HUDObjDetDispLayer',
        'HUDObjDetDistFromCam',
        'HUDObjDetNumSelObjs',
        'HUDFrameRate',
        'HUDCapsLock',
        'HUDViewAxis',
        'HUDPolyCountVerts', 
        'HUDPolyCountEdges', 
        'HUDPolyCountFaces', 
        'HUDPolyCountTriangles', 
        'HUDPolyCountUVs',
        'HUDViewportRenderer',
        'HUDSceneTimecode',
        'HUDCurrentCharacter',
        'HUDPlaybackSpeed',
        'HUDHikKeyingMode',
        'HUDFbikKeyType',
        'HUDIKSolverState',
        'HUDGPUOverride',
        'HUDEMState',
        'HUDEvaluation']

        for a in HUD:
            try:
                mc.headsUpDisplay(a,rem=1)
            except:
                print 'Try remove error.'
                pass

        # Clear standart maya HUDs positions
        mc.headsUpDisplay(rp=(5,0))
        mc.headsUpDisplay(rp=(2,0))
        mc.headsUpDisplay(rp=(2,1))
        mc.headsUpDisplay(rp=(9,2))
        mc.headsUpDisplay(rp=(9,1))
        mc.headsUpDisplay(rp=(9,0))
        mc.headsUpDisplay(rp=(7,0))
        mc.headsUpDisplay(rp=(0,0))
        mc.headsUpDisplay(rp=(4,0))
        # ==================================
        data_position = 7
        
        if not turntable:
            
            data_position = 5

            # mc.headsUpDisplay('LOC',l=file_location,
            #         allowOverlap=1,
            #         b=0,
            #         s=2,
            #         ba='center',bs='small',lfs='small',
            #         dataFontSize='small',ao=1)

            mc.headsUpDisplay ('C_FRAME',l=' Frame:                ',
                    allowOverlap=1,
                    b=2,
                    s=9,
                    ba='left',bs='small',lfs='large',
                    dataFontSize='large',ao=1,preset='currentFrame')

            mc.headsUpDisplay ('S_LEN',l=' Scene Length:      '+str(int(max_time)),
                    allowOverlap=1,
                    b=1,
                    s=9,
                    ba='left',bs='small',lfs='large',
                    dataFontSize='large',ao=1)

            mc.headsUpDisplay('FPS',l=" FPS:                         "+FPS,
                    allowOverlap=1,
                    b=0,
                    s=9,
                    ba='left',bs='small',lfs='large',
                    dataFontSize='large',ao=1)
            ###
            # mc.headsUpDisplay('CAM',l="Camera: "+active_camera,
            #         allowOverlap=1,
            #         b=0,
            #         s=7,
            #         ba='center',bs='large',lfs='large',
            #         dataFontSize='large',ao=1)


        mc.headsUpDisplay('DATE',l=current_date+' / '+current_time,
                    allowOverlap=1,
                    b=0,
                    s=data_position,
                    ba='right',bs='large',lfs='large',
                    dataFontSize='large',ao=1)


        mc.headsUpDisplay ('NAME',l=file_name,
                    allowOverlap=1,
                    b=1,
                    s=2,
                    ba='center',bs='small',lfs=font_size,
                    dataFontSize=font_size,ao=1)
        ###

        mc.headsUpDisplay('HOST',l=host_name,
                    allowOverlap=1,
                    b=0,
                    s=0,
                    ba='center',bs='large',lfs='large',
                    dataFontSize='large',ao=1)

        
        mc.headsUpDisplay('USER',l=get_user_name,
                    allowOverlap=1,
                    b=0,
                    s=4,
                    ba='center',bs='large',lfs='large',
                    dataFontSize='large',ao=1)

    def HUD_remove(self, turntable=None):
        if not turntable:
            # mc.headsUpDisplay('LOC',rem=1)
            mc.headsUpDisplay('C_FRAME',rem=1)
            mc.headsUpDisplay('S_LEN',rem=1)
            mc.headsUpDisplay('FPS',rem=1)
            # mc.headsUpDisplay('CAM',rem=1)

        mc.headsUpDisplay('DATE',rem=1)    
        mc.headsUpDisplay('NAME',rem=1)
        mc.headsUpDisplay('HOST',rem=1)
        mc.headsUpDisplay('USER',rem=1)
        
        for h in mc.headsUpDisplay(lh=1):
            mc.headsUpDisplay(h,rem=1)
        mel.eval('source initHUD')

