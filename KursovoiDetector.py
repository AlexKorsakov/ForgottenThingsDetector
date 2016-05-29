#!/usr/bin/python
# coding=UTF-8
import modules.cv_gui as cv_gui
from PyQt4 import QtGui
import sys

app = QtGui.QApplication(sys.argv)
qb = cv_gui.cvGUI()
qb.show()	

sys.exit(app.exec_())