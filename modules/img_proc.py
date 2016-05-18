#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2

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
