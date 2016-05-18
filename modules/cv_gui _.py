#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
import cv2
import img_proc as im_proc


class cvGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # QString To QByteArrray - b = qs.toUtf8
        # QByteArray to string - s = str(b)
        #
        #
        # Настраиваем основное окно
        #
        #
        self.setWindowIcon(QtGui.QIcon('icons/ico3.png'))
        self.setWindowTitle('Computer Vision System GUI')

        self.setToolTip('Developed by <b>Terekhin A.V.</b> Murom {0} 2016'.format(chr(169)))
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))        
        

        self.format_list = ["jpg", "bmp", "png"]        

        # По центру экрана
        self.center()
        #
        #
        # Объявляем переменные
        #
        #
        # Текст окна
        self.filename = ""
        self.size = 200
        self.new_opened = False
        self.fileslist = ""
        #
        #
        # Создаем объекты компонентов формы
        #
        #
        self.image = QtGui.QLabel('', self)
        self.image2 = QtGui.QLabel('', self)
        self.defaulf_image()

        # Создаем кнопку с названием
        self.btnOpen = QtGui.QPushButton('Open', self)
        self.btnOpen.setFocusPolicy(QtCore.Qt.NoFocus)
        # Создаем кнопку с названием
        self.btnMove = QtGui.QPushButton('MoveText', self)
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

        # Создаем редактируемые поля
        self.reviewEdit = QtGui.QTextEdit()
        self.aboutEdit = QtGui.QTextEdit()
        # Создаем список
        self.list = QtGui.QListWidget(self)
        #
        #
        # Связываем события(сигналы) с методами нашего класса
        #
        #
        # событие нажатия на item в QListWidget
        self.connect(self.list, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.on_item_select)
        self.setFocus()
        # События нажатия кнопок
        self.connect(self.btnOpen, QtCore.SIGNAL('clicked()'), self.OpenDialog)
        self.setFocus()

        self.connect(self.btnMove, QtCore.SIGNAL('clicked()'), self.on_movetext)
        self.setFocus()
        # кнопка старта прогрессбара
        self.connect(self.btnstart, QtCore.SIGNAL('clicked()'), self.on_progress)
        self.setFocus()

        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.on_slide)
        self.setFocus()

        # чек бокс
        self.connect(self.cb, QtCore.SIGNAL('stateChanged(int)'), self.on_checkbox)

        #
        #
        # Создаем сетку для размещения виджетов
        #
        #
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # Размещаем кнопку открытия изображения 2 строка 1 столбец
        grid.addWidget(self.btnOpen, 1, 0)
        grid.addWidget(self.btnMove, 2, 0)
        grid.addWidget(self.reviewEdit, 4, 0, 1, 4)
        grid.addWidget(self.aboutEdit, 4, 4, 1, 4)
        grid.addWidget(self.image, 0, 0, 1, 4)
        grid.addWidget(self.image2, 0, 4, 1, 4)
        grid.addWidget(self.list, 0, 9, 1, 2)
        grid.addWidget(self.cb, 5, 0)
        grid.addWidget(self.btnstart, 6, 0)
        grid.addWidget(self.pbar, 7, 0, 1, 8)
        grid.addWidget(self.slider, 8, 0, 1, 8)




        self.setLayout(grid)
        self.resize(300, 300)

    def defaulf_image(self):
        self.img = cv2.imread(r'no_img.png')

        if self.img is not None:
            self.cvImage = self.img
            self.RIM = im_proc.im_res(self.img, 250)

            height, width, bytesPerComponent = self.RIM.shape
            bytesPerLine = 3 * width

            self.img = cv2.cvtColor(self.RIM, cv2.COLOR_BGR2RGB)
            QImg = QtGui.QImage(self.img.data, width, height, bytesPerLine,QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(QImg)

        if pixmap != "":
            self.image.setAlignment(QtCore.Qt.AlignCenter)
            self.image2.setAlignment(QtCore.Qt.AlignCenter)
            self.image.setPixmap(pixmap)
            self.image2.setPixmap(pixmap)

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def OpenDialog(self):
        try:
            self.fileslist = QtGui.QFileDialog.getOpenFileNames(self, 'Open file',
                        '/home')
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

                    # print "\n\n{0}\n\n{1}".format(type(str(i.toUtf8())), type(i.toUtf8()))
                    self.show_img(i.toUtf8())

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

    def show_img(self, fname):
        frm = fname.split("/")[-1].split(".")[-1]
        fp = str(fname).replace("/", "//")
        if fp is not None and frm in self.format_list:
            if self.new_opened == True:
                print "    File \"{0}\" successfully opened".format(self.filename)
            pm = self.on_pixmap(fp, self.size)[0]
            pm2 = self.on_pixmap(fp, self.size)[1]
            self.image.setAlignment(QtCore.Qt.AlignCenter)
            self.image2.setAlignment(QtCore.Qt.AlignCenter)
            """Здесь на QLable накладывается QPixmap"""
            self.image.setPixmap(pm)
            self.image2.setPixmap(pm2)
        else:
            self.filename = ""
            self.defaulf_image()
            if self.new_opened == True:
                print "Cannot show image \"{0}\". Reason: Wrong file format:\"{1}\"".format(str(fname.split("/")[-1]), frm)

    def setup_pixmap(self, img):
        if len(img.shape)>2:
            """Если цветное"""
            h, w, bpLine = img.shape
        else:
            """Если полутоновое"""
            img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            h, w, bpLine= img2.shape        #недоделано
        if img is not None:
            """bpLine = byte per line"""
            bpLine = 3 * w
            """Здесь собирается QImage из IplImage и создается карта пикселей"""
            qim = QtGui.QImage(img.data, w, h, bpLine, QtGui.QImage.Format_RGB888)
            pm = QtGui.QPixmap.fromImage(qim)
            return pm

    def on_pixmap(self, path, size):
        if path != "":
            """Здесь в cvImage загружается изображение"""
            cvImage = im_proc.im_op(path)


            if cvImage is not None:
                """Здесь происходят преобразования"""
                bgr_gray = im_proc.im_gray(cvImage)
                bgr_blur = im_proc.im_mblur(cvImage, 5)

                # bgr = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
                rgb_gray = im_proc.im_gray2rgb(bgr_gray)
                rgb_blur = im_proc.im_bgr2rgb(bgr_blur)

                """Здесь изменяется размер"""
                res_gray = im_proc.im_res(rgb_gray, size)
                res_blur = im_proc.im_res(rgb_blur, size)
                return self.setup_pixmap(res_gray), self.setup_pixmap(res_blur)

    def on_movetext(self):
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

    def add_item(self, flist):
        if len(flist) > 1:
            try:
                for string in flist:
                    self.list.addItem(string)
            except Exception as e:
                print e.args, e.message

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

