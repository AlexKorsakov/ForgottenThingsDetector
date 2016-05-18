#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QImage, qRgb
from datetime import datetime, date, time
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

        self.setWindowIcon(QtGui.QIcon('favicon.ico'))
        self.setWindowTitle('Computer Vision System GUI')
        self.setToolTip('Developed by <b></b> Murom {0} 2016'.format(chr(169)))
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))

        # По центру экрана
        self.center()

        ### Объявляем переменные

        #self.n = img_proc.get_cams(n=self.n, list_of_cams=self.list_of_cams)[0]
        self.format_list = ["mp4", "bmp", "png"]
        self.filename = ""
        self.fileslist = ""
        self.size = 200
        self.fps = 24
        self.n = 0
        self.now_time = 0
        #ROI values
        c1 = 200
        r1 = 200
        h = 200
        self.start_time = time.time()
        self.new_opened = False
        self.list_of_cams = {}
        #self.cap = cv2.VideoCapture('test.mp4')
        self.cap = cv2.VideoCapture(0)
        self.capture = None
        self.capturing = None

        self.currentFrame = None
        self.frame = None
        self.etalon = 0
        self.frame1 = 0      #обработанный etalon
        self.objects = 0
        self.predmet = 0
        self.interval = 100
        self.diff_each = 0
        self.frame_counter = 0
        self.obj_coordinates = []



        ### Создаем объекты компонентов формы
        self.image = QtGui.QLabel('', self)

        self.start_button = QtGui.QPushButton('Start')
        self.end_button = QtGui.QPushButton('End')
        #self.end_button.setEnabled(False)
        self.stop_button = QtGui.QPushButton('Stop')
        #self.stop_button.setEnabled(False)

        self.video_timer = QtCore.QTimer()
        # Создаем кнопку с названием
        self.btnOpen = QtGui.QPushButton('Open', self)
        self.btnOpen.setFocusPolicy(QtCore.Qt.NoFocus)
        # Создаем кнопку с названием
        self.btnMove = QtGui.QPushButton('Go', self)
        self.btnMove.setFocusPolicy(QtCore.Qt.NoFocus)

        self.cb = QtGui.QCheckBox('Show filename', self)
        self.cb.setFocusPolicy(QtCore.Qt.NoFocus)
        # состояние по умолчанию - выкл
        # self.cb.toggle()
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setRange(self.size, self.size+500)
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)

        # прогрессбар
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.btnstart = QtGui.QPushButton('Start', self)
        self.btnstart.setCheckable(True)
        self.btnstart.setFocusPolicy(QtCore.Qt.NoFocus)

        self.timer = QtCore.QBasicTimer()
        self.step = 0

        #SetROI
        self.btnSetROI = QtGui.QPushButton('SetROI', self)

        # Создаем редактируемые поля
        self.reviewEdit = QtGui.QTextEdit()
        self.aboutEdit = QtGui.QTextEdit()
        # Создаем список
        self.list = QtGui.QListWidget(self)


        ### Связываем события(сигналы) с методами нашего класса

        # событие нажатия на item в QListWidget
        self.connect(self.list, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.on_item_select)
        self.setFocus()

        # События нажатия кнопок
        #self.connect(self.btnOpen, QtCore.SIGNAL('clicked()'), self.OpenDialog)
        self.setFocus()

        self.connect(self.btnMove, QtCore.SIGNAL('clicked()'), self.on_movetext)
        self.setFocus()
        # кнопка старта прогрессбара
        self.connect(self.btnstart, QtCore.SIGNAL('clicked()'), self.on_progress)
        self.setFocus()

        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.on_slide)
        self.setFocus()

        self.btnOpen.clicked.connect(self.OpenDialog)
        self.start_button.clicked.connect(self.on_start_capture)
        self.end_button.clicked.connect(self.on_end_capture)
        self.stop_button.clicked.connect(self.stop)
        # чек бокс
        self.connect(self.cb, QtCore.SIGNAL('stateChanged(int)'), self.on_checkbox)

        ### Создаем сетку для размещения виджетов
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        #  строка, столбец, сколько ячеек, столбцов
        grid.addWidget(self.btnstart, 1, 12, 1, 1)
        grid.addWidget(self.btnMove, 2, 12, 1, 1)    #go
        grid.addWidget(self.btnOpen, 3, 12, 1, 1)
        grid.addWidget(self.btnSetROI, 4, 12, 1, 1)
        grid.addWidget(self.start_button, 6, 12)
        grid.addWidget(self.stop_button, 7, 12)
        grid.addWidget(self.end_button, 8, 12)
        grid.addWidget(self.image, 2, 2, 10, 10)     #video
        grid.addWidget(self.slider, 11, 2, 11, 4)
        #grid.addWidget(self.reviewEdit, 4, 1, 1, 1)
        grid.addWidget(self.pbar, 12, 2, 12, 4)
        '''
        grid.addWidget(self.list, 1, 0)
        #grid.addWidget(self.image2, 0, 4, 1, 4)
        grid.addWidget(self.aboutEdit, 4, 1, 1, 1)
        grid.addWidget(self.cb, 5, 0)
        '''
        self.setLayout(grid)
        self.resize(900, 600)


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
                    # print "\n\n{0}\n\n{1}".format(type(str(i.toUtf8())), type(i.toUtf8()))
                    #self.show_img(i.toUtf8())

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
        else:
             #self.set_fps(self.cap.get(cv2.CV_CAP_PROP_FPS))
             self.set_fps(30)
        self.start()

    def on_movetext(self):
        cap = cv2.VideoCapture('test.mp4')
        #cap = cv2.VideoCapture(0)
        #frame1 = self.ObjectDetectionInTime(cap)
        #self.ObjectDetectionInTime(cap)

        text = self.aboutEdit.toPlainText()
        # print type(text)
        self.reviewEdit.setText(text)
        self.aboutEdit.setText("")

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

    def on_slide(self, value):
        pos = self.slider.value()
        self.reviewEdit.setText(str(pos))
        self.on_resize()

    def on_item_select(self):
        self.new_opened = False
        if self.cb.isChecked():
            self.setWindowTitle(self.list.currentItem().text().split("/")[-1])
        self.show_img(str(self.list.currentItem().text().toUtf8()))

    def on_resize(self):
        self.size = int(self.slider.value())
        if self.fileslist != "":
            self.new_opened = False
            if self.slider.value() != "" and self.new_opened == False:
                self.size = int(self.slider.value())

                self.show_img(str(self.list.currentItem().text().toUtf8()))
                # self.show_img(str(self.filename))
            self.new_opened = False

    def on_progress(self):
        if self.timer.isActive():
            self.btnstart.setCheckable(True)
            self.timer.stop()
            self.btnstart.setText('Start')
        elif self.timer.isActive() == False and self.step != 100:
            self.timer.start(100, self)
            self.btnstart.setText('Stop')
        else:
            self.btnstart.setCheckable(True)
            self.step = 0
            self.btnstart.setText('Start')

    def on_end_capture(self):
        self.video_timer.stop()
        self.cap.release()

        #self.default_image()
        self.stop_button.setEnabled(False)
        self.end_button.setEnabled(False)
        #self.start_button.setEnabled(True)
        #self.next_image_button.setEnabled(False)
        self.cap = None
        #self.img_list = list(self.img_box)

    def add_item(self, flist):
        if len(flist) > 1:
            try:
                for string in flist:
                    self.list.addItem(string)
            except Exception as e:
                print e.args, e.message

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.step = 0
            self.btnstart.setText('Start')
            self.btnstart.setCheckable(False)
            self.btnstart.setCheckable(True)
            return
        self.step += 1
        self.pbar.setValue(self.step)



    def ObjectDetectionInTime(self, frame):
        etalon = 0
        frame1 = 0      #обработанный etalon
        objects = 0
        predmet = 0
        interval = 100
        diff_each = 0
        frame_counter = 0
        obj_coordinates = []

        #_, frame = cap.read()

        dopusk = 1
        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                #В градации серого
        frame1 = cv2.GaussianBlur(frame1, (5, 5), 0)                       #Фильтр

        #Берем первый кадр как эталон
        if frame_counter == 0:
            etalon = frame1
            objects = cv2.absdiff(etalon, frame1)
            predmet = objects
            diff_each = predmet

        diff_each = diff_each & cv2.absdiff(etalon, frame1)
        #diff = cv2.absdiff(etalon, frame1)

        #cv2.imshow('diff_each0',diff_each)
        #cv2.imshow('etalon',etalon)
        if frame_counter%interval == 0:
            #diff[:,:] = etalon-frame1 if (etalon-frame1<5) else 0
            diff = cv2.absdiff(etalon, frame1)
            predmet = diff_each         #objects & diff
            objects = diff
            diff_each = diff
        predmet=predmet&diff_each

        #cv2.imshow('diff_each',diff_each)


        ret,frame1 = cv2.threshold(frame1,0,255,  cv2.THRESH_OTSU)  #Бинаризация
        ret,diff = cv2.threshold(predmet,0,255,  cv2.THRESH_OTSU)  #Бинаризация

        #cv2.imshow('frame1',frame1)
        #cv2.imshow('diff',diff)

        dopusk = 1
        diff = cv2.dilate(diff, None, iterations=2)
        #cv2.imshow('dilate',diff)
        (cnts, _) = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 200:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            obj_coordinates = [obj_coordinates,[x+w/2, y+h/2]]

            for obj in obj_coordinates:
                if obj!=[] and obj[0] < (x+w/2)+dopusk and obj[1] < (y+h/2)+dopusk and obj[0] > (x+w/2)-dopusk and obj[1] > (y+h/2)-dopusk:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)


        frame_counter = frame_counter + 1

        # #cv2.imshow('ROI',ROI)
        # k = cv2.waitKey(5) & 0xFF
        # if k == 27:
        #     break

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.image.setPixmap(self.setup_pixmap(img_proc.im_res(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), height=screen.height())))

        #return frame


    def next_frame(self):
        # try if cap is not None
        try:
            if self.cap.read()[0] is not None:
                ret, self.currentFrame = self.cap.read()
                self.orig_frame = cv2.cvtColor(self.currentFrame, cv2.cv.CV_BGR2RGB)

                hsv = cv2.cvtColor(self.currentFrame, cv2.COLOR_RGB2HSV)
                self.frame1 = cv2.cvtColor(self.currentFrame, cv2.COLOR_RGB2GRAY)         #В градации серого
                self.frame1 = cv2.GaussianBlur(self.frame1, (5, 5), 0)

                #Берем первый кадр как эталон
                if self.frame_counter == 0:
                    self.etalon = self.frame1
                    self.objects = cv2.absdiff(self.etalon, self.frame1)
                    self.predmet = self.objects
                    self.diff_each = self.predmet

                self.diff_each = self.diff_each & cv2.absdiff(self.etalon, self.frame1)
                #diff = cv2.absdiff(etalon, frame1)

                if self.frame_counter%self.interval == 0:
                    #diff[:,:] = etalon-frame1 if (etalon-frame1<5) else 0
                    self.diff = cv2.absdiff(self.etalon, self.frame1)
                    self.predmet = self.diff_each         #objects & diff
                    self.objects = self.diff
                    self.diff_each = self.diff
                self.predmet=self.predmet & self.diff_each

                ret,self.frame1 = cv2.threshold(self.frame1,0,255,  cv2.THRESH_OTSU)  #Бинаризация
                ret,self.diff = cv2.threshold(self.predmet,0,255,  cv2.THRESH_OTSU)  #Бинаризация

                dopusk = 1
                self.diff = cv2.dilate(self.diff, None, iterations=2)
                (cnts, _) = cv2.findContours(self.diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for c in cnts:
                    # if the contour is too small, ignore it
                    if cv2.contourArea(c) < 200:
                        continue
                    (x, y, w, h) = cv2.boundingRect(c)
                    self.obj_coordinates = [self.obj_coordinates,[x+w/2, y+h/2]]
                    #Прямоугольники
                    '''
                    for obj in self.obj_coordinates:
                        if obj != [] and obj[0] < (x+w/2)+dopusk and obj[1] < (y+h/2)+dopusk and obj[0] > (x+w/2)-dopusk and obj[1] > (y+h/2)-dopusk:
                            cv2.rectangle(self.currentFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    '''
                cv2.drawContours(self.currentFrame, cnts, -1, (0, 255, 0), 1)
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
                self.cap = cv2.VideoCapture(self.n)
                self.start()
        except Exception as e:
            print e.args, e.message

    def start(self):
        self.video_timer = QtCore.QTimer()
        self.video_timer.timeout.connect(self.next_frame)
        self.video_timer.start(1000./self.fps)

        #self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.end_button.setEnabled(True)
        #self.next_image_button.setEnabled(True)

        self.capturing = True

    def stop(self):
        self.video_timer.stop()
        # im_proc.im_save(self.orig_frame, 1)
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
