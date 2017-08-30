# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 01:40:39 2017

@author: tomita
"""

import os

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

import pickle

import time

def getDagPathFromName(nodeName):
    sel = OpenMaya.MSelectionList()
    sel.add(nodeName)

    if sel.isEmpty():
        return None
    
    return sel.getDagPath(0)

def getSelectedShapes():
    shapes = []

    sel = OpenMaya.MGlobal.getActiveSelectionList()
    
    for i in range(0,sel.length()):
        obj = sel.getDagPath(i)
        apiType = obj.apiType()
        
        if apiType == OpenMaya.MFn.kTransform:
            shapes.append(obj.extendToShape())
            
        elif apiType == OpenMaya.MFn.kMesh:
            shapes.append(obj)
    
    return shapes

from averageVertexColor import AverageVertexColor

def vertexColorEdit(shapeName, maxDepth = 3, methodType = 0):
    shape = getDagPathFromName(shapeName)
    _vertexColorEdit(shape,maxDepth,methodType)

def vertexColorEditSelectedShapes(maxDepth = 3, methodType = 0):
    elapsedTime = 0.0
    for shape in getSelectedShapes():
        elapsedTime += _vertexColorEdit(shape,maxDepth,methodType)
    
    return elapsedTime
    
def _vertexColorEdit(shape, maxDepth = 3, methodType = 0):    
    vertItr = OpenMaya.MItMeshVertex(shape)
    
    vertexColors = []
    connectedVertices = []
    colorIndexRemap = {}
    
    tm = time.time()
    
    while not vertItr.isDone():
        vertexColors.append(list(vertItr.getColor()))
        connectedVertices.append(list(vertItr.getConnectedVertices()))
        
        for idx in vertItr.getColorIndices():
            colorIndexRemap[idx] = vertItr.index()
        
        vertItr.next()

    print('[build AdjacencyList] %f sec' % (time.time() -tm))
    
    tm = time.time()
    
    averageVertexColor = AverageVertexColor(vertexColors,connectedVertices,maxDepth,methodType)
    averageVertexColor.average()
    
    elapsedTime = (time.time() -tm)
    print('%f sec' % elapsedTime)
    
    vertexColors = averageVertexColor.vertexColors

    tm = time.time()
    
    mesh = OpenMaya.MFnMesh(shape)
    
    numColor = mesh.numColors()
    colors = OpenMaya.MColorArray()
    colors.setLength(numColor)
    for i in range(0,numColor):
        colors[i] = OpenMaya.MColor(vertexColors[colorIndexRemap[i]])
    
    colorSetName = mesh.currentColorSetName()
    mesh.setColors(colors,colorSetName)
    
    
    print('[apply vertex color] %f sec' % (time.time() - tm))
    
    return elapsedTime
    
def adjacencyDebug(shape, maxDepth = 3, startVertexId = 0, methodType = 1):
    vertItr = OpenMaya.MItMeshVertex(shape)
    
    vertexColors = []
    connectedVertices = []
    
    while not vertItr.isDone():
        vertexColors.append(list(vertItr.getColor()))
        connectedVertices.append(list(vertItr.getConnectedVertices()))
        
        vertItr.next()
        
    averageVertexColor = AverageVertexColor(vertexColors,connectedVertices,maxDepth)
    
    with open(os.path.join(os.path.dirname(__file__),'vertexColor_test.bin'),'wb') as fp:
        pickle.dump({'vertexColors' : vertexColors, 'connectedVertices' : connectedVertices},fp)

    if methodType == 0 or \
       methodType == 1:    
        return averageVertexColor.traverseAdjacencyListLoopDebug(startVertexId,connectedVertices)
    else:
        return averageVertexColor.traverseAdjacencyListLoopDebug2(startVertexId,connectedVertices)
    
    
    
    
    
    
    
    






