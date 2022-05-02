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


temp = "가사맞2 \t[22/02/26 수정]"
num = 9
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


# 색 바꿔가며 전각 underbar
def makebar2(word):
    outword = ""

    mycount = 0
    myarr = ["\\x04","\\x08"]

    for w in word.replace("(N)", ""):
        if w == " ":
            outword += w
        else:
            mycount = (mycount + 1) % 2
            outword += myarr[mycount] + "＿"

    return outword


def calculateMylength(myword):
    res = 0
    for w in str(myword):
        if w.isdigit():
            res += .75
        elif w in "()[]{}":
            res += .5
        elif w.encode().isalpha():
            res += .75
        elif w == " ":
            res += .75
        else:
            res += 1
    
    return res


class MyCut:
    def __init__(self):
        self.idx2 = None
        self.singer = None
        self.address = None
        self.time = None

        self.lyrics_length = None
        self.lyrics_init_state = None
        self.lyrics_answer = None
        self.show_lyrics_answer = []
        self.show_lyrics_bar = []
        self.lyrics_line = None
        self.lyrics_line_length = None


class MySong:
    def __init__(self):
        """idx1: 노래 순번 / idx2: 노래 cut 번호 / idx3: artist구분 번호"""
        self.idx1 = None
        self.basic_info = []
        self.option1 = []
        # 텍스트 분리 시, length list를 따로 만들자
        self.cuts = {}
        # 가사 길이 & 가사 표시 & 가사 정답 & 


class MyDict:
    AnswerDict = {}
    Scount = 0
    Lcount = 0
    def __init__(self):
        self.songDict = {}
        self.typeDict = {}
        self.infoidx = 2
        self.optionidx = 6
        self.addridx = 9
        self.ansidx = 14

    def append(self, appendType, datalist, numberCut=None):
        """
        appendType: Song(노래)
        """
        if appendType == "Song":
            d1 = datalist[0] - 1
            d2 = datalist[1] - 1

            infoidx = self.infoidx
            optionidx = self.optionidx
            addridx = self.addridx
            ansidx = self.ansidx

            if d1 not in self.songDict:
                self.songDict[d1] = MySong()
                self.songDict[d1].idx1 = d1
                self.songDict[d1].basic_info = [str(data) if data else "" for data in datalist[infoidx:infoidx+4]]
                self.songDict[d1].option1 = [str(data) if data else "" for data in datalist[optionidx:optionidx+2]]
                
            else:
                if self.songDict[d1].cuts.get(d2) != None:
                    raise IndexError

            self.songDict[d1].cuts[d2] = MyCut()
            self.songDict[d1].cuts[d2].idx2 = d2
            
            self.songDict[d1].cuts[d2].singer = str(datalist[optionidx+2])
            self.songDict[d1].cuts[d2].address = str(datalist[addridx])
            self.songDict[d1].cuts[d2].time = [x if x else 0 for x in datalist[addridx+1:addridx+3]]
            self.songDict[d1].cuts[d2].lyrics_length = 0 if datalist[addridx+4] == None else datalist[addridx+4]
            lyrics_org = [x for x in datalist[ansidx:] if x]

            self.songDict[d1].cuts[d2].lyrics_line = [0]
            self.songDict[d1].cuts[d2].lyrics_init_state = [1 if "(N)" in x else 0 for x in lyrics_org]
            self.songDict[d1].cuts[d2].show_lyrics_answer = []
            lyrics_split = [x.split(" / ") for x in lyrics_org[:self.songDict[d1].cuts[d2].lyrics_length] if x]
        
            typeKey = self.songDict[d1].option1[0]
            if self.typeDict.get(typeKey) == None:
                self.typeDict[typeKey] = []
            if d1 not in self.typeDict[typeKey]:
                self.typeDict[typeKey].append(d1)

            idx4 = 0
            idx5 = -2

            for idx6 in range(self.songDict[d1].cuts[d2].lyrics_length):
                W1 = lyrics_split[idx6]
                W2 = lyrics_split[idx6+1] if idx6+1< self.songDict[d1].cuts[d2].lyrics_length else None
                W3 = lyrics_split[idx6+2] if idx6+2< self.songDict[d1].cuts[d2].lyrics_length else None
                W4 = lyrics_split[idx6+3] if idx6+3< self.songDict[d1].cuts[d2].lyrics_length else None
                W5 = lyrics_split[idx6+4] if idx6+4< self.songDict[d1].cuts[d2].lyrics_length else None
                    

                idx5 += 2.5
                myword = lyrics_split[idx6][0].replace("(N)", "").replace("  ", " ")
                self.songDict[d1].cuts[d2].show_lyrics_answer.append(myword)
                self.songDict[d1].cuts[d2].show_lyrics_bar.append(makebar2(myword))
                mylen = calculateMylength(myword)

                if idx5 + mylen <= 51:
                    self.songDict[d1].cuts[d2].lyrics_line[-1] += 1
                    idx5 += mylen
                else:
                    self.songDict[d1].cuts[d2].lyrics_line.append(self.songDict[d1].cuts[d2].lyrics_line[-1]+1)
                    idx5 = mylen

                w_list = []
                Ws = [W1, W2, W3, W4, W5]
                
                for W in Ws:
                    if not W:
                        break

                    isbreak = False
                    for w in W:
                        if "(N)" in w:
                            isbreak = True
                            break
                    if isbreak:
                        break

                    w_list.append([""])
                    for w in W:
                        w_list[-1].append(w)
                
                selected = [0 for _ in w_list]
                max_select = [len(w) for w in w_list]

                if not selected:
                    continue
                while selected[0] < max_select[0]:
                    selected[-1] += 1
                    for i in range(len(selected)-1, 0, -1):
                        if selected[i] >= max_select[i]:
                            selected[i] = 0
                            selected[i-1] += 1

                    iscontinue = False
                    for idx_s, s in enumerate(selected):
                        
                        if s == 0:
                            if idx_s == len(selected):
                                continue
                            if sum(selected[idx_s:]) != 0:
                                iscontinue = True
                                break
                    if iscontinue:
                        continue
                    
                    if selected[0] >= max_select[0]:
                        break

                    # print(w_list)
                    # print(selected)
                    # print(max_select)
                    w_conjoined = " ".join([w_li[selected[idx]] for idx, w_li in enumerate(w_list)]).strip()
                    
                    idx7 = len(w_list) - selected.count(0)-1
                    if "(yu)" in w_conjoined:
                        idx7 += 5
                        w_conjoined = w_conjoined.replace("(yu)", "")


                    for w_conjoined_answer in makeAnswer(w_conjoined):
                        if w_conjoined_answer not in self.AnswerDict.keys():
                            self.AnswerDict[w_conjoined_answer] = []

                        self.AnswerDict[w_conjoined_answer].append((5000 + self.Scount*100 + idx6)*10+idx7)
                        # print(f"{w_conjoined_answer}: {(5000 + self.Scount*100 + idx6)*10+idx7}")
            self.songDict[d1].cuts[d2].lyrics_line_length=len(self.songDict[d1].cuts[d2].show_lyrics_answer)
            self.Lcount += 1
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

    def add_list(self, name, data):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["link"] = rootChanger(f".\\{name}")
            self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")

        self.Dict[name]["list"].append(data)

    def add_text(self, name, text):
        if name not in self.Dict.keys():
            self.Dict[name] = {}
            self.Dict[name]["link"] = rootChanger(f".\\{name}")
            self.Dict[name]["file"] = open(self.Dict[name]["link"], "w", encoding="utf-8")
        
        self.Dict[name]["file"].write(text)

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
            if "youtu.be/" in addr:
                filename = f"{addr.split('youtu.be/')[1].split('&')[0]}.wav"
            elif "youtube":
                filename = f"{addr.split('?v=')[1].split('&')[0]}.wav"
        filepath = self.orgpath + filename

        if isfile(filepath):
            print(f"{filename} is already exist.")
            print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03} \t[{SongName}]")
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
            if "youtu.be/" in addr:
                filename = f"{addr.split('youtu.be/')[1].split('&')[0]}.wav"
            elif "youtube":
                filename = f"{addr.split('?v=')[1].split('&')[0]}.wav"
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

        print(f"count:\t <{idx1+1:03}-{idx2+1:03}> {now+1:03} / {total:03}")

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
        self.KeyDict = {}
        newdx = 2000

        self.key2000List = []
        self.key2000Length = [0]

        self.DupleDict = {}

        self.ErrMSG = {
            "SingleLine":[],
            "MultiLine":[]
        }

        self.TxtDict = TxtDict()

        print(DeleteAllFiles(self.txtpath, ".txt"))
        # print(self.MyDict.AnswerDict)

        for val in self.MyDict.AnswerDict.keys():
            key = self.MyDict.AnswerDict[val]
            key2 = [x//1000 for x in key]

            for v in key2:
                if key2.count(v) > 1:
                    if f"{val}:{v-50+3}" not in self.ErrMSG["SingleLine"]:
                        self.ErrMSG["SingleLine"].append(f"{val}:{v-50+3}")

            if len(key) > 1:
                if val not in self.ErrMSG["MultiLine"]:
                    self.ErrMSG["MultiLine"].append(val)

                self.TriggerDict[newdx] = [val]

                for v in key:
                    self.KeyDict[v] = newdx

                self.key2000List += key
                self.key2000Length += [self.key2000Length[-1] + len(key)]

                newdx += 1
            else:
                if key[0] not in self.TriggerDict:
                    self.TriggerDict[key[0]] = []
                self.TriggerDict[key[0]] += [val]

                self.KeyDict[key[0]] = key[0]

        self.TxtDict.set_init("DupleTxt", rootChanger(self.txtpath + "\\" + "!중복 여부 확인용.txt"))
        for key, val in self.ErrMSG.items():
            if key == "SingleLine":
                val.sort(key = lambda x: (int(x.split(":")[-1]), x))
            self.TxtDict.add_text("DupleTxt", f"{key}\n: {val}\n")

        if self.ErrMSG["SingleLine"]:
            print("한 줄에서, 같은 정답이 2개 이상 사용되었습니다.")
            print("종료합니다...")
            self.TxtDict.set_write_all(False)
            self.TxtDict.set_write("DupleTxt", True)
            return False


        self.TxtDict.set_init("Key2000Txt", self.txtpath + "\\" + "key2000List.txt")
        self.TxtDict.set_init("Key2000LenTxt", self.txtpath + "\\" + "key2000Length.txt")

        idx = 0
        limit_len = len(self.key2000List)
        while idx < limit_len:
            if idx+100 >= limit_len:
                self.TxtDict.add_text("Key2000Txt", str(self.key2000List[idx:])[1:-1]+",\n")
                break
            self.TxtDict.add_text("Key2000Txt", str(self.key2000List[idx:idx+100])[1:-1]+",\n")
            idx += 100

        idx = 0
        limit_len = len(self.key2000Length)
        while idx < limit_len:
            if idx+100 >= limit_len:
                self.TxtDict.add_text("Key2000LenTxt", str(self.key2000Length[idx:])[1:-1]+",\n")
                break
            self.TxtDict.add_text("Key2000LenTxt", str(self.key2000Length[idx:idx+100])[1:-1]+",\n")
            idx += 100


        self.TxtDict.set_init("TriggerTxt", rootChanger(self.txtpath + "\\" + "정답 트리거.txt"))
        self.TxtDict.add_text("TriggerTxt", "[chatEvent]\n__addr__: 0x58D900\n")


        check_key = 50000 // 250

        mykeys = [x//100 for x in sorted(self.TriggerDict.keys())]
        mykeys = list(set(mykeys))

        idx_end = len(self.TriggerDict.keys())
        for idx, key in enumerate(sorted(self.TriggerDict.keys())):
            for val in self.TriggerDict[key]:
                if (check_key != (key // 250)) and (key >= 50000):
                    check_key = key // 250
                    self.TxtDict.add_text("TriggerTxt", "\n")
                self.TxtDict.add_text("TriggerTxt", f"{val}: {key}\n") 
            print(f"{idx:03} / {idx_end:03}")


        self.TxtDict.set_init("Song1Txt", self.txtpath + "\\" + "노래 정보 1.txt")
        self.TxtDict.set_init("Song2Txt", self.txtpath + "\\" + "노래 정보 2.txt")
        self.TxtDict.set_init("Song3Txt", self.txtpath + "\\" + "노래 정보 3.txt")
        self.TxtDict.set_init("Song4Txt", self.txtpath + "\\" + "노래 정보 4.txt")
        self.TxtDict.set_init("Song5Txt", self.txtpath + "\\" + "노래 정보 5.txt")
        self.TxtDict.set_init("Song6Txt", self.txtpath + "\\" + "노래 정보 6.txt")

        self.TxtDict.set_init("SongLengthTxt", self.txtpath + "\\" + "노래 길이.txt")

        self.TxtDict.set_init("SongAnswerTxt", self.txtpath + "\\" + "정답 시 - 노래 (노래정보 1 & 2 합진 것).txt")
        self.TxtDict.set_init("SongTypeTxt", self.txtpath + "\\" + "정답 시 - 장르 (노래정보 6).txt")
        self.TxtDict.set_init("SongSingerTxt", self.txtpath + "\\" + "정답 시 - 가수 (노래정보 7).txt")

        self.TxtDict.set_init("ShowLyricsTxt", self.txtpath + "\\" + "가사 리스트.txt")
        self.TxtDict.set_init("ShowBarTxt", self.txtpath + "\\" + "Bar 리스트.txt")

        self.TxtDict.set_init("LyricLengthTxt", self.txtpath + "\\" + "가사 길이 리스트.txt")
        self.TxtDict.set_init("LyricCountTxt", self.txtpath + "\\" + "가사 개수 리스트.txt")
        self.TxtDict.set_init("LyricInitialTxt", self.txtpath + "\\" + "가사 초기 상태 리스트.txt")

        self.TxtDict.set_init("LyricSettingTxt", self.txtpath + "\\" + "가사 줄 리스트.txt")
        self.TxtDict.set_init("LyricSettingLengthTxt", self.txtpath + "\\" + "가사 줄 길이 리스트.txt")

        self.TxtDict.add_list("LyricCountTxt", 0)

        self.keylist = sorted(self.MyDict.songDict.keys())
        for key in self.keylist:
            ASDF = self.MyDict.songDict[key]

            vals = ASDF.basic_info
            val = vals[0]
            if vals[1] and vals[0] != vals[1]:
                val = f"{val}({vals[1]})"

            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("SongAnswerTxt", str(mytext))

            val = vals[0]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("Song1Txt", str(mytext))

            val = vals[1]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("Song2Txt", str(mytext))

            val = vals[2]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("Song3Txt", str(mytext))

            val = vals[3]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("Song4Txt", str(mytext))

            vals = ASDF.option1
            val = vals[0]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("Song5Txt", str(mytext))

            val = vals[1]
            if "'" in val:
                mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
            else:
                mytext = "Db('{}'), ".format(replace_show(val, False))
            self.TxtDict.add_text("SongTypeTxt", str(mytext))

            self.TxtDict.add_list("LyricCountTxt", self.TxtDict.return_list("LyricCountTxt", -1) + len(ASDF.cuts))

            self.TxtDict.add_text("ShowLyricsTxt", "[")
            self.TxtDict.add_text("ShowBarTxt", "[")

            for idx, asdf in ASDF.cuts.items():
                val = asdf.singer
                if "'" in val:
                    mytext = 'Db("{}"), '.format(replace_show(val, False).replace('"', "\\\""))
                else:
                    mytext = "Db('{}'), ".format(replace_show(val, False))
                self.TxtDict.add_text("Song6Txt", str(mytext))
                self.TxtDict.add_text("SongSingerTxt", str(mytext))

                val = "{}, ".format(round(asdf.time[1] - asdf.time[0]))
                self.TxtDict.add_text("SongLengthTxt", str(val))

                val = ['Db("{}"), '.format(replace_show(x, False).replace('"', "\\\"")) for x in asdf.show_lyrics_answer]
                mytext = f'[{"".join(val)}]' + ',\n'
                self.TxtDict.add_text("ShowLyricsTxt", str(mytext))

                val = ['Db("{}"), '.format(replace_show(x, False).replace('"', "\\\"")) for x in asdf.show_lyrics_bar]
                mytext = f'[{"".join(val)}]' + ',\n'
                self.TxtDict.add_text("ShowBarTxt", str(mytext))

                val = "{}, ".format(asdf.lyrics_length)
                self.TxtDict.add_text("LyricLengthTxt", str(val))

                val = "{},\n".format(asdf.lyrics_init_state)
                self.TxtDict.add_text("LyricInitialTxt", str(val))

                val = "{}, ".format(asdf.lyrics_line)
                self.TxtDict.add_text("LyricSettingTxt", str(mytext))

                val = "{}, ".format(asdf.lyrics_line_length)
                self.TxtDict.add_text("LyricSettingLengthTxt", str(mytext))

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

        now = 0
        for now1, elememtKey in enumerate(sorted(self.MyDict.songDict.keys())):
            song = self.MyDict.songDict[elememtKey]

            for now2, cutKey in enumerate(sorted(song.cuts.keys())):
                cut = song[cutKey]

                now += 1
                in_dict = {"addr":cut.address, "SongName":song.basic_info[0], "idx1":song.idx1, "idx2":cut.idx2, "now":now, "total":self.MyDict.Lcount}
                self.YouTubeDownload(**in_dict)

        if self.download_failed:
            with open(rootChanger(self.txtpath + "\\" + "!!!다운로드 이슈.txt"), "w", encoding="utf-8") as f:
                f.write(f"total failed: {len(self.download_failed)}\n\n")
                for failed in self.download_failed:
                    f.write(f'[{failed["songname"]}] was failed at [{failed["address"]}]\n')
                    f.write(f'error: {failed["error"]}\n\n')
            return

        print(DeleteAllFiles(rootChanger(self.wavpath + "\\cut"), ".wav"))

        now = 0
        for now1, elememtKey in enumerate(sorted(self.MyDict.songDict.keys())):
            song = self.MyDict.songDict[elememtKey]

            for now2, cutKey in enumerate(sorted(song.cuts.keys())):
                cut = song[cutKey]

                now += 1
                in_dict = {"addr":cut.address, "SongName":song.basic_info[0], "idx1":song.idx1, "idx2":song.idx2, "now": now, "total":self.MyDict.Lcount, "cut1": cut.time[0], "cut2": cut.time[1], "SI":SI, "mono":isMono}
                self.CutFile(**in_dict)

        

    def make_config(self):
        print(DeleteAllFiles(rootChanger(self.txtpath), ".eps"))
        with open(rootChanger(self.txtpath + "\\" + "musicConfig.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("SongAnswerTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const SongAnswer = [{mytext}];\n\n")

            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("SongTypeTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const SongType = [{mytext}];\n\n")

            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("SongSingerTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const SongSinger = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("SongLengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const MusicLength = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricLengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricLength = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricCountTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricCount = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricInitialTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricInitiState = [{mytext}];\n\n")

            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricSettingTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricSetting = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("LyricSettingLengthTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const LyricSettingLength = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Key2000Txt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key2000List = [{mytext}];\n\n")
            
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("Key2000LenTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const key2000Length = [{mytext}];\n\n")

        with open(rootChanger(self.txtpath + "\\" + "L1.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("ShowLyricsTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L1 = [{mytext}];\n\n")

        with open(rootChanger(self.txtpath + "\\" + "L2.eps"), "w", encoding="utf-8") as f:
            mytext = ""
            with open(rootChanger(self.TxtDict.get_link("ShowBarTxt")), "r", encoding="utf-8") as f1:
                mytext = "".join(f1.readlines())
            f.write(f"const L2 = [{mytext}];\n\n")