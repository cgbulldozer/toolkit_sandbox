# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'playblast_dialog.ui'
#
# Created: Tue May 26 19:55:02 2020
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PlayblastDialog(object):
    def setupUi(self, PlayblastDialog):
        PlayblastDialog.setObjectName("PlayblastDialog")
        PlayblastDialog.resize(468, 182)
        self.gridLayout = QtGui.QGridLayout(PlayblastDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.cmbPercentage = QtGui.QComboBox(PlayblastDialog)
        self.cmbPercentage.setObjectName("cmbPercentage")
        self.gridLayout.addWidget(self.cmbPercentage, 2, 0, 1, 1)
        self.chbUploadToShotgun = QtGui.QCheckBox(PlayblastDialog)
        self.chbUploadToShotgun.setObjectName("chbUploadToShotgun")
        self.gridLayout.addWidget(self.chbUploadToShotgun, 2, 1, 1, 1)
        self.chbShowViewer = QtGui.QCheckBox(PlayblastDialog)
        self.chbShowViewer.setChecked(True)
        self.chbShowViewer.setObjectName("chbShowViewer")
        self.gridLayout.addWidget(self.chbShowViewer, 2, 2, 1, 1)
        self.textEdit = QtGui.QTextEdit(PlayblastDialog)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 3)
        self.btnPlayblast = QtGui.QPushButton(PlayblastDialog)
        self.btnPlayblast.setMinimumSize(QtCore.QSize(450, 0))
        self.btnPlayblast.setObjectName("btnPlayblast")
        self.gridLayout.addWidget(self.btnPlayblast, 3, 0, 1, 3)
        self.label = QtGui.QLabel(PlayblastDialog)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.retranslateUi(PlayblastDialog)
        QtCore.QMetaObject.connectSlotsByName(PlayblastDialog)

    def retranslateUi(self, PlayblastDialog):
        PlayblastDialog.setWindowTitle(QtGui.QApplication.translate("PlayblastDialog", "The Current Sgtk Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.chbUploadToShotgun.setText(QtGui.QApplication.translate("PlayblastDialog", "Upload to Shotgun", None, QtGui.QApplication.UnicodeUTF8))
        self.chbShowViewer.setText(QtGui.QApplication.translate("PlayblastDialog", "Show Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPlayblast.setText(QtGui.QApplication.translate("PlayblastDialog", "Playblast", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PlayblastDialog", "Write Your Comment Here:", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PlayblastDialog = QtGui.QDialog()
    ui = Ui_PlayblastDialog()
    ui.setupUi(PlayblastDialog)
    PlayblastDialog.show()
    sys.exit(app.exec_())

