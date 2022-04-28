from os import listdir, rename, scandir, remove
from os.path import isdir, isfile, splitext, basename
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

from importlib import import_module


class NotExistError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class DuplicateError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class MismatchFunctionError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class basicInfo:
    def __init__(self):
        self.num = 1
        self.temp = "기본성능"
        self.lastChanged = "22/02/26"


class TypeFunction:
    def __init__(self, functionPath):
        self.totalDict = {}
        self.answerTrigger = {}
        self.functionPath = functionPath

        self.Function = []
        if isdir(functionPath):
            for file in scandir(functionPath):
                if file.path[3] == ".py":
                    self.Function[basename(file.path)] = import_module(file.path)

    def makeDefault(self):
        return DEFAULT

    def setText(self, TXT):
        necessarys = ["idx", "musicinfo1", "address", "t1", "t2", "answers"]
        for necessary in necessarys:
            if TXT.get(necessary) == None:
                raise NotExistError(f"필수 요소인 {necessary}가 존재하지 않습니다.\n{necessarys}")
        
    def readData(self, data, function):
        if function == "readSong":
            idx = data["idx"]
            keyname = f"{data['idx']:04}"

            if self.totalDict.get(keyname):
                raise DuplicateError(f"At [{keyname}](idx: {idx}), key Duplicated")

            self.totalDict[keyname] = {
                k:v for k, v in data.items()
            }
        else:
            raise MismatchFunctionError(f"FunctionName [{function}] 은 지원되지 않습니다.")

    def makeData(self):
        genreIdx = 2000

        for numIdx, data in enumerate(self.totalDict.items()):
            for cateIdx, answerlist in enumerate(data["answers"]):
                for ansIdx, answer in enumerate(answerlist):
                    for changedanswer in self.Function["word"].makeAnswer(answer):
                        if self.answerTrigger.get(changedanswer) == None:
                            self.answerTrigger[changedanswer] = []
                        self.answerTrigger[changedanswer].append(genreIdx + cateIdx*1000 + numIdx + ansIdx*0)
    
    def musicInfo(self, args):
        with open()


DEFAULT = '''CUSTOM_NAME = "DEFAULT"
READ_INFO = [
    {
        "sheetName": "Main",
        "function": "readSong",
        "range": ["start", "end"],
        "column": [
            {
                "idx_column": 0,
                "name": "idx",
            },
            {
                "idx_column": 1,
                "name": "musicinfo1",
            },
            {
                "idx_column": 2,
                "name": "musicinfo2",
            },
            {
                "idx_column": 3,
                "name": "musicinfo3",
            },
            {
                "idx_column": 4,
                "name": "musicinfo4",
            },
            {
                "idx_column": 5,
                "name": "musicinfo5",
            },
            {
                "idx_column": 6,
                "name": "address",
            },
            {
                "idx_column": 7,
                "name": "t1",
            },
            {
                "idx_column": 8,
                "name": "t2",
            },
        ],
        "readStart": 9,
        "askRange": True
    },
]
WRITE_INFO = [
    {
        "name": "musicInfo1",
        "write": "노래 정보 1.txt",
        "type": "musicInfo",
        "data": "musicinfo1"
    },
    {
        "name": "musicInfo2",
        "write": "노래 정보 2.txt",
        "type": "musicInfo",
    },
    {
        "name": "musicInfo3",
        "write": "노래 정보 3.txt",
        "type": "musicInfo",
    },
    {
        "name": "musicInfo4",
        "write": "노래 정보 4.txt",
        "type": "musicInfo",
    },
    {
        "name": "musicInfo5",
        "write": "노래 정보 5.txt",
        "type": "musicInfo",
    },
    {
        "name": "MusicAnswer",
        "write": "정답 시 (노래정보 1 & 2 합진 것).txt",
        "type": "musicInfoConjoinDelete()",
        "args": ["musicInfo1", "musicInfo2",]
    },
    {
        "name": "musicLength",
        "write": "노래 길이.txt",
        "type": "musicLength()",
        "args": 1,
    },
    {
        "name": "musicConsonantHint1",
        "write": "초성 - 1 번째.txt",
        "type": "consonantHint()",
        "args": "_",
    },
    {
        "name": "musicConsonantHint2",
        "write": "초성 - 2 번째.txt",
        "type": "consonantHint()",
        "args": "*___",
    },
    {
        "name": "musicConsonantHint3",
        "write": "초성 - 3 번째.txt",
        "type": "consonantHint()",
        "args": "*_",
    },
    {
        "name": "trigger",
        "write": "정답 트리거.txt",
        "type": "trigger",
    },
    {
        "name": "duple",
        "write": "중복정답 - 리스트.txt",
        "type": "duple",
    },
    {
        "name": "dulpeLength",
        "write": "중복정답 - 길이.txt",
        "type": "dulpeLength",
    },
    {
        "name": "dupleCheck",
        "write": "!중복정답 이슈.txt",
        "type": "dupleCheck",
    },
    {
        "name": "downloadCheck",
        "write": "!다운로드 이슈.txt",
        "type": "downloadCheck",
    },
]
CONFIG_INFO = [
    "MusicAnswer",
    "musicInfo3",
    "musicLength",
    "musicConsonantHint1",
    "musicConsonantHint2",
    "musicConsonantHint3",
    "duple",
    "dulpeLength",
]'''


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

        self.UpperSetting = [1, 1, 1]    # Org, Up, Down
        self.SpaceSetting = [1, 1]       # Org, Off

        self.numberCut = []

        self.download_failed = []

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
    
    def YouTubeDownload(self, addr, SongName, idx, total):
        # 지정 파일명
        for ext in self.extList:
            if ext in addr:
                filename = addr
                filepath = self.orgpath + filename
                if isfile(filepath):
                    print(f"{filename} is already exist.")
                    print(f"count:\t <{idx:03} / {total:03}> \t[{SongName}]")
                    return
                e = f"지정한 파일 [{filename}]이 현재 경로에 존재하지 않습니다."
                print(e)
                print(f"→ {filepath}")
                self.download_failed.append({
                    "songname": SongName,
                    "address": addr,
                    "error": e
                })
                return
        
        # 니코동 및 유튜브 주소
        if "nicovideo" in addr:
            filename = f"{addr.split('watch/')[1]}.wav"
        else:
            if "youtu.be/" in addr:
                filename = f"{addr.split('youtu.be/')[1].split('&')[0]}.wav"
            elif "youtube":
                filename = f"{addr.split('?v=')[1].split('&')[0]}.wav"
        filepath = self.orgpath + filename

        if isfile(filepath):
            print(f"{filename} is already exist.")
            print(f"count:\t <{idx:03} / {total:03}> \t[{SongName}]")
            return
        else:
            for sp in self.superpath:
                spname = rootChanger(sp + "\\" + filename)
                if isfile(spname):
                    copy2(spname, filepath)
                    print(f"Copy File: {spname} to {filepath} \t[{SongName}]")
                    return

        # 유튜브 주소 기반 다운로드
        if "youtube" in addr or "youtu.be/" in addr:
            if isfile(filepath):
                print(f"{filename} is already exist.")
            else:
                download_list = [addr, ]
                ydl_opt = {
                    'outtmpl': filepath,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '320',
                    }],
                }

                for z in range(5):
                    try:
                        with YoutubeDL(ydl_opt) as ydl:
                            ydl.download(download_list)
                        break
                    except Exception as e:
                        print(f"Over ERROR {z} in Youbube_dl ({e}) \t[{SongName}]")
                        if z >= 4:
                            print("상기의 이유로 인해 다운로드가 불가능합니다.")
                            self.download_failed.append({
                                "songname": SongName,
                                "address": addr,
                                "error": e
                            })
                            return

                y, sr = libLoad(filepath, sr=44100, mono=False)
                sfWrite(filepath, y.T, sr, format='WAV', 
                        endian='LITTLE', subtype='PCM_16')


        # 니코동 주소 기반 다운로드
        elif "nico" in addr:
            addr = addr.split("?")[0]

            if isfile(filepath):
                print(
                    f"{filename} is already exist.")
            else:
                with NicoNicoVideo(addr) as nico:
                    nico.download(filepath)
                print("Downloaded")

                files = glob(self.orgpath + "*.wa4")
                for x in files:
                    if not isdir(x):
                        filename = splitext(x)
                        try:
                            rename(x, filename[0] + ".wav")
                        except:
                            pass
                y, sr = libLoad(filepath, sr=44100)
                sfWrite(filepath, y, sr, format='WAV',
                        endian='LITTLE', subtype='PCM_16')

        print(f"{filename} download complete. \t{SongName}")
        print(f"count:\t <{idx:03} / {total:03}> \t[{SongName}]")
        sleep(0.5)

    def CutFile(self, addr, SongName, idx, total, cut1, cut2, SI, mono=False):
        isFind = False

        for ext in self.extList:
            if ext in addr:
                filename = addr
                isFind = True
                break

        if isFind:
            pass
        elif "nicovideo" in addr:
            filename = f"{addr.split('watch/')[1]}.wav"
        else:
            if "youtu.be/" in addr:
                filename = f"{addr.split('youtu.be/')[1].split('&')[0]}.wav"
            elif "youtube":
                filename = f"{addr.split('?v=')[1].split('&')[0]}.wav"
        length = round(cut2 - cut1, 5)

        filename2 = f'{idx:03}.wav'

        filepath = self.orgpath + filename

        fileinpath = filepath
        filemidpath = self.cutmidpath + f"↓{cut1}↓{length}↓{mono}↓{SI}↓{filename}"
        fileoutpath = self.cutpath + filename2

        # 이미 잘라놓은 파일 쓰는 경우
        if isfile(filemidpath):
            print(f"Song {filename2[:-4]} {SongName} Convert Complete.")

            copy2(filemidpath, fileoutpath)
        else:
            y, sr = libLoad(fileinpath, sr=44100, mono=mono)

            wanttime = [cut1, cut2]

            if cut1 >= cut2:
                print(f"[{SongName}] 의 StartTime({cut1}) 이 EndTime({cut2}) 보다 큽니다!")
                print(f"FullTime 곡으로 대체합니다.")
                wanttime = [0, 9999]

            # 모노
            if mono:
                y2 = y[int(sr * wanttime[0]):int(sr * wanttime[1])]

                meter = Meter(sr)
                loudness = meter.integrated_loudness(y2)

                loudness2 = loudness

                a = 1

                y3 = y2
            # 스테레오
            else:
                y4 =y[:, int(sr * wanttime[0]):int(sr * wanttime[1])]

                sfWrite(self.cutmidpath + "임시저장.wav", y4.T, sr, format='WAV',
                    endian='LITTLE', subtype='PCM_16')
                y2, sr = libLoad(self.cutmidpath + "임시저장.wav", sr=44100, mono=True)

                meter = Meter(sr)
                loudness = meter.integrated_loudness(y2)

                loudness2 = loudness

                a = 1
                
                y3 = y4
            
            # 음량 조절
            if SI != 0:
                while not(-SI -.05 < loudness2 < -SI):
                    if loudness2 < -SI -.05:
                        a *= 1.01
                    elif loudness2 > -SI:
                        a *= 0.99

                    y3 = y2 * a

                    loudness2 = meter.integrated_loudness(y3)

                print(loudness2)

                if mono:
                    y3 = y2 * round(a, 5)
                else:
                    y3 = y4 * round(a, 5)

            # 파일 저장
            sfWrite(filemidpath, y3.T, sr, format='WAV',
                    endian='LITTLE', subtype='PCM_16')

            copy2(filemidpath, fileoutpath)

            print(
                f"Song {filename2[:-4]} - {SongName} Cut Complete. (highLight = {cut1})")
            print(f"{loudness} \t-> \t{loudness2}")
            sleep(0.5)

        print(f"count:\t {idx:03} / {total:03}")

    def ReadData(self):
        # 정답 위치 설정
        while 1:
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
                
            self.numberCut = [int(x) for x in inputdata]
            break

        # Main Sheet 읽기
        for data in self.wb["Main"]:
            datalist = [x.value for x in data[:]]

            #파일 걸러내기
            if datalist[0] and not isinstance(datalist[0], int):
                continue

            if datalist[0] == None or datalist[0] == "":
                continue

            self.MyDict.append("Song", datalist=datalist, numberCut=self.numberCut)

    def MakeTxt(self):
        self.TriggerDict = {}
        newdx = 10000

        self.key10000keys = []
        self.key10000vals = []

        self.DupleDict = {}

        self.ErrMSG = {
            "SingleLine":[],
            "MultiLine":[]
        }

        self.TxtDict = TxtDict()

        print(DeleteAllFiles(self.txtpath, ".txt"))

        for val in self.MyDict.AnswerDict.keys():
            key = self.MyDict.AnswerDict[val]
            for v in key:
                if key.count(v) > 1:
                    if val not in self.ErrMSG["SingleLine"]:
                        self.ErrMSG["SingleLine"].append(val)

            if len(key) > 1:
                if val not in self.ErrMSG["MultiLine"]:
                    self.ErrMSG["MultiLine"].append(val)
                if str(key) not in self.DupleDict.keys():
                    self.DupleDict[str(key)] = []
                self.DupleDict[str(key)] += [val]
            else:
                if key[0] not in self.TriggerDict:
                    self.TriggerDict[key[0]] = []
                self.TriggerDict[key[0]] += [val]

        self.TxtDict.set_init("DupleTxt", rootChanger(self.txtpath + "\\" + "!중복 여부 확인용.txt"))
        for key, val in self.ErrMSG.items():
            self.TxtDict.add_text("DupleTxt", f"{key}\n: {val}\n")

        if self.ErrMSG["SingleLine"]:
            print("한 줄에서, 같은 정답이 2개 이상 사용되었습니다.")
            print("종료합니다...")
            self.TxtDict.set_write_all(False)
            self.TxtDict.set_write("DupleTxt", True)
            return False

        self.TxtDict.set_init("TriggerTxt", rootChanger(self.txtpath + "\\" + "정답 트리거.txt"))
        self.TxtDict.add_text("TriggerTxt", "[chatEvent]\n__addr__: 0x58D900\n")

        for key in sorted(self.TriggerDict.keys()):
            if 2000 <= key < 10000:
                self.TxtDict.add_text("TriggerTxt", "\n")
                
            for val in self.TriggerDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {key}\n")

        self.TxtDict.add_text("TriggerTxt", "\n")

        for key in self.DupleDict.keys():
            DpKeyList = sorted([int(x) for x in key[1:-1].split(", ")])

            self.key10000keys.append(newdx)
            self.key10000vals.append(DpKeyList)

            for val in self.DupleDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {newdx}\n")

            newdx += 1   

        key10000L = [0]
        key10000 = []
        for v in self.key10000vals:
            key10000L += [key10000L[-1] + len(v)]
            key10000 += v

        if not key10000:
            key10000 = [0]

        self.TxtDict.set_init("key10000ListTxt", rootChanger(self.txtpath + "\\" + "key10000List.txt"))
        self.TxtDict.extend_list("key10000ListTxt", key10000)
        
        self.TxtDict.set_init("key10000LengthTxt", rootChanger(self.txtpath + "\\" + "key10000Length.txt"))
        self.TxtDict.extend_list("key10000LengthTxt", key10000L)

        self.TxtDict.set_init("Song1Txt", rootChanger(self.txtpath + "\\" + "노래 정보 1.txt"))
        self.TxtDict.set_init("Song2Txt", rootChanger(self.txtpath + "\\" + "노래 정보 2.txt"))
        self.TxtDict.set_init("Song3Txt", rootChanger(self.txtpath + "\\" + "노래 정보 3.txt"))
        self.TxtDict.set_init("Song4Txt", rootChanger(self.txtpath + "\\" + "노래 정보 4.txt"))
        self.TxtDict.set_init("Song5Txt", rootChanger(self.txtpath + "\\" + "노래 정보 5.txt"))

        self.TxtDict.set_init("LengthTxt", rootChanger(self.txtpath + "\\" + "노래 길이.txt"))

        self.TxtDict.set_init("Hint1Txt", rootChanger(self.txtpath + "\\" + "초성 - 1 번째.txt"))
        self.TxtDict.set_init("Hint2Txt", rootChanger(self.txtpath + "\\" + "초성 - 2 번째.txt"))
        self.TxtDict.set_init("Hint3Txt", rootChanger(self.txtpath + "\\" + "초성 - 3 번째.txt"))

        self.TxtDict.set_init("SongAnswerTxt", rootChanger(self.txtpath + "\\" + "정답 시 (노래정보 1 & 2 합진 것).txt"))

        self.keylist = sorted(self.MyDict.songDict.keys())

        for key in self.keylist:
            ASDF = self.MyDict.songDict[key]

            vals = ASDF.basic_info
            val = vals[0]
            if vals[1] and vals[0] != vals[1]:
                val = f"{val}({vals[1]})"

            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("SongAnswerTxt", str(mytext))

            val = vals[0]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Song1Txt", str(mytext))

            val = vals[1]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Song2Txt", str(mytext))

            val = vals[2]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Song3Txt", str(mytext))

            val = vals[3]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Song4Txt", str(mytext))

            val = vals[4]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Song5Txt", str(mytext))

            val = "{}, ".format(round(ASDF.time[1] - ASDF.time[0]))
            self.TxtDict.add_text("LengthTxt", str(val))

            vals = ASDF.hint

            if "'" in vals[0]:
                mytext = 'Db("{}"), '.format(vals[0].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[0])
            self.TxtDict.add_text("Hint1Txt", str(mytext))

            if "'" in vals[1]:
                mytext = 'Db("{}"), '.format(vals[1].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[1])
            self.TxtDict.add_text("Hint2Txt", str(mytext))

            if "'" in vals[2]:
                mytext = 'Db("{}"), '.format(vals[2].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[2])
            self.TxtDict.add_text("Hint3Txt", str(mytext))


        self.TxtDict.add_text("TriggerTxt", "\n!강퇴1: 1990\n!강퇴2: 1991\n!강퇴3: 1992\n!강퇴4: 1993\n!강퇴5: 1994\n!강퇴6: 1995\n!강퇴7: 1996\n")
        self.TxtDict.set_write_all(True)
        
        return True

    def Running(self):
        wantDL = None
        isMono = None

        self.ReadData()
        if not self.MakeTxt():
            return

        self.TxtDict.write_text()
        self.TxtDict.close_all_file()
        self.make_config()

        while (wantDL == None):
            in_data = input("노래 다운로드 및 컷팅을 진행하시겠습니까??? (T / F)")

            if in_data in ["T", "t"]:
                wantDL = True
            if in_data in ["F", "f"]:
                wantDL = False
                return

        while (isMono == None):
            in_data = input("Mono Type으로 자르시겠습니까??? (T / F)")

            if in_data in ["T", "t"]:
                isMono = True
            if in_data in ["F", "f"]:
                isMono = False

        SI=None
        while(SI == None):
            in_data = input("원하시는 볼륨 크기를 적어주세요. 숫자가 작을수록, 음량이 커집니다.(볼륨 평준화 용도 / 0은 볼륨 평준화 안한다는 의미)")
            if in_data.isdigit():
                SI = int(in_data)

        idx = 0
        for elememtKey in sorted(self.MyDict.songDict.keys()):
            song = self.MyDict.songDict[elememtKey]

            idx+= 1
            in_dict = {"addr":song.address, "SongName":song.basic_info[0], "idx":idx, "total":self.MyDict.Scount}
            self.YouTubeDownload(**in_dict)

        if self.download_failed:
            with open(rootChanger(self.txtpath + "\\" + "!!!다운로드 이슈.txt"), "w", encoding="utf-8") as f:
                f.write(f"total failed: {len(self.download_failed)}\n\n")
                for failed in self.download_failed:
                    f.write(f'[{failed["songname"]}] was failed at [{failed["address"]}]\n')
                    f.write(f'error: {failed["error"]}\n\n')
            return

        idx = 0
        print(DeleteAllFiles(rootChanger(self.wavpath + "\\cut"), ".wav"))

        for elememtKey in sorted(self.MyDict.songDict.keys()):
            song = self.MyDict.songDict[elememtKey]

            idx+= 1
            in_dict = {"addr":song.address, "SongName":song.basic_info[0], "idx":idx, "total":self.MyDict.Scount, "cut1": song.time[0], "cut2": song.time[1], "SI":SI, "mono":isMono}
            self.CutFile(**in_dict)

        

    def make_config(self):
        print(DeleteAllFiles(rootChanger(self.txtpath), ".eps"))
        with open(rootChanger(self.txtpath + "\\" + "musicConfig.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Song3Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicHint1 = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Hint1Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const ConsonantHint1 = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Hint2Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const ConsonantHint2 = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Hint3Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const ConsonantHint3 = [{mytext}];\n\n")

            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("SongAnswerTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicAnswer = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicLength = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("key10000ListTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key10000List = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("key10000LengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key10000Length = [{mytext}];\n\n")