import sys
import os
import shutil

Resources={
    'APP_NAME' :'Wallpaper changer',
    'ICON_PATH' :'resources/icon.png',
    'CONFIG_YAML':'config.yaml',
    'LOG_FILE':'log.txt',
    'TEMP_DIR':'temp'
}

if hasattr(sys,'_MEIPASS'):
    Resources['ICON_PATH'] = sys._MEIPASS+'/'+Resources['ICON_PATH']
    Resources['TEMP_DIR'] = sys._MEIPASS+'/'+Resources['TEMP_DIR']
    if not os.path.isfile(Resources['CONFIG_YAML']):
        shutil.copyfile(sys._MEIPASS+'/'+Resources['CONFIG_YAML'],Resources['CONFIG_YAML'])

if not os.path.isdir(Resources['TEMP_DIR']):
    os.mkdir(Resources['TEMP_DIR'])

Resources['TEMP_DIR'] = os.path.abspath(Resources['TEMP_DIR'])
Resources['CONFIG_YAML'] = os.path.abspath(Resources['CONFIG_YAML'])
Resources['LOG_FILE'] = os.path.abspath(Resources['LOG_FILE'])
Resources['ICON_PATH'] = os.path.abspath(Resources['ICON_PATH'])
Resources['DB_FILE'] = os.path.abspath('wallpaperChanger.db')
