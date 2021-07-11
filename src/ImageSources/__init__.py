import logging
# import glob
# import os
# import importlib
# import inspect

_sourceMapping ={} 

def registerSourceType(sourceName,sourceClass):
    log = logging.getLogger('WallpaperChanger')
    if sourceName in _sourceMapping:
        log.error(f'registerSourceType: collision with source type name "{sourceName}" and classes {_sourceMapping[sourceName].__module__} and {sourceClass.__module__}')
    else:
        _sourceMapping[sourceName]=sourceClass
        log.info(f'registerSourceType: registered class {sourceClass.__module__} as {sourceName}')

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
    # fileList = glob.glob(os.path.dirname(__file__)+'/*.py')
    # fileList = [os.path.basename(x)[:-3] for x in fileList]
    # fileList = list(filter(lambda x: x!='__init__',fileList))
    
    # for fileName in fileList:
    #     module = importlib.import_module('ImageSources.'+fileName)
    #     members = inspect.getmembers(module)
    #     for member in members:
    #         classType = member[1]
    #         if inspect.isclass(classType) and classType.__module__.startswith('ImageSources') and hasattr(classType,'getTypeName'):
    #             ret = registerSourceType(classType.getTypeName(),classType)  
    from ImageSources.redditImageSource import RedditImageSource
    from ImageSources.folderImageSource import FolderImageSource                  

    registerSourceType(RedditImageSource.getTypeName(),RedditImageSource)
    registerSourceType(FolderImageSource.getTypeName(),FolderImageSource) 
