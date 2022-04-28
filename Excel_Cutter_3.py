import openpyxl as xl
from os import makedirs
from os.path import exists, dirname, realpath

from importlib import import_module

from os import listdir, rename, scandir, remove
from os.path import isdir, isfile, splitext, basename
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

from json import loads as jsonloads



class NotExistError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class IndexMatchFailError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg



class MainProgram:
    def __init__(self):
        self.__version = "3.0.0"
        self.__platform = platform.system()
        self.__type = None
        self.__typeFunction = None
        self.__typeNum = None
        self.__name = None
        self.__wb = None
        self.__txt = None

    def rootChanger(self, root):
        if self.__platform == "Linux":
            return root.replace("\\", "/")
        else:
            return root

    def slash(self):
        return "/" if self.__platform == "Linux" else "\\"

    def folderCheck(self):
        self.mypath = self.rootChanger(dirname(realpath(__file__)))
        self.pathDict = {
            "xlsx": f"{self.mypath}\\__XLSX",
            "result": f"{self.mypath}\\__RESULT",
            "type": f"{self.mypath}\\__Type",
            "custom": f"{self.mypath}\\__Custom",
            "function": f"{self.mypath}\\__Function",
        }

        self.pathDict = {key:self.rootChanger(val) for key,val in self.pathDict.items()}

        for myFolder, myRoot in self.pathDict.items():
            if not exists(myRoot):
                raise NotExistError(f"기본적인 폴더[{myFolder}]가 존재하지 않습니다. 파일 경로에 이상이 있습니다...")

    def wbCheck(self):
        while (self.__name == None):
            print("원하시는 Excel File 명을 입력해주세요.")

            in_data = input()

            if not exists(self.rootChanger(self.pathDict["xlsx"] + "\\" + in_data + ".xlsx")):
                print("입력하신 파일이 존재하지 않습니다. 다시 입력해주시기 바랍니다...")
                continue

            self.__name = in_data

        self.__wb = xl.load_workbook(self.pathDict["xlsx"] + "\\" +  in_data + ".xlsx", data_only=True)

        additionalPathDict = {}
        additionalPathDict["result.name"] = self.pathDict["result"] + f"\\{self.__name}"
        additionalPathDict["result.name.txt"] = additionalPathDict["result.name"] + f"\\txt"
        additionalPathDict["result.name.wav"] = additionalPathDict["result.name"] + f"\\wav"
        additionalPathDict["result.name.wav.org"] = additionalPathDict["result.name.wav"] + f"\\org"
        additionalPathDict["result.name.wav.cut_saved"] = additionalPathDict["result.name.wav"] + f"\\cut_saved"
        additionalPathDict["result.name.wav.cut"] = additionalPathDict["result.name.wav"] + f"\\cut"

        additionalPathDict = {key:self.rootChanger(val) for key,val in additionalPathDict.items()}

        self.pathDict.update(additionalPathDict)

    def typeCheck(self):
        self.typeInfoDict = {}
        for i in range(1, 100):
            pyName = f"Type{i:02}.py"
            if exists(self.rootChanger(f"{self.mypath}\\__Type\\" + pyName)):
                moduleName = import_module("__Type." + pyName[:-3])
                className =  "basicInfo"

                infoClass = getattr(moduleName, className)()
                infoText = f"{infoClass.num:02}: {infoClass.temp}\t[{infoClass.lastChanged}]"

                self.typeInfoDict[i] = infoText

        if not self.typeInfoDict:
            raise NotExistError("Type File이 하나도 존재하지 않습니다. 다운로드해주시길 바랍니다...")
        
        while (self.__typeNum == None):
            print("원하시는 Type 번호를 입력해주세요.")
            for idx, typeInfo in self.typeInfoDict.items():
                print(typeInfo)

            in_data = input()

            if not in_data.isdigit():
                print("숫자가 아닌 값이 입력되었습니다. 다시 입력해주시기 바랍니다...")
                continue

            in_data = int(in_data)
            if in_data in self.typeInfoDict.keys():
                self.__typeNum = in_data
            else:
                print("선택하신 숫자의 Type 파일이 존재하지 않습니다. 다시 입력해주시기 바랍니다...")
                continue

        self.__type = import_module("__Type." + f"Type{self.__typeNum:02}")
        self.__typeFunction = self.__type.TypeFunction(self.pathDict["function"])

    def checkTxt(self):
        customTxtDirectory = self.rootChanger(self.pathDict["custom"] + f"\\Type{self.__typeNum:02}")
        customTxtList = []
        createFolder(customTxtDirectory)

        if isdir(customTxtDirectory):
            for file in scandir(customTxtDirectory):
                if file.path[-3:].lower() == "txt":
                    customTxtList.append(self.rootChanger(file.path))

        default_path = self.rootChanger(self.pathDict["custom"] + f"\\Type{self.__typeNum:02}\\default.txt")
        if default_path not in customTxtList:
            with open(default_path, "w", encoding="utf-8") as default_txt:
                default_txt.write(self.__typeFunction.makeDefault())

        while True:
            print("원하시는 Custom 설정을 입력해주시기 바랍니다.")
            for idx, txtPath in enumerate(customTxtList):
                print(f"{idx+1:02}: {txtPath.split(self.slash())[-1]}")

            in_data = input()
            if in_data.isdigit() and 0<=int(in_data)-1<len(customTxtList):
                myTxt = self.readTxt(customTxtList[int(in_data)-1])

                print("=== ==="*4)
                print("해당 내용이 원하는 Custom 설정이 맞습니까??")
                print(f"CUSTOM_NAME = {myTxt['CUSTOM_NAME']}")
                print("...")
                print("=== ==="*4)

                self.__txt = myTxt
                self.__typeFunction.setTxt(self.__txt)
                break
            else:
                print("잘못된 숫자를 입력했습니다. 다시 입력해주시길 바랍니다...")
        
    def readTxt(self, txtPath):
        resDict = {}

        f = open(txtPath, "r", encoding="utf-8")
        totalLines = "".join(f.readlines())
        f.close()
        
        subidx = [totalLines.find("CUSTOM_NAME"), totalLines.find("READ_INFO"), totalLines.find("WRITE_INFO"), totalLines.find("CONFIG_INFO"), len(totalLines)]
        subLines = [totalLines[subidx[idx]:subidx[idx+1]] for idx in range(len(subidx)-1)]

        resDict["CUSTOM_NAME"] = subLines[0]
        resDict["READ_INFO"] = subLines[1]
        resDict["WRITE_INFO"] = subLines[2]
        resDict["CONFIG_INFO"] = subLines[3]

        idx_i = [0 for _ in range(4)]
        idx_f = [0 for _ in range(4)]

        idx_i[0] = resDict["CUSTOM_NAME"].find("\"")
        idx_f[0] = len(resDict["CUSTOM_NAME"]) - resDict["CUSTOM_NAME"][::-1].find("\"")
        resDict["CUSTOM_NAME"] = resDict["CUSTOM_NAME"][idx_i[0]+1:idx_f[0]-1]

        idx_i[1] = resDict["READ_INFO"].find("[")
        idx_f[1] = len(resDict["READ_INFO"]) - resDict["READ_INFO"][::-1].find("]")
        resDict["READ_INFO"] = resDict["READ_INFO"][idx_i[1]:idx_f[1]].replace(" ", "").replace("\n", "").replace(",]", "]").replace(",}", "}")
        resDict["READ_INFO"]= jsonloads(resDict["READ_INFO"])

        idx_i[2] = resDict["WRITE_INFO"].find("[")
        idx_f[2] = len(resDict["WRITE_INFO"]) - resDict["WRITE_INFO"][::-1].find("]")
        resDict["WRITE_INFO"] = resDict["WRITE_INFO"][idx_i[2]:idx_f[2]].replace(" ", "").replace("\n", "").replace(",]", "]").replace(",}", "}")
        resDict["WRITE_INFO"]= jsonloads(resDict["WRITE_INFO"])

        idx_i[3] = resDict["CONFIG_INFO"].find("[")
        idx_f[3] = len(resDict["CONFIG_INFO"]) - resDict["CONFIG_INFO"][::-1].find("]")
        resDict["CONFIG_INFO"] = resDict["CONFIG_INFO"][idx_i[3]:idx_f[3]].replace(" ", "").replace("\n", "").replace(",]", "]").replace(",}", "}")
        resDict["CONFIG_INFO"]= jsonloads(resDict["CONFIG_INFO"])

        return resDict
        
    def readXlsx(self):
        for READ_INFO in self.__txt["READ_INFO"]:
            columns = READ_INFO["column"]

            numberCut = None
            if READ_INFO["askRange"]:
                while True:
                    inputdata = input("정답 칸의 너비를 입력해주세요 (기본: 15 10)")
                    inputdata = inputdata.split()

                    isBreak = False

                    for i in inputdata:
                        if not i.isdigit():
                            print(f"{i} 는 숫자가 아닙니다! 다시 입력해주시기 바랍니다!")
                            isBreak = True

                            break
                    
                    if isBreak:
                        continue
                        
                    numberCut = [int(x) for x in inputdata]
                    break

            for data in self.__wb[READ_INFO["sheetName"]]:
                datalist = [x.value for x in data[:]]

                #파일 걸러내기
                if datalist[0] and not isinstance(datalist[0], int):
                    continue

                if datalist[0] == None or datalist[0] == "":
                    continue

                readData = {}
                
                for column in columns:
                    idx_column = column["idx_column"]
                    name = column["name"]
                    readData[name] = datalist[idx_column]

                answers = []
                readStart = column["readStart"]
                if numberCut:
                    for myCut in numberCut:
                        answers.append(datalist[readStart:readStart+myCut])
                        readStart += myCut
                else:
                    answers.append(datalist[readStart:])

                readData["answers"] = answers

                self.__typeFunction.readData(readData, READ_INFO["function"])

    def typeRun(self):
        pass
    

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
        my_program.folderCheck()
        my_program.wbCheck()
        my_program.typeCheck()
        my_program.checkTxt()
        my_program.readXlsx()
        my_program.typeRun()


    except Exception as e:
        print(f"에러 발생!: {e}")
        print(format_exc())
        input("\n종료합니다...")