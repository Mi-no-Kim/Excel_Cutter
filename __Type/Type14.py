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


temp = "MashUp(특수사양)\t[22/04/30 수정]"
num = 14
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
def replace_show(word):
    res = word
    res = res.replace("\\","\\\\")
    res = res.replace("“", "\"").replace("”",  "\"")
    res = res.replace("‘", "\'").replace("’",  "\'")
    res = res.replace("…", "...")

    return res


def replace_answer(word):
    res = word
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



class MySong:
    def __init__(self):
        self.idx1 = None
        self.c1 = None
        self.basic_info = None
        self.address = None
        self.time = None
        self.answer = None
        self.hint = None


class MyDict:
    AnswerDict = {}
    Scount = 0
    def __init__(self):
        self.songDict = {}
        self.nameidx = 2
        self.ansidx = 27
        self.addridx = 15

    def append(self, appendType ,datalist, numberCut=None):
        """
        appendType: Song(노래)
        """
        if appendType == "Song":
            # datalist 안의 숫자가, 열 번호-1 을 의미합니다. 만약 열을 바꾸셨다면, 이 숫자부터 바꿔보는 것을 추천합니다.
            d1 = datalist[0] - 1
            ansidx = self.ansidx
            nameidx = self.nameidx
            addridx = self.addridx

            if d1 not in self.songDict:
                self.songDict[d1] = MySong()
                self.songDict[d1].idx1 = d1
            else:
                raise IndexError

            c1 = datalist[1]
            c2 = datalist[14]
            
            self.songDict[d1].c1 = c1
            self.songDict[d1].c2 = c2

            self.songDict[d1].basic_info = [[str(data) if data else "" for data in datalist[nameidx+c*4:nameidx+(c+1)*4]] for c in range(c1)]
            self.songDict[d1].address = [str(data) if data else "" for data in datalist[addridx:addridx+c2*3:3]]
            self.songDict[d1].time = [[x if x else 0 for x in datalist[addridx+c*3+1:addridx+(c+1)*3]] for c in range(c2)]
            self.songDict[d1].answer = [[str(data) for data in datalist[ansidx+c*10:ansidx+(c+1)*10] if data] for c in range(c1) ]
            self.songDict[d1].hint = [makehint(data) for data in datalist[ansidx:ansidx+(c1)*10:10]]

            sample = [[""], [""], [""]]

            for idx, anslist in enumerate(self.songDict[d1].answer):
                for ans in anslist:
                    for a in makeAnswer(ans):
                        if a not in self.AnswerDict:
                            self.AnswerDict[a] = []
                        self.AnswerDict[a].append(10000 + d1*10 + idx)
                        sample[idx].append(a)
            
            
            for v1 in sample[0]:
                for v2 in sample[1]:
                    # 3: 0 & 1
                    v12 = [f"{v1} {v2}", f"{v2} {v1}", f"{v1}{v2}", f"{v2}{v1}"]
                    for val in v12:
                        if len(val.encode()) <= 78 and (v1 != "" and v2 != ""):
                            if self.AnswerDict.get(val) == None:
                                self.AnswerDict[val] = []
                            self.AnswerDict[val].append(10000 + d1*10 + 3)

                    for v3 in sample[2]:
                        # 4: 0 & 2
                        if v2 == sample[1][0]:
                            v13 = [f"{v1} {v3}", f"{v3} {v1}", f"{v1}{v3}", f"{v3}{v1}"]
                            for val in v13:
                                if len(val.encode()) <= 78 and (v1 != "" and v3 != ""):
                                    if self.AnswerDict.get(val) == None:
                                        self.AnswerDict[val] = []
                                    self.AnswerDict[val].append(10000 + d1*10 + 4)

                        # 5: 1 & 2
                        if v1 == sample[0][0]:
                            v23 = [f"{v2} {v3}", f"{v3} {v2}", f"{v2}{v3}", f"{v3}{v2}"]
                            for val in v23:
                                if len(val.encode()) <= 78 and (v2 != "" and v3 != ""):
                                    if self.AnswerDict.get(val) == None:
                                        self.AnswerDict[val] = []
                                    self.AnswerDict[val].append(10000 + d1*10 + 5)

                        # 6: 0 & 1 & 2
                        v123 = [f"{v1} {v2} {v3}", f"{v1} {v3} {v2}", f"{v2} {v1} {v3}", f"{v2} {v3} {v1}", f"{v3} {v1} {v2}", f"{v3} {v2} {v1}"]
                        v123 += [f"{v1}{v2}{v3}", f"{v1}{v3}{v2}", f"{v2}{v1}{v3}", f"{v2}{v3}{v1}", f"{v3}{v1}{v2}", f"{v3}{v2}{v1}"]
                        for val in v123:
                            if len(val.encode()) <= 78 and (v1 != "" and v2 != "" and v3 != ""):
                                if self.AnswerDict.get(val) == None:
                                    self.AnswerDict[val] = []
                                self.AnswerDict[val].append(10000 + d1*10 + 6)

            self.Scount += 1


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
    
    def YouTubeDownload(self, addr, SongName, idx1, idx2, total):
        # 지정 파일명
        for ext in self.extList:
            if ext in addr:
                filename = addr
                filepath = self.orgpath + filename
                if isfile(filepath):
                    print(f"{filename} is already exist.")
                    print(f"count:\t <{idx1:03}-{idx2:03} / {total:03}> \t[{SongName}]")
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
            print(f"count:\t <{idx1:03}-{idx2:03} / {total:03}> \t[{SongName}]")
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
        print(f"count:\t <{idx1:03}-{idx2:03} / {total:03}> \t[{SongName}]")
        sleep(0.5)

    def CutFile(self, addr, SongName, idx1, idx2, total, cut1, cut2, SI, mono=False):
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

        filename2 = f'{idx1:03}-{idx2:03}.wav'

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
                try:
                    y4 =y[:, int(sr * wanttime[0]):int(sr * wanttime[1])]

                    sfWrite(self.cutmidpath + "임시저장.wav", y4.T, sr, format='WAV',
                        endian='LITTLE', subtype='PCM_16')
                    y2, sr = libLoad(self.cutmidpath + "임시저장.wav", sr=44100, mono=True)

                    meter = Meter(sr)
                    loudness = meter.integrated_loudness(y2)

                    loudness2 = loudness

                    a = 1
                    
                    y3 = y4
                except:
                    mono = True
                    y2 = y[int(sr * wanttime[0]):int(sr * wanttime[1])]

                    meter = Meter(sr)
                    loudness = meter.integrated_loudness(y2)

                    loudness2 = loudness

                    a = 1

                    y3 = y2
            
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

        print(f"count:\t {idx1:03}-{idx2:03} / {total:03}")

    def ReadData(self):
        # Main Sheet 읽기
        for data in self.wb["Main"]:
            datalist = [x.value for x in data[:]]

            #파일 걸러내기
            if datalist[0] and not isinstance(datalist[0], int):
                continue

            if datalist[0] == None or datalist[0] == "":
                continue

            self.MyDict.append("Song", datalist=datalist)

    def MakeTxt(self):
        self.TriggerDict = {}
        newdx = 2000

        self.key2000keys = []
        self.key2000vals = []

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
            if 10000 <= key:
                self.TxtDict.add_text("TriggerTxt", "\n")
                
            for val in self.TriggerDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {key}\n")

        self.TxtDict.add_text("TriggerTxt", "\n")

        for key in self.DupleDict.keys():
            DpKeyList = sorted([int(x) for x in key[1:-1].split(", ")])

            self.key2000keys.append(newdx)
            self.key2000vals.append(DpKeyList)

            for val in self.DupleDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {newdx}\n")

            newdx += 1   

        key2000L = [0]
        key2000 = []
        for v in self.key2000vals:
            key2000L += [key2000L[-1] + len(v)]
            key2000 += v

        if not key2000:
            key2000 = [0]

        self.TxtDict.set_init("key2000ListTxt", rootChanger(self.txtpath + "\\" + "key2000List.txt"))
        self.TxtDict.extend_list("key2000ListTxt", key2000)
        
        self.TxtDict.set_init("key2000LengthTxt", rootChanger(self.txtpath + "\\" + "key2000Length.txt"))
        self.TxtDict.extend_list("key2000LengthTxt", key2000L)

        self.TxtDict.set_init("Song1Txt", rootChanger(self.txtpath + "\\" + "노래 정보 1.txt"))
        self.TxtDict.set_init("Song2Txt", rootChanger(self.txtpath + "\\" + "노래 정보 2.txt"))
        self.TxtDict.set_init("Song3Txt", rootChanger(self.txtpath + "\\" + "노래 정보 3.txt"))
        self.TxtDict.set_init("Song4Txt", rootChanger(self.txtpath + "\\" + "노래 정보 4.txt"))

        self.TxtDict.set_init("LengthTxt", rootChanger(self.txtpath + "\\" + "노래 길이.txt"))

        self.TxtDict.set_init("Hint1Txt", rootChanger(self.txtpath + "\\" + "초성 - 1 번째.txt"))
        self.TxtDict.set_init("Hint2Txt", rootChanger(self.txtpath + "\\" + "초성 - 2 번째.txt"))
        self.TxtDict.set_init("Hint3Txt", rootChanger(self.txtpath + "\\" + "초성 - 3 번째.txt"))

        self.TxtDict.set_init("SongAnswerTxt", rootChanger(self.txtpath + "\\" + "정답 시 (노래정보 1 & 2 합진 것).txt"))

        self.TxtDict.set_init("Count1Txt", rootChanger(self.txtpath + "\\" + "노래 당 섞인 곡 수.txt"))
        self.TxtDict.set_init("Count2Txt", rootChanger(self.txtpath + "\\" + "노래 당 재생 곡 수.txt"))

        self.keylist = sorted(self.MyDict.songDict.keys())

        vB = 0
        self.TxtDict.add_text("Count2Txt", f"{vB}, ")

        for key in self.keylist:
            ASDF = self.MyDict.songDict[key]

            self.TxtDict.add_text("SongAnswerTxt", "[")
            self.TxtDict.add_text("Song1Txt", "[")
            self.TxtDict.add_text("Song2Txt", "[")
            self.TxtDict.add_text("Song3Txt", "[")
            self.TxtDict.add_text("Song4Txt", "[")
            self.TxtDict.add_text("Hint1Txt", "[")
            self.TxtDict.add_text("Hint2Txt", "[")
            self.TxtDict.add_text("Hint3Txt", "[")

            self.TxtDict.add_text("Count1Txt", f"{ASDF.c1}, ")
            for c in range(ASDF.c1):
                vals = ASDF.basic_info[c]
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

                vals = ASDF.hint[c]

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

            self.TxtDict.add_text("Hint1Txt", "], ")
            self.TxtDict.add_text("Hint2Txt", "], ")
            self.TxtDict.add_text("Hint3Txt", "], ")

            self.TxtDict.add_text("SongAnswerTxt", "], ")
            self.TxtDict.add_text("Song1Txt", "], ")
            self.TxtDict.add_text("Song2Txt", "], ")
            self.TxtDict.add_text("Song3Txt", "], ")
            self.TxtDict.add_text("Song4Txt", "], ")

            # --------------------------------------------------------------

            self.TxtDict.add_text("LengthTxt", "[")

            vB += ASDF.c2
            self.TxtDict.add_text("Count2Txt", f"{vB}, ")
            for c in range(ASDF.c2):

                val = "{}, ".format(round(ASDF.time[c][1] - ASDF.time[c][0]))
                self.TxtDict.add_text("LengthTxt", str(val))

            self.TxtDict.add_text("LengthTxt", "], ")

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

        print("-" * 20)
        while (wantDL == None):
            in_data = input("노래 다운로드 및 컷팅을 진행하시겠습니까??? (T / F)")

            if in_data in ["T", "t"]:
                wantDL = True
            if in_data in ["F", "f"]:
                wantDL = False
                return

        print("-" * 20)
        while (isMono == None):
            in_data = input("Mono Type으로 자르시겠습니까??? (T / F)")

            if in_data in ["T", "t"]:
                isMono = True
            if in_data in ["F", "f"]:
                isMono = False

        print("-" * 20)
        SI=None
        while(SI == None):
            in_data = input("원하시는 볼륨 크기를 적어주세요. 숫자가 작을수록, 음량이 커집니다.(볼륨 평준화 용도 / 0은 볼륨 평준화 안한다는 의미)")
            if in_data.isdigit():
                SI = int(in_data)

        idx1 = 0
        for elememtKey in sorted(self.MyDict.songDict.keys()):
            song = self.MyDict.songDict[elememtKey]

            idx1 += 1

            for idx2 in range(song.c2):
                in_dict = {"addr":song.address[idx2], "SongName":"/".join([x[0] for x in song.basic_info]), "idx1":idx1, "idx2":idx2, "total":self.MyDict.Scount}
                print(in_dict)
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

            for idx2 in range(song.c2):
                in_dict = {"addr":song.address[idx2], "SongName":"/".join([x[0] for x in song.basic_info]), "idx1":idx, "idx2":idx2, "total":self.MyDict.Scount, "cut1": song.time[idx2][0], "cut2": song.time[idx2][1], "SI":SI, "mono":isMono}
                print(in_dict)
                self.CutFile(**in_dict)


    def make_config(self):
        # print(DeleteAllFiles(rootChanger(self.txtpath), ".eps"))
        with open(rootChanger(self.txtpath + "\\" + "musicConfig.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Song3Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicHint1 = [{mytext}];\n\n")
            
            with open(rootChanger(self.TxtDict.get_link("Song4Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicHint2 = [{mytext}];\n\n")
            
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
            with open(rootChanger(self.TxtDict.get_link("key2000ListTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key2000List = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("key2000LengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key2000Length = [{mytext}];\n\n")

            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Count1Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const Count1Txt = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Count2Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const Count2Txt = [{mytext}];\n\n")