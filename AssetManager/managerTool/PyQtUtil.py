# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 17:59:26 2017

@author: tomita
"""
import os
import sys

if not os.getenv("QT_API"):
    """
    環境変数QT_APIに、仕様するQtAPIを指定してなければ、PyQt5を先にインポートを試す。（注　PyQt5は Maya2017には、標準で同梱されていない。各自ビルドが必要
    """
    try:
        import PyQt5
        os.environ["QT_API"] = 'pyqt5'
    except:
        os.environ["QT_API"] = 'pyside2'
    
# CEDEC講演時には、 pyside2を使う設定
os.environ["QT_API"] = 'pyside2'
    
if os.getenv('QT_API') == 'pyqt5':
    import sip
    from PyQt5 import uic as dynamic
    from PyQt5 import QtCore, QtGui, QtWidgets
    
    wrapInstance = sip.wrapinstance
    
    QtCore.Signal = QtCore.pyqtSignal
    
    # Pythonの例外からqFatal()が呼び出された場合に、アプリケーションの終了をしないようにフックする
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    
    sys.excepthook = except_hook
    
    
elif os.getenv('QT_API') == 'pyside2':
    import shiboken2
    import pyside_dynamic as dynamic
    from PySide2 import QtCore, QtGui, QtWidgets
    
    wrapInstance = shiboken2.wrapInstance 
    
os.environ["PYEXE"] = os.path.basename(sys.argv[0])

if os.environ["PYEXE"] == "maya.exe" or \
   os.environ["PYEXE"] == "mayapy.exe":
    
    import maya.OpenMaya as OpenMaya
    import maya.OpenMayaUI as OpenMayaUI
    
    def getMayaApp():
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        return wrapInstance(long(ptr),QtWidgets.QMainWindow)

    class MayaSignalBase(QtCore.QObject):
        def __init__(self):
            QtCore.QObject.__init__(self)
            self.callbackId = self.register()
            
        def register(self):
            return None
        
        def removeCallback(self):
            if not self.callbackId is None:
                OpenMaya.MMessage.removeCallback(self.callbackId)
    
        def emitTriger(self,*args):
            self.trigger.emit(args[0])
        
        def getTrigger(self):
            return self.trigger
    
    class MayaSignalNoArgment(MayaSignalBase):
        trigger = QtCore.Signal()
        
        def emitTriger(self,*args):
            self.trigger.emit()
        
    class MayaSignalArgmentMObject(MayaSignalBase):
        trigger = QtCore.Signal(OpenMaya.MObject)
    
    class MayaSignalArgmentPyList(MayaSignalBase):
        trigger = QtCore.Signal(list)
    
    class MayaSignalArgmentSceneFileName(MayaSignalBase):
        trigger = QtCore.Signal(unicode)

        def emitTriger(self,*args):
            self.trigger.emit(OpenMaya.MFileIO.currentFile())    
    
    class AddNodeMayaSignal(MayaSignalArgmentMObject):
        def register(self):
            return OpenMaya.MDGMessage.addNodeAddedCallback(self.emitTriger)

    class DeleteNodeMayaSignal(MayaSignalArgmentMObject):
        def register(self):
            return OpenMaya.MDGMessage.addNodeRemovedCallback(self.emitTriger)

    class SelectNodeMayaSignal(MayaSignalArgmentPyList):
        def register(self):
            return OpenMaya.MEventMessage.addEventCallback('SelectionChanged',self.emitTriger)
    
        def emitTriger(self,*args):
            selList = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(selList)
            
            def getDepNode(selectionList,index):
                mobj = OpenMaya.MObject()
                selectionList.getDependNode(index,mobj)
                return mobj
            
            self.trigger.emit([getDepNode(selList,i) for i in range(0,selList.length())])
            
    class OpenSceneBeforeMayaSignal(MayaSignalArgmentSceneFileName):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeOpen,self.emitTriger)
        
    class OpenSceneAfterMayaSignal(MayaSignalArgmentSceneFileName):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen,self.emitTriger)
    
    class SaveSceneBeforeMayaSignal(MayaSignalArgmentSceneFileName):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeSave,self.emitTriger)

    class NewSceneBeforeMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeNew,self.emitTriger)
    
    class NewSceneAfterMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew,self.emitTriger)
    
    class ImportSceneBeforeMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeImport,self.emitTriger)

    class ImportSceneAfterMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterImport,self.emitTriger)
        
    class UndoMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MEventMessage.addEventCallback('Undo',self.emitTriger)

    class RedoMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MEventMessage.addEventCallback('Redo',self.emitTriger)
    
    class QuitAppMayaSignal(MayaSignalNoArgment):
        def register(self):
            return OpenMaya.MEventMessage.addEventCallback('quitApplication',self.emitTriger)

    class MayaApp(object):
        def __init__(self):
            self.mayaApp = getMayaApp()
            self.init_event_setting()
        
        def __del__(self):
            for mayaSignal in self.mayaSignals:
                mayaSignal.removeCallback()
            
        def getApp(self):
            return self.mayaApp
    
        def init_event_setting(self):
            self.mayaSignals = []
            
            registeredSignals=[(AddNodeMayaSignal(),'mayaOnAddNode'),
                               (DeleteNodeMayaSignal(),'mayaOnDeleteNode'),
                               (SelectNodeMayaSignal(),'mayaOnSelectNode'),
                               (OpenSceneBeforeMayaSignal(),'mayaOnOpenSceneBefore'),
                               (OpenSceneAfterMayaSignal(),'mayaOnOpenSceneAfter'),
                               (SaveSceneBeforeMayaSignal(),'mayaOnSaveSceneBefore'),
                               (NewSceneBeforeMayaSignal(),'mayaOnNewSceneBefore'),
                               (NewSceneAfterMayaSignal(),'mayaOnNewSceneAfter'),
                               (ImportSceneBeforeMayaSignal(),'mayaOnImportSceneBefore'),
                               (ImportSceneAfterMayaSignal(),'mayaOnImportSceneAfter'),
                               (UndoMayaSignal(),'mayaOnUndo'),
                               (RedoMayaSignal(),'mayaOnRedo'),
                               (QuitAppMayaSignal(),'mayaOnQuitApp')]
            
            for signal,attrbute in registeredSignals:
                setattr(self.mayaApp,attrbute,signal.getTrigger())
                self.mayaSignals.append(signal)
            
    MayaAppInstace = None
    
    def getMayaMainWindow():
        global MayaAppInstace
        
        if MayaAppInstace is None:
            MayaAppInstace = MayaApp()
        
        return MayaAppInstace.getApp()
    
else:
    def getMayaMainWindow():
        return None

class CloseEventFilter(QtCore.QObject):
    beforeClosing = QtCore.Signal()
    
    def eventFilter(self,qObj,event):
        stat = QtCore.QObject.eventFilter(self,qObj,event)
        evtTyp = event.type()
        
        if evtTyp == QtCore.QEvent.Close:
            self.beforeClosing.emit()
        
        return stat
    
def createWindowFromUiFile(appName, uiFileName, baseWidgetInsrance = None):
    ui = dynamic.loadUi(uiFileName,baseWidgetInsrance)

    if hasattr(ui,'close_ui'):
        ui._closeEventFilter = CloseEventFilter()
        ui.installEventFilter(ui._closeEventFilter)
        
        appSettingData = QtCore.QSettings(appName,os.path.basename(uiFileName))
        
        ui._closeEventFilter.beforeClosing.connect(lambda : appSettingData.setValue('window_geometry',ui.saveGeometry().toBase64()))
        ui._closeEventFilter.beforeClosing.connect(lambda : ui.close_ui(appSettingData))
    
    if hasattr(ui,'init_ui'):
        appSettingData = QtCore.QSettings(appName,os.path.basename(uiFileName))
        
        geometry = appSettingData.value('window_geometry')
        if geometry is not None:
            ui.restoreGeometry(QtCore.QByteArray.fromBase64(geometry))
        
        ui.init_ui(appSettingData)
        
    return ui

###############################################################################
def test():
    class MyMainWindow(QtWidgets.QMainWindow):
        def init_ui(self,appSettingData):
            pass
        
        def close_ui(self,appSettingData):
            pass
    
    global window
    
    window = createWindowFromUiFile('testApp',os.path.join(os.path.dirname(__file__),'test_app.ui'),MyMainWindow(parent = getMayaMainWindow()))
    window.show()
    
    
    

    





