from os import scandir, remove
from os.path import isdir, isfile


def DeleteAllFiles(filePath, ext):
    """파일 전부 삭제"""
    if isdir(filePath):
        for file in scandir(filePath):
            if file.path[-len(ext):] == ext:
                remove(file.path)
        return 'Remove All File'
    else:
        return 'Directory Not Found'


def DeleteFile(filePath):
    """단일파일 삭제"""
    if isfile(filePath):
        remove(filePath)