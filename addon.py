﻿# Tester script
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
from contextlib import closing
import json

history_cmds = []

class AndroidCommand(object):
    
    def __init__(self):
        self.package = ""
        self.intent = ""
        self.action = ""
        self.category = ""
        self.className = ""
        self.dataType = ""
        self.dataURI = ""
        self.flags = ""
        self.extras = []
        
    def get_name(self):
        return f"{self.package} | {self.intent} | {self.dataURI}"
    
    def load(self, data: dict):
        for key, value in data.items():
            if key not in self.__dict__:
                continue
            if isinstance(self.__dict__[key], bool):
                self.__dict__[key] = bool(data[key])
            elif isinstance(self.__dict__[key], int):
                self.__dict__[key] = int(data[key])
            else:
                self.__dict__[key] = value
        
def execute_android(cmd: AndroidCommand):
    xbmc.log("Android CMD Starting ...", xbmc.LOGINFO)

    data_dir = xbmcaddon.Addon().getAddonInfo('profile')
    xbmcvfs.mkdirs(data_dir)
    path = data_dir + "/history.json"    
    with closing(xbmcvfs.File(path, 'w')) as fo:
        cmds_dicts = [cmd.__dict__ for cmd in history_cmds]
        fo.write(json.dumps(cmds_dicts))
        
    extras_json = json.dumps(cmd.extras)
    command = f'StartAndroidActivity("{cmd.package}", "{cmd.intent}", "{cmd.dataType}", "{cmd.dataURI}", "{cmd.flags}", "{extras_json}", "{cmd.action}", "{cmd.category}", "{cmd.className}")'
    xbmc.log(f"=============>>>> CMD: {command}")
    xbmc.executebuiltin(command, True)

    xbmc.log("Android CMD ENDS")    

def cmd_dialog(cmd: AndroidCommand):    
    options = []
    options.append(xbmcgui.ListItem("Package", cmd.package, "PACKAGE"))
    options.append(xbmcgui.ListItem("Intent", cmd.intent, "INTENT"))
    options.append(xbmcgui.ListItem("Category", cmd.category, "CATEGORY"))
    options.append(xbmcgui.ListItem("Action", cmd.action, "ACTION"))
    options.append(xbmcgui.ListItem("ClassName", cmd.className, "CLASSNAME"))
    options.append(xbmcgui.ListItem("DataURI", cmd.dataURI, "DATAURI"))
    options.append(xbmcgui.ListItem("DataType", cmd.dataType, "DATATYPE"))
    options.append(xbmcgui.ListItem("Flags", cmd.flags, "FLAGS"))
    options.append(xbmcgui.ListItem("Extras", json.dumps(cmd.extras), "EXTRAS"))
    options.append(xbmcgui.ListItem("EXECUTE", None, "EXECUTE"))
    
    dialog = xbmcgui.Dialog()
    selection = dialog.select("COMMAND", options)       
    if selection < 0: return None
    
    selected_item:xbmcgui.ListItem = options[selection]
    path = selected_item.getPath()
    if path == "EXECUTE":
        execute_android(cmd)
    elif path == "EXTRAS":
        pass
    else:
        keyboard = xbmc.Keyboard(selected_item.getLabel2(), selected_item.getLabel())
        keyboard.doModal()
        if keyboard.isConfirmed():
            new_value = keyboard.getText()
            if path == "PACKAGE": cmd.package = new_value
            elif path == "INTENT": cmd.intent = new_value
            elif path == "ACTION": cmd.action = new_value
            elif path == "CATEGORY": cmd.category = new_value
            elif path == "CLASSNAME": cmd.className = new_value
            elif path == "DATATYPE": cmd.dataType = new_value
            elif path == "DATAURI": cmd.dataURI = new_value
            elif path == "FLAGS": cmd.flags = new_value
    
    cmd_dialog(cmd)

def list_history(base_url, handle):
    
    data_dir = xbmcaddon.Addon().getAddonInfo('profile')
    xbmcvfs.mkdirs(data_dir)
    path = data_dir + "/history.json"
    
    if xbmcvfs.exists(path):
        with closing(xbmcvfs.File(path, 'r')) as fo:
            jsonobjs = json.loads(fo.read())
            for jsonobj in jsonobjs:
                cmd = AndroidCommand()
                cmd.load(jsonobj)
                history_cmds.append(cmd)
    
    url_str = f"{base_url}?cmd=NEW"
    list_item = xbmcgui.ListItem("NEW")
    xbmcplugin.addDirectoryItem(handle = handle, url = url_str, listitem = list_item, isFolder = False)
    
    i = 0
    for history_cmd in history_cmds:
        list_item = xbmcgui.ListItem(history_cmd.get_name())
        url_str = f"{base_url}?item={i}"
        xbmcplugin.addDirectoryItem(handle = handle, url = url_str, listitem = list_item, isFolder = False)
        i += 1
        
    xbmcplugin.endOfDirectory(handle = handle, succeeded = True, cacheToDisc = False)

def runplugin(base_url, handle):
    list_history(base_url, handle) 
    
try:
    history_cmds = []
    base_url = sys.argv[0]
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        handle = int(sys.argv[1])
    else:
        handle = -1
    
    if len(sys.argv) > 2:
        pass
        
    runplugin(base_url, handle)
except Exception as ex:
    xbmc.log(f"General exception: {ex.message}", xbmc.LOGERROR)
