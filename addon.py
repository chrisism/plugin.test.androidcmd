# Tester script
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
from contextlib import closing
import json

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
    
    extras_json = json.dumps(cmd.extras)
    command = f'StartAndroidActivity("{cmd.package}", "{cmd.intent}", "{cmd.dataType}", "{cmd.dataURI}", "{cmd.flags}", "{extras_json}", "{cmd.action}", "{cmd.category}", "{cmd.className}")'
    xbmc.log(f"=============>>>> CMD: {command}")
    xbmc.executebuiltin(command, True)

    xbmc.log("Android CMD ENDS")    


def runplugin(base_url, handle):
    
    data_dir = xbmcaddon.Addon().getAddonInfo('profile')
    xbmcvfs.mkdirs(data_dir)
    path = data_dir + "/history.json"
    
    history_cmds = []
    if xbmcvfs.exists(path):
        with closing(xbmcvfs.File(path)) as fo:
            jsonobjs = json.loads(fo.read())
            for jsonobj in jsonobjs:
                cmd = AndroidCommand()
                cmd.load(jsonobj)
                history_cmds.append(cmd)
    
    i = 0
    for history_cmd in history_cmds:
        list_item = xbmcgui.ListItem(history_cmd.get_name())
        url_str = f"{base_url}?item={i}"
        xbmcplugin.addDirectoryItem(handle = handle, url = url_str, listitem = list_item, isFolder = False)
        i += 1
        
    xbmcplugin.endOfDirectory(handle = handle, succeeded = True, cacheToDisc = False)

try:
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
