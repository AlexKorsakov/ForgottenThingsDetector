#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QImage, qRgb
from Tkinter import *
import time
import cv2
import numpy as np
import img_proc

class cvGUI(QtGui.QWidget):
    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)

        # QString To QByteArrray - b = qs.toUtf8
        # QByteArray to string - s = str(b)

        ### Настраиваем основное окно

        self.setWindowTitle('Forgotten Things Detector')
        self.setWindowIcon(QtGui.QIcon('F:\\favicon.ico'))
        self.setStyleSheet(img_proc.read_stylesheet("F:\style.qss"))

        #btn.setToolTip('This is a <b>QPushButton</b> widget')

        # По центру экрана
        self.center()

        ### Объявляем переменные

        #self.n = img_proc.get_cams(n=self.n, list_of_cams=self.list_of_cams)[0]
        self.format_list = ["mp4", "3gp", "bmp", "png"]
        self.filename = ""
        self.fileslist = ""
        self.size = 200
        self.fps = 24
        self.n = 0
        self.now_time = 0
        #ROI values
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.issetroi = False
        self.start_time = time.time()
        self.new_opened = False
        self.list_of_cams = {}
        #self.cap = cv2.VideoCapture('test.mp4')
        self.cap = None #cv2.VideoCapture(0)
        self.capture = None
        self.capturing = None

        self.initial_frame = None
        self.currentFrame = None
        self.frame = None
        self.etalon = 0
        self.frame1 = 0      #обработанный etalon
        self.objects = 0
        self.predmet = 0
        self.diff_each = 0
        self.frame_counter = 0
        self.obj_coordinates = []
        self.interval = 100
        self.contour_area1 = 50
        self.contour_area2 = 5000
        self.previous = 0



        ### Создаем объекты компонентов формы
        '''
        #self.QtGui.statusBar().showMessage('Ready')
        self.myQMenuBar = QtGui.QMenuBar(self)
        exitMenu = self.myQMenuBar.addMenu('File')
        exitAction = QtGui.QAction('Exit', self)
        exitAction.triggered.connect(QtGui.qApp.quit)
        exitMenu.addAction(exitAction)
        '''
        #
        #Создание элементов управления
        #
        self.image =                QtGui.QLabel('', self)
        self.start_button =         QtGui.QPushButton(u'Старт')
        self.pause_button =         QtGui.QPushButton(u'Пауза')
        self.end_button =           QtGui.QPushButton(u'Конец')
        self.btnOpen =              QtGui.QPushButton(u'Открыть', self)
        self.btnMove =              QtGui.QPushButton('Go', self)
        self.set_etalon_btn =       QtGui.QPushButton(u'Эталон')
        self.cb =                   QtGui.QCheckBox('Show filename', self)
        self.roi_checkbox =         QtGui.QCheckBox('ROI', self)
        self.btnSetROI =            QtGui.QPushButton('SetROI', self)
        self.txb_ot =              QtGui.QLabel(u'От',self)
        self.txb_do =              QtGui.QLabel(u'До',self)
        self.pbar =                 QtGui.QProgressBar(self)
        self.btnstart =             QtGui.QPushButton('Start', self)
        self.txtb_sl2 =             QtGui.QSpinBox(self)                         # редактируемые поля
        self.txtb_sl1 =             QtGui.QSpinBox(self)
        self.list =                 QtGui.QListWidget(self)                         # список
        self.spinbox =              QtGui.QSpinBox(self)
        self.lbl=                   QtGui.QLabel(u'Количество',self)
        self.timer_lbl=             QtGui.QLabel(self)
        self.saveframe_button =     QtGui.QPushButton(u'Сохранить')
        self.a =                    QtGui.QStatusBar(self)
        self.video_timer =          QtCore.QTimer()

        self.btnSetROI.setEnabled(False)
        #self.end_button.setEnabled(False)
        #self.pause_button.setEnabled(False)

        self.btnOpen.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btnMove.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cb.setFocusPolicy(QtCore.Qt.NoFocus)
        # состояние по умолчанию - выкл
        # self.cb.toggle()
        # прогрессбар
        self.pbar.setGeometry(30, 40, 200, 25)

        self.btnstart.setCheckable(True)
        self.btnstart.setFocusPolicy(QtCore.Qt.NoFocus)

        self.timer = QtCore.QBasicTimer()
        self.timer_step = 0
        self.spinbox.setRange(0, 640)
        self.txtb_sl1.setRange(1, 10000)
        self.txtb_sl2.setRange(1, 10000)
        self.txtb_sl1.setValue(self.contour_area1)
        self.txtb_sl2.setValue(self.contour_area2)

        ### Связываем события(сигналы) с методами нашего класса

        # событие нажатия на item в QListWidget
        self.connect(self.list, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.on_item_select)
        self.connect(self.btnMove, QtCore.SIGNAL('clicked()'), self.on_movetext)
        # кнопка старта прогрессбара
        self.connect(self.btnstart, QtCore.SIGNAL('clicked()'), self.on_progress)

        #self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.on_slide)
        #self.slider.valueChanged.connect(self.on_slide)
        #self.slider1.valueChanged.connect(self.on_slider1_valuechanged)
        #self.slider2.valueChanged.connect(self.on_slider2_valuechanged)
        self.txtb_sl1.valueChanged.connect(self.on_txtb_sl1_valchanged)
        self.txtb_sl2.valueChanged.connect(self.on_txtb_sl2_valchanged)

        self.btnOpen.clicked.connect(self.OpenDialog)
        self.start_button.clicked.connect(self.on_start_capture)
        self.end_button.clicked.connect(self.on_end_capture)
        self.pause_button.clicked.connect(self.stop)
        self.saveframe_button.clicked.connect(self.take_frame)
        self.set_etalon_btn.clicked.connect(self.set_etalon_frame)
        # чекбоксы
        self.connect(self.cb, QtCore.SIGNAL('stateChanged(int)'), self.on_checkbox)
        self.connect(self.roi_checkbox, QtCore.SIGNAL('stateChanged(int)'), self.on_roi_checkbox)

        ### Создаем сетку для размещения виджетов
        grid = QtGui.QGridLayout()
        self.statusBar = QStatusBar()
        #self.setStatusBar(self.statusBar)
        grid.setSpacing(10)
        #  строка, столбец, сколько ячеек, столбцов
        grid.addWidget(self.image,              1, 1, 10, 10)        #video
        grid.addWidget(self.btnstart,           1, 12, 1, 1)
        grid.addWidget(self.btnMove,            2, 12, 1, 1)       #go
        grid.addWidget(self.btnOpen,            3, 12, 1, 1)       #Open
        grid.addWidget(self.cb,                 4, 12, 1, 1)            #check
        grid.addWidget(self.start_button,       5, 12)
        grid.addWidget(self.pause_button,       6, 12)
        grid.addWidget(self.end_button,         7, 12)
        grid.addWidget(self.saveframe_button,   8, 12, 1, 1)
        grid.addWidget(self.btnSetROI,          9, 12, 1, 1)     #SetROI
        grid.addWidget(self.roi_checkbox,       10, 12, 1, 1)
        grid.addWidget(self.set_etalon_btn,     11, 12, 1, 1)
        grid.addWidget(self.txb_ot,             12, 4, 1, 1)
        grid.addWidget(self.txb_do,             12, 5, 1, 1)
        grid.addWidget(self.timer_lbl,          12, 12, 1, 1)
        grid.addWidget(self.txtb_sl1,           13, 4, 1, 1)
        grid.addWidget(self.txtb_sl2,           13, 5, 1, 1)
        grid.addWidget(self.lbl,                14, 2, 1, 1)
        grid.addWidget(self.spinbox,            14, 2, 1, 1)
        grid.addWidget(self.pbar,               15, 2, 2, 4)
        grid.addWidget(self.list,               15, 8, 1, 1)
        grid.addWidget(self.a,                  17, 2)

        self.setLayout(grid)
        self.resize(900, 600)


    def mouseDoubleClickEvent(self, e):
        '''

        if self.issetroi is True:                   #roi задан
            self.x1 = 0
            self.y1 = 0
        '''
        if self.x1 != 0 and self.y1 != 0:
            self.x2 = e.x()
            self.y2 = e.y()
        else:
            self.x1 = e.x()
            self.y1 = e.y()
        print "#### {0} | {1} #### {2} | {3}".format(self.x1, self.y1, self.x2, self.y2)


    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        print "!!!!", screen.width(), screen.height()

    def OpenDialog(self):
        try:
            self.fileslist = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', '/home')
            self.frmlist = []
            print "List of available image formats:{0}".format(self.format_list)
            if self.fileslist is not None:
                if len(self.fileslist) > 1:
                    print "Opening {} files...".format(len(self.fileslist))
                for i in self.fileslist:
                    self.new_opened = True
                    self.list.clear()
                    self.add_item(self.fileslist)
                    self.filename = str(i.toUtf8())
                    self.frmlist.append(str(i.split("/")[-1].split(".")[-1]))
                    print "You try to open file with format: {0}".format(self.frmlist.pop())
                    print "    Opening file {0}...".format(self.filename)

                    self.cap = cv2.VideoCapture(self.filename)
                    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
                    if int(major_ver) < 3:
                        fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
                        print "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps)
                    else:
                        fps = self.cap.get(cv2.CAP_PROP_FPS)
                        print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
                    self.set_fps(fps)

                    #screen = QtGui.QDesktopWidget().screenGeometry()
                    #self.set_slide_val(screen.height())

                    frm = str(i.split("/")[-1].split(".")[-1])
                    fn = i.split("/")[-1]
                    self.list.setCurrentRow(self.list.count()-1)

                    if frm not in self.format_list:
                        self.list.clear()
                        print "Failed to open file \"{0}\". Wrong file format: [\'{1}\']".format(str(fn), frm)
                        self.fileslist = None
                        break

                # self.aboutEdit.setText(self.fileslist[0])
                # self.cb.toggle()
                # self.center()
                # file=open(self.filename)
                # data = file.read()

        except Exception as e:
            print e.args, e.message

    def show_img(self, img=None, container=QtGui.QLabel):
        if img is not None:
            container.setPixmap(self.setup_pixmap(img_proc.im_res(img, self.size)))
        else:
            pass

    def frame_res(self):
        self.currentFrame = img_proc.im_res(self.orig_frame, self.size)

    def set_fps(self, fps):
        self.fps = fps

    def set_slide_val(self, height):
        self.slider1.setRange(height / 2, height * 2)
        self.size = height

    def set_etalon_frame(self):
        kadr = cv2.cvtColor(self.initial_frame, cv2.COLOR_RGB2GRAY)         #В градации серого
        self.etalon = cv2.medianBlur(kadr, 5)    #медианная

    #def set_roi(self):



    def setup_pixmap(self, img):
        #h, w, bpLine = None
        if len(img.shape)>2:
            """Если цветное"""
            h, w = img.shape[:2]
            bp_line = 3 * w
        else:
            """Если полутоновое"""
            img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            h, w = img2.shape[:2]
            bp_line = w
        if img is not None:
            """bpLine = byte per line"""
            bpLine = 3 * w
            """Здесь собирается QImage из IplImage и создается карта пикселей"""
            qim = QtGui.QImage(img.data, w, h, bpLine, QtGui.QImage.Format_RGB888)
            pm = QtGui.QPixmap.fromImage(qim)
            return pm

    def on_start_capture(self):
        #if not self.capture:
            #self.end_button.clicked.connect(self.stop)
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.set_fps(30)
        #else:
             #self.set_fps(self.cap.get(cv2.CV_CAP_PROP_FPS))
             #self.set_fps(30)
        self.start()
    '''
    def on_slider1_valuechanged(self, val):              #Слайдер1
        if val < self.contour_area2:
            pos = val
            self.contour_area1 = pos
            self.txtb_sl1.setValue(pos)

    def on_slider2_valuechanged(self, val):              #Слайдер2
        if val > self.contour_area1:
            pos = val
            self.contour_area1 = pos
            self.txtb_sl2.setValue(pos)
    '''
    def on_txtb_sl1_valchanged(self, val):
        self.contour_area1 = val

    def on_txtb_sl2_valchanged(self, val):
        self.contour_area2 = val

    def on_end_capture(self):
        self.video_timer.stop()
        #self.cap.release()

        #self.default_image()
        self.pause_button.setEnabled(False)
        self.end_button.setEnabled(False)
        #self.start_button.setEnabled(True)
        #self.next_image_button.setEnabled(False)
        self.cap = None
        #self.img_list = list(self.img_box)

    def on_movetext(self):
        cap = cv2.VideoCapture('F:\\test.mp4')
        #cap = cv2.VideoCapture(0)
        #frame1 = self.ObjectDetectionInTime(cap)
        #self.ObjectDetectionInTime(cap)

    def on_checkbox(self, value):
        if self.cb.isChecked():
            if self.filename != "":
                self.setWindowTitle(self.list.currentItem().text().split("/")[-1])
            elif self.filename == "":
                self.setWindowTitle('Image not found')
            else:
                self.setWindowTitle('Computer Vision System GUI')
        else:
            self.setWindowTitle('Computer Vision System GUI')

    def on_roi_checkbox(self):
        if self.roi_checkbox.isChecked():
            self.btnSetROI.setEnabled(True)
        else:
            self.btnSetROI.setEnabled(False)
            self.x1 = 0
            self.x2 = 0
            self.y1 = 0
            self.y2 = 0

    def on_slide(self, value):
        pos = self.slider1.value
        self.txtb_sl2.setText(str(pos))
        self.on_resize()

    def on_item_select(self):
        self.new_opened = False
        if self.cb.isChecked():
            self.setWindowTitle(self.list.currentItem().text().split("/")[-1])
        self.show_img(str(self.list.currentItem().text().toUtf8()))

    def on_resize(self):
        self.size = int(self.slider1.value)
        if self.fileslist != "":
            self.new_opened = False
            if self.slider1.value != "" and self.new_opened == False:
                self.size = int(self.slider1.value)
                #self.show_img(str(self.list.currentItem().text().toUtf8()))
                # self.show_img(str(self.filename))
            self.new_opened = False

        print(str(self.size))

    def on_progress(self):
        if self.timer.isActive():
            self.btnstart.setCheckable(True)
            self.timer.stop()
            self.btnstart.setText('Start')
        elif self.timer.isActive() == False and self.timer_step != 100:
            self.timer.start(100, self)
            self.btnstart.setText('Stop')
        else:
            self.btnstart.setCheckable(True)
            self.timer_step = 0
            self.btnstart.setText('Start')

    def add_item(self, flist):
        if len(flist) > 1:
            try:
                for string in flist:
                    self.list.addItem(string)
            except Exception as e:
                print e.args, e.message

    def timerEvent(self, event):
        if self.timer_step >= 100:
            self.timer.stop()
            self.timer_step = 0
            self.btnstart.setText('Start')
            self.btnstart.setCheckable(False)
            self.btnstart.setCheckable(True)
            return
        self.timer_step += 1
        self.pbar.setValue(self.timer_step)

    def next_frame(self):
        # try if cap is not None
        try:
            self.timer_lbl.setText("{0}".format(self.frame_counter / (self.fps/2)))


            if self.cap.read()[0] is not None:
                ret, self.initial_frame = self.cap.read()
                self.currentFrame = self.initial_frame

                if self.roi_checkbox.isChecked() and self.x1 != 0 and self.y2 != 0:             #выделение ROI
                    temp = self.initial_frame
                    '''
                    temp[0:temp.size(1)] = 0
                    mask = np.zeros((h,w,z), np.uint8)
                    cv2.floodFill(temp, mask, (0,0), 255)
                    '''
                    temp[self.x1:self.x2, self.y1:self.y2] = self.initial_frame[self.x1:self.x2, self.y1:self.y2]
                    #self.issetroi = True
                    self.currentFrame = temp

                self.frame1 = cv2.cvtColor(self.currentFrame, cv2.COLOR_RGB2GRAY)         #В градации серого
                self.frame1 = cv2.medianBlur(self.frame1, 5)    #медианная

                if self.frame_counter == 0:                 #Берем первый кадр как эталон
                    self.etalon = self.frame1
                    self.objects = cv2.absdiff(self.etalon, self.frame1)
                    self.predmet = self.objects
                    self.diff_each = self.predmet

                self.diff_each = self.diff_each & cv2.absdiff(self.etalon, self.frame1)

                cv2.imshow('diff_each0', self.diff_each)
                if self.frame_counter % self.interval == 0:
                    self.diff = cv2.absdiff(self.etalon, self.frame1)
                    self.predmet = self.diff_each         #objects & diff
                    self.objects = self.diff
                    #cv2.imshow('diff', self.diff)
                    self.diff_each = self.diff
                self.predmet=self.predmet & self.diff_each

                ret, self.frame1 = cv2.threshold(self.frame1, 0, 255,  cv2.THRESH_OTSU)  #Бинаризация
                ret, self.diff = cv2.threshold(self.predmet, 0, 255,  cv2.THRESH_OTSU)  #Бинаризация
                #морфологическое открытие/закрытие
                dopusk = 1
                self.diff = cv2.dilate(self.diff, None, iterations=2)
                (cnts, _) = cv2.findContours(self.diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                print "cnts1: {0}".format(cnts)
                counter = 0
                for c in cnts:
                    Ploshad = cv2.contourArea(c)
                    if Ploshad < self.contour_area1 or Ploshad > self.contour_area2:        #if cv2.contourArea(c) < 200:
                        continue
                    counter += 1
                    print "area: {0}".format(cv2.contourArea(c))
                    (x, y, w, h) = cv2.boundingRect(c)
                    if previous is not None:
                        self.is_equal([x, y, w, h],previous)
                    previous = [x, y, w, h]
                    self.obj_coordinates = [self.obj_coordinates,[x+w/2, y+h/2]]
                    #Прямоугольники
                    for obj in self.obj_coordinates:
                        if obj != [] and obj[0] < (x+w/2)+dopusk and obj[1] < (y+h/2)+dopusk and obj[0] > (x+w/2)-dopusk and obj[1] > (y+h/2)-dopusk:
                            cv2.rectangle(self.currentFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            #cv2.drawContours(self.currentFrame, cnts, counter, (0, 255, 255), 1)

                #cnts = [c for c in cnts if cv2.contourArea(c) < self.contour_area]
                #print "cnts2: {0}".format(cnts)

                #cv2.drawContours(self.currentFrame, cnts, -1, (0, 255, 255), 1)
                self.frame_counter = self.frame_counter + 1

                '''for resizing'''
                #self.curImage1 = self.frame
                '''resize only current images on Qlabels'''

                #self.size = int(self.size * 2)
                #self.frame_res()
                screen = QtGui.QDesktopWidget().screenGeometry()
                self.image.setPixmap(self.setup_pixmap(img_proc.im_res(cv2.cvtColor(self.currentFrame, cv2.COLOR_BGR2RGB), height=screen.height()/2)))

            else:
                self.video_timer.stop()
                #self.cap = cv2.VideoCapture(self.n)
                self.cap = cv2.VideoCapture(0)
                self.start()
        except Exception as e:
            print e.args, e.message

    def start(self):
        self.video_timer = QtCore.QTimer()
        self.video_timer.timeout.connect(self.next_frame)
        self.video_timer.start(1000./self.fps)
        #self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.end_button.setEnabled(True)
        #self.next_image_button.setEnabled(True)
        self.capturing = True

    def stop(self):
        self.video_timer.stop()
        #self.cap = None
        # img_proc.im_save(self.orig_frame, 1)
        self.start_button.setEnabled(True)
        self.end_button.setEnabled(False)
        self.capturing = False


    def next_image(self):
        #if len(self.img_list) == 0:
        #    self.img_list = list(self.img_box)
        #i = 6 - len(self.img_list)
        # self.views[i] = self.orig_frame
        self.show_img(self.currentFrame, self.image)
        # self.img_list = self.img_list[1:]

    def take_frame(self):
        if self.currentFrame is not None:
            img_proc.im_save(self.currentFrame, 1)
        else:
            pass

    def is_equal(self, cont1, cont2):      #cont1[x, y, w, h]       #
        #if (cont1[0]+cont1[2]/2) == (cont2[0]+cont2[2]/2) and (cont1[1]+cont1[3]/2) == (cont2[1]+cont2[3]/2):
        center1 = [cont1[0]+cont1[2]/2, cont1[1]+cont1[3]/2]
        center2 = [cont2[0]+cont2[2]/2, cont2[1]+cont2[3]/2]
        if self.in_diapazon(center1, center2):          #(cont1[0]+cont1[2]/2) == (cont2[0]+cont2[2]/2) and (cont1[1]+cont1[3]/2) == (cont2[1]+cont2[3]/2):
            return True
        else:
            return False
        #if obj != [] and obj[0] < (x+w/2)+dopusk and obj[1] < (y+h/2)+dopusk and obj[0] > (x+w/2)-dopusk and obj[1] > (y+h/2)-dopusk:

    def in_diapazon(self, center1, center2):
        if (center1[0]+2 > center2[0] or center1[0]-2 < center2[0]) and (center1[1]+2 > center2[1] or center1[1]-2 < center2[1]):
            return True
        else:
            return False
'''
gray_color_table = [qRgb(i, i, i) for i in range(256)]

def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                return qim.copy() if copy else qim
'''