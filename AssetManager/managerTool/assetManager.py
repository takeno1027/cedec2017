# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 23:18:30 2017

@author: tomita
"""

import sys
import os

import xmlrpclib

from PyQtUtil import QtCore, QtWidgets, QtGui, createWindowFromUiFile, getMayaMainWindow

import screenShot

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

import shutil

ASSET_ROOT_DIR = os.path.join(os.path.dirname(__file__),os.pardir,"data")
print("ASSET_ROOT_DIR",ASSET_ROOT_DIR)

ICON_SIZE = (160,128)

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

def getTextureNodeFromShape(shape):
    mesh = OpenMaya.MFnMesh(shape)
    for uvSetName in mesh.getUVSetNames():
        for texture in mesh.getAssociatedUVSetTextures(uvSetName):
            yield OpenMaya.MFnDependencyNode(texture)

def getAttrPlug(node,attrName):
    if type(node) == OpenMaya.MObject:
        depNode = OpenMaya.MFnDependencyNode(node)
    elif type(node) == OpenMaya.MFnDependencyNode:
        depNode = node
    else:
        raise RuntimeError('must be mobject')
    
    return depNode.findPlug(attrName,True)

def getTextureFileNameFromShape(shape):
    for tex in getTextureNodeFromShape(shape):
        yield getAttrPlug(tex,'fileTextureName').asString()

class AsyncCopy(QtCore.QThread):
    progress      = QtCore.Signal(object)
    succeeded     = QtCore.Signal()
    error         = QtCore.Signal()
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.copyFiles = []
        
    def appendCopyFile(self,src,tar):
        self.copyFiles.append((src,tar))
        
    def run(self):
        for src,tar in self.copyFiles:
            try:
                shutil.copy2(src,tar)
                self.progress.emit((src,tar))
            except Exception as e:
                self.error.emit(e)
        
        self.copyFiles = []
        self.succeeded.emit()
        
class AssetManagerWindow(QtWidgets.QMainWindow):
    def init_ui(self,appSettingData):
        self.pushButton_insertDB.clicked.connect(self.insertDB)
        self.pushButton_searchDB.clicked.connect(self.searchDB)
        
        self.connect = xmlrpclib.ServerProxy("http://localhost:15600")
        
        now = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit_search_data_to.setDateTime(now)
        self.dateTimeEdit_search_data_from.setDateTime(now.addMonths(-1))
        
        self.model = QtGui.QStandardItemModel()
        self.tableView_searchResult.setModel(self.model)
        self.tableView_searchResult.setIconSize(QtCore.QSize(*ICON_SIZE))
        self.tableView_searchResult.doubleClicked.connect(self.importScene)
        
        self.asyncCopy = AsyncCopy()
        
        def Print(*args):
            print(args)
        
        self.asyncCopy.progress.connect(Print)
        
        self.searchResults = []
        self.iconCache = {}
        
    def close_ui(self,appSettingData):
        self.iconCache.clear()
        
    def insertDB(self):
        assetName = self.lineEdit_assetName.text()
        status = QtWidgets.QMessageBox.question(self,u'確認',u'%sを登録しますか？' % assetName,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if status != QtWidgets.QMessageBox.Yes:
            return        
        
        if len(cmds.ls(sl = True)) == 0:
            QtWidgets.QMessageBox.critical(self,u'エラー',u'登録したいオブジェクトを選択してください')
            return
        
        Id = self.connect.insertAsset(assetName,os.getenv('USERNAME'))
        print('Id : %d' % Id)
        exportedDirName = os.path.join(ASSET_ROOT_DIR,'%d' % Id)
        if not os.path.exists(exportedDirName):
            os.mkdir(exportedDirName)
        
        self.exportScene(exportedDirName)
        self.takeSnapShot(exportedDirName)
        
        conditions = {'id' : Id}
        self.searchResults = self.connect.searchAsset(conditions)
        self.updateSearchResult()
        
    def takeSnapShot(self,exportedDirName):
        screenShot.capture(os.path.join(exportedDirName,'snapshot.jpg'),resize = ICON_SIZE)
        
        
    def importScene(self,modelIndex):
        data = modelIndex.data(QtCore.Qt.UserRole)
        
        status = QtWidgets.QMessageBox.question(self,u'確認',u'ID %dをインポートしますか？' % data['id'],QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if status != QtWidgets.QMessageBox.Yes:
            return
        
        exportedDirName = os.path.join(ASSET_ROOT_DIR,'%d' % data['id'])
        mbFileName = os.path.join(exportedDirName,'asset.mb')
        if not os.path.exists(mbFileName):
            QtWidgets.QMessageBox.critical(self,u'エラー',u'%sが存在しませんでした。' % mbFileName)

        cmds.file(mbFileName,i = True)
        
    def exportScene(self,exportedDirName):
        mbFileName = os.path.join(exportedDirName,'asset.mb').replace('\\','/')
        cmds.file(mbFileName,f = True,type = 'mayaBinary', exportSelected = True)
        print('exported %s' % mbFileName)
        
        for shape in getSelectedShapes():
            for textureFileName in getTextureFileNameFromShape(shape):
                self.asyncCopy.appendCopyFile(textureFileName,exportedDirName)
                
        self.asyncCopy.start()
        
    def searchDB(self):
        conditions = {}
        
        if self.checkBox_assetName.checkState():
            conditions['name'] = self.lineEdit_search_assetName.text()
            
        if self.checkBox_search_date.checkState():
            conditions['date'] = (self.dateTimeEdit_search_data_from.dateTime().toString('yyyy-MM-dd hh:mm:ss'),
                                  self.dateTimeEdit_search_data_to.dateTime().toString('yyyy-MM-dd hh:mm:ss'))
                      
        if self.checkBox_userName.checkState():
            conditions['username'] = self.lineEdit_search_userName.text()
        
        if len(conditions) != 0:
            self.searchResults = self.connect.searchAsset(conditions)
            
        else:
            self.searchResults = self.connect.fetchAllAsset()
        
        self.updateSearchResult()
            
    def makeThumbnailIcon(self,result):
        snapshotFileName = os.path.join(ASSET_ROOT_DIR,'%d' % result['id'],'snapshot.jpg')
        
        icon = None
        if os.path.exists(snapshotFileName):
            QtGui.QImage(snapshotFileName)
            
            icon = QtGui.QIcon(snapshotFileName)
        
        return icon
    
    def resizeEvent(self,event):
        self.updateSearchResult()
        
    def updateSearchResult(self):
        self.model.clear()
        
        width = self.tableView_searchResult.width()
        columnCount = max(1,(width / ICON_SIZE[0]) - 2)
        
        for i,result in enumerate(self.searchResults):
            text = '[Id] %d\n[Name] %s\n[User] %s\n[Date] %s' % (result['id'],result['name'],result['username'],result['date'])
            item = QtGui.QStandardItem(text)
            item.setData(result,QtCore.Qt.UserRole)
            
            if result['id'] in self.iconCache:
                icon = self.iconCache[result['id']]
            else:
                icon = self.makeThumbnailIcon(result)
                self.iconCache[result['id']] = icon
                
            if icon:
                item.setIcon(icon)
            
            y= i % columnCount
            x= i / columnCount
            
            self.model.setItem(x,y,item)
            
            
        
def main():
    window = createWindowFromUiFile('AssetManager',os.path.join(os.path.dirname(__file__),'assetManager.ui'),AssetManagerWindow(parent = getMayaMainWindow()))
    window.show()
    
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
    
    
