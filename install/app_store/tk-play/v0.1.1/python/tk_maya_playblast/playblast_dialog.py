
import tank
import os
import sys
import threading

from tank.platform.qt import QtCore, QtGui
from .ui.playblast_dialog import Ui_PlayblastDialog

SCALE_OPTIONS = [50, 100]

class PlayblastDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    def __init__(self, app, handler, parent=None):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)

        self._app = app
        self._handler = handler
        
        # now load in the UI that was created in the UI designer
        self._ui = Ui_PlayblastDialog() 
        self._ui.setupUi(self)
        self.__initComponents()
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        # self._app = tank.platform.current_bundle()
        
        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 
        
        # lastly, set up our very basic UI
        # self._ui.context.setText("Current Shot: %s" % self._app.context)
        
        self._ui.chbUploadToShotgun.clicked.connect(self.__checkSG)
        self._ui.btnPlayblast.clicked.connect(self.doPlayblast)
        self._ui.textEdit.textChanged.connect(self.__enable_button)
        self.message_text = ''

    def __text_test(self):
        message_text = self._ui.textEdit.toPlainText()

        if message_text:
            self.message_text = message_text
            spl = list(set(message_text.split('\n')))
            if spl != [''] or len(spl) != 1:
                return True
        else:
            self.message_text = ''

        return False

    def __checkSG(self):
        
        if self._ui.chbUploadToShotgun.isChecked() and not self.__text_test():
            self._ui.btnPlayblast.setEnabled(False)
        else:
            self._ui.btnPlayblast.setEnabled(True)
        print 'check sg'

    def __enable_button(self):
        if self.__text_test():
            self._ui.btnPlayblast.setEnabled(True)
        elif not self.__text_test() and self._ui.chbUploadToShotgun.isChecked():
            self._ui.btnPlayblast.setEnabled(False)
        

    def __initComponents(self):
        # Setting up playblast resolution percentage. Customizable through
        # optional "scale_options" field in app settings.
        scaleIntList = self._app.get_setting("scale_options", SCALE_OPTIONS)
        for percentInt in scaleIntList:
            self._ui.cmbPercentage.addItem( "%d%%" % percentInt, userData=percentInt )

    def doPlayblast(self):
        overridePlayblastParams = {}

        uploadToShotgun = self._ui.chbUploadToShotgun.isChecked()
        self._handler.setUploadToShotgun( uploadToShotgun )
        self._handler.setMessageText( self.message_text )

        showViewer = self._ui.chbShowViewer.isChecked()
        overridePlayblastParams["viewer"] = showViewer

        percentInt = self._ui.cmbPercentage.itemData( self._ui.cmbPercentage.currentIndex() )
        overridePlayblastParams["percent"] = percentInt
        self._handler.doPlayblast(**overridePlayblastParams)

