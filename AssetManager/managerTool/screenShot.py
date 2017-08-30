# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 16:29:51 2017

@author: tomita
"""

import os

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI

import ctypes
glFT = ctypes.cdll.OpenGL32

glFT.glReadBuffer.argtypes = [ctypes.c_uint] # mode
glFT.glReadPixels.argtypes = [ctypes.c_int,ctypes.c_int, # x,y
                              ctypes.c_int,ctypes.c_int, # width, height
                              ctypes.c_uint,ctypes.c_uint, # format, type
                              ctypes.c_void_p] # data

GL_RGB  = 0x1907
GL_RGBA = 0x1908

GL_UNSIGNED_BYTE = 0x1401
GL_FRONT = 0x0404

def capture(snapShotImageFileName,resize = (-1,-1)):
    view = OpenMayaUI.M3dView.active3dView()
    
    w = view.portWidth()
    h = view.portHeight()
    
    view.refresh()
    
    view.beginGL()
    
    img = OpenMaya.MImage()
    img.create(w,h)
    
    glFT.glReadBuffer(GL_FRONT)
    glFT.glReadPixels(0,0,w,h,GL_RGBA,GL_UNSIGNED_BYTE,ctypes.c_void_p(img.pixels()))
    
    view.endGL()
    
    if resize != (-1,-1):
        img.resize(resize[0],resize[1],True)
    
    ext = os.path.splitext(snapShotImageFileName)[1][1:]
    img.writeToFile(snapShotImageFileName,ext)
    
