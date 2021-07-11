import logging
import glob
import os
import importlib
import inspect

_sourceMapping ={} 

def registerSourceType(sourceName,sourceClass):
    log = logging.getLogger('WallpaperChanger')
    if sourceName in _sourceMapping:
        className1 = str(sourceClass)
        className2 = str(_sourceMapping[sourceName])
        log.error(f'registerSourceType: collision with source type name "{sourceName}" and classes {className1} and {className2}')
        return False
    else:
        _sourceMapping[sourceName]=sourceClass
        return True

def getSourceTypes():
    return [x for x in _sourceMapping]

def ImageSource(sourceConfig):
    log = logging.getLogger('WallpaperChanger')

    sourceType = sourceConfig['type']
    if not sourceType in _sourceMapping:
        log.error(f'MainApp: unknow source type {sourceType}')
        return None
    instanceType = _sourceMapping[sourceType]
    return instanceType(sourceConfig)

def registerAllTypes():
    log = logging.getLogger('WallpaperChanger')

    fileList = glob.glob(os.path.dirname(__file__)+'/*.py')
    fileList = [os.path.basename(x)[:-3] for x in fileList]
    fileList = list(filter(lambda x: x!='__init__',fileList))
    
    for fileName in fileList:
        module = importlib.import_module('ImageSources.'+fileName)
        members = inspect.getmembers(module)
        for member in members:
            classType = member[1]
            if inspect.isclass(classType) and classType.__module__.startswith('ImageSources') and hasattr(classType,'getTypeName'):
                ret = registerSourceType(classType.getTypeName(),classType)
                if ret:
                    log.info(f'registerAllTypes: registered class {classType.__module__} as {classType.getTypeName()}')

