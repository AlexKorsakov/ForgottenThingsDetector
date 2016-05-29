#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import datetime as dt
import sys
from PyQt4 import Qt


def im_op(filename):
    img = cv2.imread(filename)
    return img


def im_res(image, width=None, height=None, inter=cv2.INTER_AREA):
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        d = (int(w * r), height)
    else:
        r = width / float(w)
        d = (width, int(h * r))
    res_img = cv2.resize(image, d, interpolation=inter)
    return res_img


def im_mblur(img, k=5):
    mblur = cv2.medianBlur(img, k)
    return mblur


def im_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def im_bgr2rgb(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb


def im_gray2rgb(gray):
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    return rgb


def im_save(img, n=1):
    cur_time = dt.datetime.now()
    cur_data = str(cur_time).split()[0]
    cur_time = str(cur_time).split()[1].split(".")[0].replace(":", "_")
    if str(sys.platform)[0:3] == "lin":
        fname = "saved_images//image{0}_{1}-{2}.jpg".format(str(n), cur_data, cur_time)
    elif str(sys.platform)[0:3] == "win":
        fname = "saved_images\\image{0}_{1}-{2}.jpg".format(str(n), cur_data, cur_time)
    print fname
    cv2.imwrite(fname, img)

'''
def set_label_bg():
'''


def read_stylesheet(filename):
    css = Qt.QString()
    file = Qt.QFile(filename)
    if file.open(Qt.QIODevice.ReadOnly) :
        css = Qt.QString(file.readAll())
        file.close()
    return css