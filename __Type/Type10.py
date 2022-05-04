from os import listdir, rename, scandir, remove
from os.path import isdir, isfile, splitext
from platform import platform
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


temp = "가사 싱크\t[22/04/30 수정]"
num = 10
platform = None


def rootChanger(root):
    if platform == "Linux":
        return root.replace("\\", "/")
    else:
        return root


def DeleteAllFiles(filePath, ext):
    """파일 전부 삭제"""
    filePath = rootChanger(filePath)
    if isdir(filePath):
        for file in scandir(filePath):
            if file.path[-len(ext):] == ext:
                remove(file.path)
        return 'Remove All File'
    else:
        return 'Directory Not Found'


def DeleteFile(filePath):
    """단일파일 삭제"""
    filePath = rootChanger(filePath)
    if isfile(filePath):
        remove(filePath)


# 초성 생성
def checking(word):
    """매 글자의 초성을 반환합니다."""
    checklist = [
        "까", "나", "다", "따", "라", "마", "바", "빠", "사", "싸", "아", "자", "짜", "차", "카", "타", "파", "하", "힣"]
    returnlist = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
                  "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

    if word < "가" or word > checklist[-1] or word == " ":
        return word

    if word.isalpha():
        if 96 <= ord(word) <= 122 or 65 <= ord(word) <= 90:
            return word

    for idx, checkword in enumerate(checklist):
        if word < checkword:
            return returnlist[idx]


# 전체 초성 변화
def makehint(answer):
    """
    초성으로만 이루어진 것,
    단어 1글자 + 초성 3개,
    단어 1글자 + 초성 1개
    """

    hint = ""
    for word in answer:
        hint += checking(word)

    hint2text = hint
    hint3text = ""
    hint4text = ""

    if len(hint2text) == 1:
        hint3text = hint2text
        hint4text = hint2text
    else:
        k = 0
        for a in range(len(hint2text)):
            if k % 4:
                if k % 2:
                    hint4text += hint2text[a]
                else:
                    hint4text += answer[a]
                hint3text += hint2text[a]
            else:
                hint3text += answer[a]
                hint4text += answer[a]
            if "가" <= answer[a] <= "힣":
                k += 1

    return hint2text, hint3text, hint4text


# 소문자 변환
def changeLowerAnswer(word):
    """lower"""
    new_word = "".join([w.lower() if 65<=ord(w)<=90 else w for w in str(word)])

    return new_word


# 대문자 변환
def changeUpperAnswer(word):
    """upper"""
    new_word = "".join([w.upper() if 96<=ord(w)<=122 else w for w in str(word)])

    return new_word


# 그냥
def nonChange(word):
    """별 거 없음"""
    return word


# replace 뭉치
def replace_show(word, slash = True):
    res = word
    if slash:
        res = res.replace("\\","\\\\")
    res = res.replace("“", "\"").replace("”",  "\"")
    res = res.replace("‘", "\'").replace("’",  "\'")
    res = res.replace("…", "...")

    return res


def replace_answer(word, slash = True):
    res = word
    if slash:
        res = res.replace("\\","\\\\")
    res = res.replace(":","\\:")
    res = res.replace("“", "\"").replace("”",  "\"")
    res = res.replace("‘", "\'").replace("’",  "\'")
    res = res.replace("…", "...")
    res = res.replace("=", "\\=")

    return res


# 답판정 변경
def makeAnswer(word):
    res = []

    UpperFunction = [nonChange, changeUpperAnswer, changeLowerAnswer]
    Spaceword = [replace_answer(str(word)), replace_answer(str(word)).replace(" ","")]

    UpperSetting = [1, 1, 1]    # Org, Up, Down
    SpaceSetting = [1, 1]       # Org, Off

    for idx1, spcst in enumerate(SpaceSetting):
        myword = Spaceword[idx1]
        
        for idx2, upst in enumerate(UpperSetting):

            if spcst * upst == 0:
                continue

            myword2 = UpperFunction[idx2](myword)
            if myword2 not in res and len(myword2.encode()) <= 78:
                res.append(myword2)

    return tuple(res)


def calculateTiming(timing):
    return int(timing / 2.28 * 2220)

class MySong:
    def __init__(self):
        self.idx1 = None
        self.time = []

class MyLyric:
    def __init__(self):
        self.idx1 = None
        self.timelist = []
        self.textlist = [[],[],[],[]]


class MyDict:
    AnswerDict = {}
    Scount = 0
    def __init__(self):
        self.lyricDict = {}
        self.songDict = {}
        self.idxidx = 0
        self.timeidx = 1
        self.textidx = 7

    def append(self, appendType ,datalist, isLink, timeIdx):
        """
        appendType: Lyrics(가사)
        """
        if appendType == "Lyrics":
            # datalist 안의 숫자가, 열 번호-1 을 의미합니다. 만약 열을 바꾸셨다면, 이 숫자부터 바꿔보는 것을 추천합니다.
            
            idxidx = self.idxidx
            timeidx = self.timeidx
            textidx = self.textidx

            d1 = datalist[idxidx] - 1

            if d1 not in self.lyricDict:
                self.lyricDict[d1] = MyLyric()
                self.lyricDict[d1].idx1 = d1
            
            if isLink:
                if self.songDict.get(d1) == None:
                    self.lyricDict[d1].timelist.append(calculateTiming(datalist[timeidx]))
                elif (self.songDict[d1].time[0] <= datalist[timeidx] <= self.songDict[d1].time[1]):
                    self.lyricDict[d1].timelist.append(calculateTiming(datalist[timeidx] - self.songDict[d1].time[0]))
                else:
                    return
            
            else:
                self.lyricDict[d1].timelist.append(calculateTiming(datalist[timeidx]))

            for lidx, lval in enumerate([replace_show(str(x), False) if x != None else " " for x in datalist[textidx:textidx+4]]):
                if "\\x12" not in lval and "\\x13" not in lval:
                    if "\\left" in lval:
                        lval2 = lval.replace("\\left", "")
                    else:
                        lval2 = f"\\x13{lval}"

                self.lyricDict[d1].textlist[lidx].append(lval2)
        
        elif appendType == "Song" and isLink:
            d1 = datalist[0] - 1

            if d1 not in self.songDict:
                self.songDict[d1] = MySong()
                self.songDict[d1].idx1 = d1

            self.songDict[d1].time = [x if x else 0 for x in datalist[timeIdx:timeIdx+2]]
                 


class TxtDict:
    def __init__(self) -> None:
        self.Dict = {}

    def set_init(self, name, link):
        self.Dict[name] = {}
        self.Dict[name]["list"] = []
        self.Dict[name]["link"] = rootChanger(link)
        self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")
        self.Dict[name]["wantWrite"] = False

    def set_write(self, name, boolean):
        self.Dict[name]["wantWrite"] = boolean

    def set_write_all(self, boolean):
        for name in self.Dict.keys():
            self.Dict[name]["wantWrite"] = boolean

    def append_list(self, name, data):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["link"] = rootChanger(f".\\{name}")
            self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")

        self.Dict[name]["list"].append(data)

    def extend_list(self, name, data):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["link"] = rootChanger(f".\\{name}")
            self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")

        self.Dict[name]["list"].extend(data)

    def add_text(self, name, text):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["link"] = rootChanger(f".\\{name}")
            self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")
        
        self.Dict[name]["file"].write(text)

    def get_link(self, name):
        return self.Dict[name]["link"]

    def return_list(self, name, idx1=None, idx2=None):
        if idx1 == None:
            return self.Dict[name]["list"]
        elif idx2 == None:
            return self.Dict[name]["list"][idx1]
        return self.Dict[name]["list"][idx1:idx2]

    def close_file(self, name):
        self.Dict[name]["file"].close()
        self.Dict[name]["file"] = None

    def close_all_file(self):
        for name in self.Dict.keys():
            if self.Dict[name]["file"]:
                self.close_file(name)

    def write_text(self):
        for name in self.Dict.keys():
            if self.Dict[name]["wantWrite"] == False:
                self.Dict[name]["file"].close()
                DeleteFile(self.Dict[name]["link"])
            elif self.Dict[name]["list"]:
                if self.Dict[name]["wantWrite"]:
                    self.Dict[name]["file"].write(str(self.Dict[name]["list"])[1:-1])


class MyType:
    def __init__(self):
        self.temp = temp
        self.num = num
        self.wb = None

        self.MyDict = MyDict()

        self.mypath = None
        self.wavpath = None
        self.txtpath = None

    def insert_defalut_data(self, wb, mypath, wavpath, txtpath):
        self.wb = wb
        self.mypath = mypath
        self.wavpath = wavpath
        self.txtpath = txtpath

        self.orgpath = rootChanger(self.wavpath + "\\" + "org" + "\\")
        self.superpath = [x for x in listdir(rootChanger(self.mypath + "\\__RESULT")) if isdir(x)]
        self.extList = [".mp3", ".wav", ".m4a", ".mp4", ".MP3", ".WAV", ".M4A", ".MP4"]
        self.cutmidpath = rootChanger(self.wavpath + "\\" + "cut_saved" + "\\")
        self.cutpath = rootChanger(self.wavpath + "\\" + "cut" + "\\")
    
    def ReadData(self):
      # 정답 위치 설정
        print("-" * 20)
        isLink = None
        timeIdx = None

        while isLink == None:
            in_data = input("다른 Sheet와 가사가 연동되어 있습니까? 노래 파일이 풀버전인 경우, F를 입력해주세요... (T / F)")

            if in_data in ["T", "t"]:
                isLink = True
                break
            elif in_data in ["F", "f"]:
                isLink = False
                break
            else:
                print(f"다시 입력해주시기 바랍니다!")

        while isLink and timeIdx == None:
            in_data = input("Time의 column Line Number를 입력해주시기 바랍니다. (첫 줄(A) = 0)")
            if in_data.isdigit():
                isLink = int(in_data)
            else:
                print(f"{in_data}는 숫자가 아닙니다! 다시 입력해주시기 바랍니다...")

        # Main Sheet 읽기
        if isLink:
            for data in self.wb["Main"]:
                datalist = [x.value for x in data[:]]

                #파일 걸러내기
                if datalist[0] and not isinstance(datalist[0], int):
                    continue

                if datalist[0] == None or datalist[0] == "":
                    continue

                self.MyDict.append("Lyrics", datalist=datalist, isLink=isLink, timeIdx=timeIdx)
        
        # Lyrics Sheet 읽기
        for data in self.wb["Lyrics"]:
            datalist = [x.value for x in data[:]]

            #파일 걸러내기
            if datalist[0] and not isinstance(datalist[0], int):
                continue

            if datalist[0] == None or datalist[0] == "":
                continue

            self.MyDict.append("Lyrics", datalist=datalist, isLink=isLink, timeIdx=timeIdx)

    def MakeTxt(self):
        self.TxtDict = TxtDict()

        self.TxtDict.set_init("L1Txt", rootChanger(self.txtpath + "\\" + "L1 텍스트.txt"))
        self.TxtDict.set_init("L2Txt", rootChanger(self.txtpath + "\\" + "L2 텍스트.txt"))
        self.TxtDict.set_init("L3Txt", rootChanger(self.txtpath + "\\" + "L3 텍스트.txt"))
        self.TxtDict.set_init("L4Txt", rootChanger(self.txtpath + "\\" + "L4 텍스트.txt"))
        
        self.TxtDict.set_init("LyricTimingTxt", rootChanger(self.txtpath + "\\" + "가사 등장 타이밍.txt"))
        self.TxtDict.set_init("LyricTimingLengthTxt", rootChanger(self.txtpath + "\\" + "가사 등장 타이밍 길이.txt"))

        self.keylist = sorted(self.MyDict.lyricDict.keys())

        for key in self.keylist:
            ASDF = self.MyDict.lyricDict[key]

            vals = ASDF.textlist

            self.TxtDict.add_text("L1Txt", "[")
            self.TxtDict.add_text("L2Txt", "[")
            self.TxtDict.add_text("L3Txt", "[")
            self.TxtDict.add_text("L4Txt", "[")

            for val in vals[0]:
                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
                else:
                    mytext = "Db('{}'), ".format(val)
                self.TxtDict.add_text("L1Txt", str(mytext))

            for val in vals[1]:
                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
                else:
                    mytext = "Db('{}'), ".format(val)
                self.TxtDict.add_text("L2Txt", str(mytext))

            for val in vals[2]:
                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
                else:
                    mytext = "Db('{}'), ".format(val)
                self.TxtDict.add_text("L3Txt", str(mytext))

            for val in vals[3]:
                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
                else:
                    mytext = "Db('{}'), ".format(val)
                self.TxtDict.add_text("L4Txt", str(mytext))
                
            self.TxtDict.add_text("L1Txt", "],\n")
            self.TxtDict.add_text("L2Txt", "],\n")
            self.TxtDict.add_text("L3Txt", "],\n")
            self.TxtDict.add_text("L4Txt", "],\n")
            

            val = ASDF.timelist
            self.TxtDict.add_text("LyricTimingLengthTxt", f"{len(val)}, ")
            self.TxtDict.add_text("LyricTimingTxt", f"{val[:]+[99999999,99999999]},\n")

        self.TxtDict.set_write_all(True)
        
        return True

    def Running(self):
        self.ReadData()
        self.MakeTxt()
        self.TxtDict.write_text()
        self.TxtDict.close_all_file()
        self.make_config()


    def make_config(self):
        with open(rootChanger(self.txtpath + "\\" + "lyricsConfig.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("L1Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L1Txt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("L2Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L2Txt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("L3Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L3Txt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("L4Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L4Txt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricTimingTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricTimingTxt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricTimingLengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricTimingLengthTxt = [{mytext}];\n\n")