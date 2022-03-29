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

# 기본 설정
temp = "정답 2개 \t[22/02/05 수정]"
num = 3

def DeleteAllFiles(filePath, ext):
    """파일 전부 삭제"""
    if isdir(filePath):
        for file in scandir(filePath):
            if file.path[-len(ext):] == ext:
                remove(file.path)
        return 'Remove All File'
    else:
        return 'Directory Not Found'


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


class MyAni:
    def __init__(self):
        self.idx1 = None
        self.basic_info = None
        self.answer = None
        self.hint = None
        self.songs = None


class MySong:
    def __init__(self):
        self.idx1 = None
        self.idx2 = None
        self.idx3 = None
        self.basic_info = None
        self.address = None
        self.time = None
        self.answer = None
        self.hint = None


class MyDict:
    AnswerDict = {}
    Scount = 0
    def __init__(self):
        self.aniDict = {}
        self.songDict = {}
        self.ansidx1 = 6
        self.ansidx2 = 12

    def append(self, appendType, datalist, numberCut):
        """
        appendType: Ani(애니), Song(노래)
        """
        if appendType == "Ani":
            d1 = datalist[0] - 1
            ansidx = self.ansidx1

            if d1 not in self.songDict:
                self.aniDict[d1] = MyAni()
                self.aniDict[d1].idx1 = d1
            else:
                raise IndexError

            self.aniDict[d1].basic_info = [str(data) if data else "" for data in datalist[1:6]]
            self.aniDict[d1].answer = []
            self.aniDict[d1].hint = makehint(datalist[ansidx])
            self.aniDict[d1].songs = []

            for i in numberCut:
                self.aniDict[d1].answer.append([str(x) for x in datalist[ansidx:ansidx+i] if x])
                ansidx += i

            for idx, anslist in enumerate(self.aniDict[d1].answer):
                for ans in anslist:
                    for a in makeAnswer(ans):
                        if a not in self.AnswerDict:
                            self.AnswerDict[a] = []
                        self.AnswerDict[a].append(d1 + 1000*(idx+2))  

        elif appendType == "Song":
            d1 = datalist[0] - 1
            d2 = datalist[1] - 1
            d3 = datalist[3] - 1
            ansidx = self.ansidx2

            myD = f"{d1:03}-{d2:03}"

            if myD not in self.songDict:
                self.songDict[myD] = MySong()
                self.songDict[myD].idx1 = d1
                self.songDict[myD].idx2 = d2
                self.songDict[myD].idx3 = d3
            else:
                raise IndexError

            self.aniDict[d3].songs.append(self.Scount)
            self.songDict[myD].basic_info = [str(data) if data else "" for data in datalist[4:9]]
            self.songDict[myD].address = str(datalist[9])
            self.songDict[myD].time = [x if x else 0 for x in [datalist[10], datalist[11]]]
            self.songDict[myD].answer = []
            self.songDict[myD].hint = makehint(datalist[ansidx])

            for i in numberCut:
                self.songDict[myD].answer.append([str(x) for x in datalist[ansidx:ansidx+i] if x])
                ansidx += i

            for idx, anslist in enumerate(self.songDict[myD].answer):
                for ans in anslist:
                    for a in makeAnswer(ans):
                        if a not in self.AnswerDict:
                            self.AnswerDict[a] = []
                        self.AnswerDict[a].append(self.Scount + 1000*(idx+12))
            
            self.Scount += 1


class TxtDict:
    def __init__(self) -> None:
        self.Dict = {}


    def set_init(self, name, link):
        self.Dict[name] = {}
        self.Dict[name]["text"] = ""
        self.Dict[name]["link"] = link
        self.Dict[name]["list"] = []

    def add_list(self, name, data):
        self.Dict[name]["list"].append(data)

    def add_text(self, name, text):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["text"] = ""
            self.Dict[name]["link"] = f".\\{name}"
        
        self.Dict[name]["text"] += text

    def return_text(self, name):
        return self.Dict[name]["text"]

    def return_list(self, name, idx1=None, idx2=None):
        if idx1 == None:
            return self.Dict[name]["list"]
        elif idx2 == None:
            return self.Dict[name]["list"][idx1]
        return self.Dict[name]["list"][idx1:idx2]

    def write_text(self):
        for name in self.Dict.keys():
            with open(self.Dict[name]["link"], "w", encoding="utf-8") as f:
                if self.Dict[name]["text"]:        
                    f.write(self.Dict[name]["text"])
                else:
                    f.write(str(self.Dict[name]["list"])[1:-1])


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

        self.orgpath = self.wavpath + "\\" + "org" + "\\"
        self.superpath = [x for x in listdir(self.mypath + "\\__RESULT") if isdir(x)]
        self.extList = [".mp3", ".wav", ".m4a", ".mp4", ".MP3", ".WAV", ".M4A", ".MP4"]
        self.cutmidpath = self.wavpath + "\\" + "cut_saved" + "\\"
        self.cutpath = self.wavpath + "\\" + "cut" + "\\"
    
    def YouTubeDownload(self, addr, SongName, idx1, idx2, now, total):
        # 지정 파일명
        for ext in self.extList:
            if ext in addr:
                filename = addr
                filepath = self.orgpath + filename
                if isfile(filepath):
                    print(f"{filename} is already exist.")
                    print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03} \t[{SongName}]")
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
            filename = f"{addr.split('?v=')[1].split('&list=')[0]}.wav"
        filepath = self.orgpath + filename

        if isfile(filepath):
            print(f"{filename} is already exist.")
            print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03} \t[{SongName}]")
            return
        else:
            for sp in self.superpath:
                spname = sp + "\\" + filename
                if isfile(spname):
                    copy2(spname, filepath)
                    print(f"Copy File: {spname} to {filepath} \t[{SongName}]")
                    return

        # 유튜브 주소 기반 다운로드
        if "youtube" in addr:
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
        print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03} \t[{SongName}]")
        sleep(0.5)

    def CutFile(self, addr, SongName, idx1, idx2, now, total, cut1, cut2, SI, mono=False):
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
            filename = f"{addr.split('?v=')[1].split('&list=')[0]}.wav"

        length = round(cut2 - cut1, 5)

        filename2 = f'{idx1+1:03}-{idx2+1:03}.wav'

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

        print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03}")

    def ReadData(self):
        # 정답 위치 설정[애니]
        while 1:
            inputdata = input("[애니] 정답 칸의 너비를 입력해주세요 (기본: 15)")
            inputdata = inputdata.split()

            isBreak = False

            for i in inputdata:
                if not i.isdigit():
                    print(f"{i} 는 숫자가 아닙니다! 다시 입력해주시기 바랍니다!")
                    isBreak = True

                    break
            
            if isBreak:
                continue
                
            self.aniNumberCut = [int(x) for x in inputdata]
            break

        for data in self.wb["Ani"]:
            datalist = [x.value for x in data[:]]

            if datalist[0] and not isinstance(datalist[0], int):
                continue

            if datalist[0] == None or datalist[0] == "":
                continue

            self.MyDict.append("Ani", datalist=datalist, numberCut=self.aniNumberCut)

        # 정답 위치 설정[노래]
        while 1:
            inputdata = input("[노래] 정답 칸의 너비를 입력해주세요 (기본: 15)")
            inputdata = inputdata.split()

            isBreak = False

            for i in inputdata:
                if not i.isdigit():
                    print(f"{i} 는 숫자가 아닙니다! 다시 입력해주시기 바랍니다!")
                    isBreak = True

                    break
            
            if isBreak:
                continue
                
            self.songNumberCut = [int(x) for x in inputdata]
            break

        # Song Sheet 읽기
        for data in self.wb["Song"]:
            datalist = [x.value for x in data[:]]

            #파일 걸러내기
            if datalist[0] and not isinstance(datalist[0], int):
                continue

            if datalist[0] == None or datalist[0] == "":
                continue

            self.MyDict.append("Song", datalist=datalist, numberCut=self.songNumberCut)

    def MakeTxt(self):
        self.TriggerDict = {}
        newdx = 20000

        self.key20000keys = []
        self.key20000vals = []

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

        self.TxtDict.set_init("DupleTxt", self.txtpath + "\\" + "!중복 여부 확인용.txt")
        for key, val in self.ErrMSG.items():
            self.TxtDict.add_text("DupleTxt", f"{key}\n: {val}\n")

        if self.ErrMSG["SingleLine"]:
            print("한 줄에서, 같은 정답이 2개 이상 사용되었습니다.")
            print("종료합니다...")
            input()
            exit()

        self.TxtDict.set_init("TriggerTxt", self.txtpath + "\\" + "정답 트리거.txt")
        self.TxtDict.add_text("TriggerTxt", "[chatEvent]\n__addr__: 0x58D900\n")

        for key in sorted(self.TriggerDict.keys()):
            if 2000 <= key < 20000:
                self.TxtDict.add_text("TriggerTxt", "\n")
                
            for val in self.TriggerDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {key}\n")

        self.TxtDict.add_text("TriggerTxt", "\n")

        for key in self.DupleDict.keys():
            DpKeyList = sorted([int(x) for x in key[1:-1].split(", ")])

            self.key20000keys.append(newdx)
            self.key20000vals.append(DpKeyList)

            for val in self.DupleDict[key]:
                self.TxtDict.add_text("TriggerTxt", f"{val}: {newdx}\n")

            newdx += 1   

        key20000L = [0]
        key20000 = []
        for v in self.key20000vals:
            key20000L += [key20000L[-1] + len(v)]
            key20000 += v

        if not key20000:
            key20000 = [0]

        self.TxtDict.set_init("Key20000Txt", self.txtpath + "\\" + "Key20000.txt")


        self.TxtDict.set_init("Ani1Txt", self.txtpath + "\\" + "애니 정보 1.txt")
        self.TxtDict.set_init("Ani2Txt", self.txtpath + "\\" + "애니 정보 2.txt")
        self.TxtDict.set_init("Ani3Txt", self.txtpath + "\\" + "애니 정보 3.txt")
        self.TxtDict.set_init("Ani4Txt", self.txtpath + "\\" + "애니 정보 4.txt")
        self.TxtDict.set_init("Ani5Txt", self.txtpath + "\\" + "애니 정보 5.txt")

        self.TxtDict.set_init("AniHint1Txt", self.txtpath + "\\" + "애니 초성 - 1 번째.txt")
        self.TxtDict.set_init("AniHint2Txt", self.txtpath + "\\" + "애니 초성 - 2 번째.txt")
        self.TxtDict.set_init("AniHint3Txt", self.txtpath + "\\" + "애니 초성 - 3 번째.txt")

        self.TxtDict.set_init("AniAnswerTxt", self.txtpath + "\\" + "애니 정답 시 (노래정보 1 & 2 합진 것).txt")

        self.TxtDict.set_init("AnitoSongListTxt", self.txtpath + "\\" + "애니→노래 할당.txt")
        self.TxtDict.set_init("AnitoSongLengthTxt", self.txtpath + "\\" + "애니→노래 길이.txt")

        self.TxtDict.set_init("Key20000Txt", self.txtpath + "\\" + "Key20000.txt")
        self.TxtDict.add_text("Key20000Txt", str(key20000L) + "\n\n")
        self.TxtDict.add_text("Key20000Txt", str(key20000))

        self.TxtDict.set_init("Song1Txt", self.txtpath + "\\" + "노래 정보 1.txt")
        self.TxtDict.set_init("Song2Txt", self.txtpath + "\\" + "노래 정보 2.txt")
        self.TxtDict.set_init("Song3Txt", self.txtpath + "\\" + "노래 정보 3.txt")
        self.TxtDict.set_init("Song4Txt", self.txtpath + "\\" + "노래 정보 4.txt")
        self.TxtDict.set_init("Song5Txt", self.txtpath + "\\" + "노래 정보 5.txt")

        self.TxtDict.set_init("LengthTxt", self.txtpath + "\\" + "노래 길이.txt")

        self.TxtDict.set_init("SongHint1Txt", self.txtpath + "\\" + "노래 초성 - 1 번째.txt")
        self.TxtDict.set_init("SongHint2Txt", self.txtpath + "\\" + "노래 초성 - 2 번째.txt")
        self.TxtDict.set_init("SongHint3Txt", self.txtpath + "\\" + "노래 초성 - 3 번째.txt")

        self.TxtDict.set_init("SongAnswerTxt", self.txtpath + "\\" + "노래 정답 시 (노래정보 1 & 2 합진 것).txt")


        self.keylist = sorted(self.MyDict.aniDict.keys())
        self.TxtDict.add_list("AnitoSongListTxt", 0)
        for key in self.keylist:
            ASDF = self.MyDict.aniDict[key]

            vals = ASDF.basic_info
            val = vals[0]
            if vals[1] and vals[0] != vals[1]:
                val = f"{val}({vals[1]})"

            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("AniAnswerTxt", str(mytext))

            val = vals[0]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Ani1Txt", str(mytext))

            val = vals[1]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Ani2Txt", str(mytext))

            val = vals[2]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Ani3Txt", str(mytext))

            val = vals[3]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Ani4Txt", str(mytext))

            val = vals[4]
            if "'" in val:
                mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(val)
            self.TxtDict.add_text("Ani5Txt", str(mytext))

            vals = ASDF.hint

            if "'" in vals[0]:
                mytext = 'Db("{}"), '.format(vals[0].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[0])
            self.TxtDict.add_text("AniHint1Txt", str(mytext))

            if "'" in vals[1]:
                mytext = 'Db("{}"), '.format(vals[1].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[1])
            self.TxtDict.add_text("AniHint2Txt", str(mytext))

            if "'" in vals[2]:
                mytext = 'Db("{}"), '.format(vals[2].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[2])
            self.TxtDict.add_text("AniHint3Txt", str(mytext))

            val = ASDF.songs
            self.TxtDict.add_list("AnitoSongLengthTxt", self.TxtDict.return_list("AnitoSongListTxt", -1) + len(val))
            self.TxtDict.add_text("AnitoSongListTxt", f'[{", ".join(map(str, val))}], ')

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
            self.TxtDict.add_text("SongHint1Txt", str(mytext))

            if "'" in vals[1]:
                mytext = 'Db("{}"), '.format(vals[1].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[1])
            self.TxtDict.add_text("SongHint2Txt", str(mytext))

            if "'" in vals[2]:
                mytext = 'Db("{}"), '.format(vals[2].replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(vals[2])
            self.TxtDict.add_text("SongHint3Txt", str(mytext))

        self.TxtDict.add_text("TriggerTxt", "\n!강퇴1: 1990\n!강퇴2: 1991\n!강퇴3: 1992\n!강퇴4: 1993\n!강퇴5: 1994\n!강퇴6: 1995\n!강퇴7: 1996\n")

    def Running(self):
        wantDL = None
        isMono = None

        self.ReadData()
        self.MakeTxt()
        self.TxtDict.write_text()


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

        for now, elememtKey in enumerate(sorted(self.MyDict.songDict.keys())):
            song = self.MyDict.songDict[elememtKey]

            in_dict = {"addr":song.address, "SongName":song.basic_info[0], "idx1":song.idx1, "idx2":song.idx2, "now":now, "total":self.MyDict.Scount}
            self.YouTubeDownload(**in_dict)

        if self.download_failed:
            with open(self.txtpath + "\\" + "다운로드 이슈.txt", "w", encoding="utf-8") as f:
                f.write(f"total failed: {len(self.download_failed)}\n\n")
                for failed in self.download_failed:
                    f.write(f'[{failed["songname"]}] was failed at [{failed["address"]}]\n')
                    f.write(f'error: {failed["error"]}\n\n')
            return

        print(DeleteAllFiles(self.wavpath + "\\cut", ".wav"))

        for now, elememtKey in enumerate(sorted(self.MyDict.songDict.keys())):
            song = self.MyDict.songDict[elememtKey]

            in_dict = {"addr":song.address, "SongName":song.basic_info[0], "idx1":song.idx1, "idx2":song.idx2, "now": now, "total":self.MyDict.Scount, "cut1": song.time[0], "cut2": song.time[1], "SI":SI, "mono":isMono}
            self.CutFile(**in_dict)