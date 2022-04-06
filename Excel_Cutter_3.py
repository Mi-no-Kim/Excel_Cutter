import openpyxl as xl
from os import makedirs
from os.path import exists, dirname, realpath

from importlib import import_module

from os import listdir, rename, scandir, remove
from os.path import isdir, isfile, splitext
from shutil import copy2
from matplotlib.pyplot import pause
from yt_dlp import YoutubeDL
from librosa import load as libLoad
from soundfile import write as sfWrite
from time import sleep
from pyloudnorm import Meter
from numpy import linspace
from niconico_dl.video_manager import NicoNicoVideo
from glob import glob
from traceback import format_exc

import platform 



class NotExistError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class MainProgram:
    def __init__(self):
        self.__version = "3.0.0"
        self.__platform = platform.system()

    def rootChanger(self, root):
        if self.__platform == "Linux":
            return root.replace("\\", "/")
        else:
            return root

    def basicCheck(self):
        self.mypath = dirname(realpath(__file__))
        self.pathDict = {
            "xlsx": f"{self.mypath}\\__XLSX",
            "result": f"{self.mypath}\\__RESULT",
            "type": f"{self.mypath}\\__Type",
            "custom": f"{self.mypath}\\__Custom",
        }

        self.pathDict = {key:self.rootChanger(val) for key,val in self.pathDict.items()}

        checkList= [self.rootChanger(f"{self.mypath}\\__XLSX"), self.rootChanger(f"{self.mypath}\\__Type")]

        for myFolder in checkList:
            if not exists(myFolder):
                raise NotExistError("기본적인 폴더가 존재하지 않습니다. 파일 경로에 이상이 있습니다.")

        folderList= [self.rootChanger(f"{self.mypath}\\{folder}") for folder in [self.pathDict["xlsx"], self.pathDict["result"], self.pathDict["type"], self.pathDict["custom"]]]
        
        for myFolder in folderList:
            createFolder(myFolder)

        # 정규식을 활용한 파일 유무 확인

        


        



    def main(self):
        print(f"Excel Cutter {self.__version} Ver 입니다.")
        self.mypath = dirname(realpath(__file__))

        createFolder(self.rootChanger(f"{self.mypath}\\__XLSX"))
        createFolder(self.rootChanger(f"{self.mypath}\\__RESULT"))
        createFolder(self.rootChanger(f"{self.mypath}\\__Type"))

        self.xl_name = input("(확장자 및 경로를 제외한) 대상 파일 이름을 입력해주세요...\n: ")
        self.filename = self.rootChanger(f"{self.xl_name}.xlsx")

        self.myinputpath = self.rootChanger(f"{self.mypath}\\__XLSX")
        self.myoutputpath = self.rootChanger(f"{self.mypath}\\__RESULT\\{self.xl_name}")

        self.txtpath = self.rootChanger(self.myoutputpath + "\\txt")
        self.wavpath = self.rootChanger(self.myoutputpath + "\\wav")

        self.filepath = self.rootChanger(f"{self.myinputpath}\\{self.filename}")

        # 엑셀
        self.wb = xl.load_workbook(self.filepath, data_only=True)

        createFolder(self.myoutputpath)

        createFolder(self.txtpath)
        createFolder(self.wavpath)

        createFolder(self.rootChanger(self.wavpath + "\\" + "org"))
        createFolder(self.rootChanger(self.wavpath + "\\" + "cut"))
        createFolder(self.rootChanger(self.wavpath + "\\" + "cut_saved"))

        self.wantType = -1
        self.typeArr = []

        for i in range(1,100):
            pyName = f"Type{i:02}.py"
            if exists(self.rootChanger(f"{self.mypath}\\__Type\\" + pyName)):
                self.typeArr.append(import_module("__Type." + pyName[:-3]))


        self.numArr = [str(x.num) for x in self.typeArr]

        # Type 선택 질문
        for temp in range(len(self.typeArr)):
            print(f"{self.typeArr[temp].num:03}: {self.typeArr[temp].temp}")

        while (self.wantType == -1):
            in_data = input("원하시는 변환 타입을 입력해주세요.")

            if in_data in self.numArr:
                self.wantType = int(in_data)

        for idx, num in enumerate([x.num for x in self.typeArr]):
            if self.wantType == num:
                self.my_type = self.typeArr[idx].MyType()
                self.typeArr[idx].platform = self.__platform
                break

        # self.my_type.platform = self.__platform
        self.my_type.insert_defalut_data(self.wb, self.mypath, self.wavpath, self.txtpath)

        self.my_type.Running()
        print("완료.")
        input()
        

# 폴더 생성
def createFolder(directory):
    try:
        if not exists(directory):
            makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


if __name__ == "__main__":
    my_program = MainProgram()

    try:
        my_program.main()
    except Exception as e:
        print(f"에러 발생!: {e}")
        print(format_exc())
        input()
        exit()