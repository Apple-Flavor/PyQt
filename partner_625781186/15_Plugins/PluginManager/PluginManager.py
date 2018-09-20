 # -*- coding: utf-8 -*-
 
import os , time , imp
from importlib.machinery import SourceFileLoader



from PyQt5 import  QtGui, QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PluginManager import PluginStore

from Tools.pmf_myjson import *

    
class PluginManager(QObject):

    def __init__(self, parent = None , *args, **kwargs):
        super(PluginManager, self).__init__(parent  , *args, **kwargs)
        self.__mw = parent
        self.__initUI()
        
        self.pluginDirs = {"pluginPath": os.path.join("./", "Plugins"),}
        self.existPlugin = {}
        self.header = ["PlugName","Allow" ,  "CreateTime", "ModifyTime"]
        
#        print("pluginDirs:", os.path.abspath(self.pluginDirs['pluginPath']))
        
        # 获取插件模块名 及 路径
        self.pluginsModule = self.getPluginModules(
                             self.pluginDirs['pluginPath'])
    
#        print(self.pluginsModule)
        #载入模块 
        self.loadAll()
        
        # 文件监听器
        self.watcher = QFileSystemWatcher(["./Plugins"], 
            directoryChanged = self.m_directoryChanged )

    def m_directoryChanged(self):
        self.pluginsModule = self.getPluginModules(
                             self.pluginDirs['pluginPath'])
        
    def __initUI(self):
        if self.__mw.findChild(QMenuBar, "menuBar"):
            
            self.__mw.menuPlugin = QAction("Plugin", self.__mw.menuBar, 
                                        triggered = self.__createPluginStoreDialog) 
            self.__mw.menuBar.addAction(self.__mw.menuPlugin) 
            
        else:
            QMessageBox.information(self.__mw, "", "主窗体没有菜单栏, 请先创建.")
    
    def __createPluginStoreDialog(self):
        """
        显示插件加载情况的 窗体.
        """
        dia = PluginStore.PluginStore(self, self.__mw)
      
        dia.exec_()
    
    def getPluginModules(self, pluginPath:"./Plugins")->"module list":
        """
        Public method to get a list of plugin modules.
        """
        try:
            existPlugin = mfunc_readJson(setting_flie)
        except:
            existPlugin=[]
            
        pluginFiles = {}
        
        for f in os.listdir(pluginPath):
            # 插件名称的有效性检查
            if f.endswith(".py") and f.startswith("Plugin"):
                # 去掉后缀 , 加入模块
                module = f[:-3]
                
                fullPath = os.path.join( pluginPath , f)
                pluginFiles[module] = {"path":fullPath}
                
                # 判断是否存在配置信息中
                if module not in existPlugin:
                    
                    # 插件创建时间
                    _ctime = time.localtime(os.stat(fullPath).st_ctime) 
                    ctime = time.strftime("%Y-%m-%d-%H:%M:%S",_ctime)
                    # 插件修改时间
                    _mtime = time.localtime(os.stat(fullPath).st_mtime)
                    mtime = time.strftime("%Y-%m-%d-%H:%M:%S",_mtime)
                    
                    # 写入配置
                    mfunc_writeJson( module , 
                                   {
                                   self.header[1]: True, #allow
                                   self.header[2]: ctime,#cteateTime
                                   self.header[3]: mtime,#modifyTime
                                   } ,  
                                    self = self)
                                    
        # 添加完重新加载一遍看是否有插件删除
        self.delJson(pluginFiles)
        
        return pluginFiles
        
    def delJson(self ,  pluginFiles)->"json":  
        """
        删除插件 的json配置.
        """
        # 获取最终json配置
        self.existPlugin = mfunc_readJson(setting_flie)

        if len(self.existPlugin)>len(pluginFiles):
            with open( setting_flie ,'a+' , encoding='utf-8') as f:
                # 被删除的插件集合
                delPlugin = set(self.existPlugin)-set(pluginFiles)
                for item in delPlugin:
                    self.existPlugin.pop(item)
                # 写入配置
                mfunc_afterDelJson(f, self.existPlugin)
                
    # 加载所有插件
    def loadAll(self):
        for mod in self.existPlugin:
            if self.existPlugin[mod]["Allow"]:
                try:
                    self.load(mod)
                except:
                    continue

    # 加载插件
    def load(self , mod:"str"):
        
        try:
            print(self.pluginsModule[mod]["path"])
            # python内置函数, 把.py 当做模块载入
            _pluginModule = SourceFileLoader( mod , 
                self.pluginsModule[mod]["path"]).load_module()
    #       _pluginModule=imp.load_source(mod, self.pluginsModule[mod]["path"])
        except:
#            QMessageBox.information(self.__mw, 
#                                    "模块导入异常", 
#                                    "请在%s.py检查模块."%mod)

            self.pluginsModule[mod]["active"] = False
            return
            
        try:
            className   = getattr(_pluginModule, "className")
            pluginClass = getattr(_pluginModule,  className )
        except:
            self.pluginsModule[mod]["active"] = False
            QMessageBox.information(self.__mw, 
                                    "插件加载错误", 
                                    "请在%s.py全局指定className值."%mod)
            return
        # 实例化类 
        pluginObject = pluginClass()
        pluginObject.setObjectName(className)
        
        self.__mw.verticalLayout.addWidget(pluginObject)
        self.pluginsModule[mod]["active"] = True
        
        return True
    # 卸载所有插件
    def unloadAll(self):
        pass
 
    # 卸载插件
    def unload(self,   mod:"str"):
#        self.__mw.findchild()
        print(sys.modules[mod], mod)
        print(self.__mw.findChild(QWidget, mod))
        #TODO:
        
        return True
        
 
 