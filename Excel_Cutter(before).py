# import information
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


# 폴더 생성
def createFolder(directory):
    try:
        if not exists(directory):
            makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

try:
    # 프로그램 정보
    print("Excel Cutter 1.2.0 Ver 입니다.")

    mypath = dirname(realpath(__file__))

    createFolder(f"{mypath}\\__XLSX")
    createFolder(f"{mypath}\\__RESULT")
    createFolder(f"{mypath}\\__Type")

    name = input("(확장자 및 경로를 제외한) 대상 파일 이름을 입력해주세요...\n: ")
    filename = f"{name}.xlsx"

    myinputpath = f"{mypath}\\__XLSX"
    myoutputpath = f"{mypath}\\__RESULT\\{name}"

    txtpath = myoutputpath + "\\txt"
    wavpath = myoutputpath + "\\wav"

    filepath = f"{myinputpath}\\{filename}"

    # 엑셀
    wb = xl.load_workbook(filepath, data_only=True)

    createFolder(myoutputpath)

    createFolder(txtpath)
    createFolder(wavpath)

    createFolder(wavpath + "\\" + "org")
    createFolder(wavpath + "\\" + "cut")
    createFolder(wavpath + "\\" + "cut_saved")


    # Type 지정
    wantType = -1
    typeArr = []


    for i in range(1,100):
        pyName = f"Type{i:02}(before).py"
        if exists(f"{mypath}\\__Type\\" + pyName):
            typeArr.append(import_module("__Type." + pyName[:-3]))


    numArr = [str(x.num) for x in typeArr]


    # Type 선택 질문
    for temp in range(len(typeArr)):
        print(f"{typeArr[temp].num:03}: {typeArr[temp].temp}")

    while (wantType == -1):
        in_data = input("원하시는 변환 타입을 입력해주세요.")

        if in_data in numArr:
            wantType = int(in_data)

    for idx, num in enumerate([x.num for x in typeArr]):
        if wantType == num:
            myType = typeArr[idx]
            break

    myType.wb = wb

    myType.mypath = f"{mypath}"
    myType.txtpath = txtpath
    myType.wavpath = wavpath

except Exception as e:
    print(f"에러 발생!: {e}")
    print(format_exc())
    input()
    exit()

myType.Running()
print("완료.")
input()