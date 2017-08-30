# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 01:40:39 2017

@author: tomita
"""

import sys
import os

from PyQtUtil import QtCore, QtWidgets, QtGui, createWindowFromUiFile, getMayaMainWindow

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

import vertexColorEdit
import averageVertexColor

class AverageVertexColorToolWindow(QtWidgets.QMainWindow):
    def init_ui(self,appSettingData):
        self.pushButton_apply.clicked.connect(self.averageVertexColor)
        self.pushButton_adjacency_debug.clicked.connect(self.adjacencyDebug)

        self.lcdNumber_elapsedTime.display(0.0)
        
        self.lastSelected = None
        self.startVtx = 0
        
        
    def close_ui(self, appSettingData):
        print(appSettingData)
        
    def averageVertexColor(self):
        self.lcdNumber_elapsedTime.display(0.0)
        
        elapsedTime = vertexColorEdit.vertexColorEditSelectedShapes(maxDepth = self.spinBox_max_depth.value(),methodType = self.comboBox_average_method_type.currentIndex())
        
        self.lcdNumber_elapsedTime.display(elapsedTime)
        
        
    def adjacencyDebug(self):
        """
        maxDepthに応じて隣接リストで選択される頂点の領域を選択する
        """

        if self.lastSelected is None:
            nodeName,vtx = cmds.ls(sl = True)[0].split('.')
            self.startVtx = int(vtx[4:-1])
            
            shape = vertexColorEdit.getDagPathFromName(nodeName)
            #shape = vertexColorEdit.getSelectedShapes()[0]            
            self.lastSelected = shape
            
        else:
            shape = self.lastSelected
            
        shapeName = OpenMaya.MFnDagNode(shape).fullPathName()
        
        cmds.select(clear = True)
        
        for indices in vertexColorEdit.adjacencyDebug(shape,maxDepth = self.spinBox_max_depth.value(),startVertexId = self.startVtx, methodType = self.comboBox_average_method_type.currentIndex()):
            for index in indices:
                cmds.select('%s.vtx[%d]' % (shapeName,index), add = True)
                

def main():
    window = createWindowFromUiFile('AverageVertexColorTool',os.path.join(os.path.dirname(__file__),'averageVertexColorTool.ui'),AverageVertexColorToolWindow(parent = getMayaMainWindow()))
    window.show()
    
    


                

