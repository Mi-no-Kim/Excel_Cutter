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
temp = "카테고리 사용 \t[22/02/27 수정]"
num = 2
wb = None
MyDict = {}
CateDict = {}
AnswerDict = {}

SCount = [0]

txtpath = None
wavpath = None
mypath = None

UpperSetting = [1, 1, 1]    # Org, Up, Down
SpaceSetting = [1, 1]       # Org, Off

numberCut = []

def DeleteAllFiles(filePath, ext):
    if isdir(filePath):
        for file in scandir(filePath):
            if file.path[-len(ext):] == ext:
                remove(file.path)
        return 'Remove All File'
    else:
        return 'Directory Not Found'

# 초성 생성
def checking(word):
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


# 동영상 다운로드
def YouTubeDownload(addr, SongName, idx, total):
    orgpath = wavpath + "\\" + "org" + "\\"

    superpath = [x for x in listdir(mypath + "\\__RESULT") if isdir(x)]

    extList = [".mp3", ".wav", ".m4a", ".mp4", ".MP3", ".WAV", ".M4A", ".MP4"]

    # 지정 파일명
    for ext in extList:
        if ext in addr:
            filename = addr
            filepath = orgpath + filename
            if isfile(filepath):
                print(f"{filename} is already exist.")
                print(f"count:\t {idx:03} / {total:03} \t[{SongName}]")
                return
            print(f"지정한 파일 [{filename}]이 현재 경로에 존재하지 않습니다.")
            print(f"→ {filepath}")
            input()
            exit()
            
    # 니코동 및 유튜브 주소
    if "nicovideo" in addr:
        filename = f"{addr.split('watch/')[1]}.wav"
    else:
        filename = f"{addr.split('?v=')[1]}.wav"
    filepath = orgpath + filename

    if isfile(filepath):
        print(f"{filename} is already exist.")
        print(f"count:\t {idx:03} / {total:03} \t[{SongName}]")
        return
    else:
        for sp in superpath:
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
                        input()
                        exit()

            y, sr = libLoad(filepath, sr=44100, mono=False)
            sfWrite(filepath, y.T, sr, format='WAV', 
                    endian='LITTLE', subtype='PCM_16')

            print(f"{filename} download complete. \t[{SongName}]")

            sleep(0.5)

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

            files = glob(orgpath + "*.wa4")
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


def CutFile(addr, SongName, idx, total, cut1, cut2, SI, mono=False):
    orgpath = wavpath + "\\" + "org" + "\\"
    cutmidpath = wavpath + "\\" + "cut_saved" + "\\"
    cutpath = wavpath + "\\" + "cut" + "\\"

    extList = [".mp3", ".wav", ".m4a", ".mp4", ".MP3", ".WAV", ".M4A", ".MP4"]

    isFind = False

    for ext in extList:
        if ext in addr:
            filename = addr
            isFind = True
            break

    if isFind:
        pass
    elif "nicovideo" in addr:
        filename = f"{addr.split('watch/')[1]}.wav"
    else:
        filename = f"{addr.split('?v=')[1]}.wav"

    length = round(cut2 - cut1, 5)

    filename2 = f'{idx:03}.wav'

    filepath = orgpath + filename

    fileinpath = filepath
    filemidpath = cutmidpath + f"↓{cut1}↓{length}↓{mono}↓{SI}↓{filename}"
    fileoutpath = cutpath + filename2

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

            sfWrite(cutmidpath + "임시저장.wav", y4.T, sr, format='WAV',
                endian='LITTLE', subtype='PCM_16')
            y2, sr = libLoad(cutmidpath + "임시저장.wav", sr=44100, mono=True)

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


# 소문자 변환
def changeLowerAnswer(word):
    new_word = word.lower()

    return new_word


# 대문자 변환
def changeUpperAnswer(word):
    new_word = word.upper()

    return new_word


# 그냥
def nonChange(word):
    return word


# 답판정 변경
def makeAnswer(word):
    res = []

    UpperFunction = [nonChange, changeUpperAnswer, changeLowerAnswer]
    Spaceword = [str(word).replace("\\","\\\\").replace(":","\:"), str(word).replace(" ","").replace("\\","\\\\").replace(":","\:")]

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


# 엑셀 데이터 읽기
def ReadData():
    # 정답 위치 설정
    while 1:
        inputdata = input("정답 칸의 너비를 입력해주세요 (기본: 25)")
        inputdata = inputdata.split(" ")

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

    for data in wb["Category"]:
        datalist = [x.value for x in data[:]]

        if datalist[0] and not isinstance(datalist[0], int):
            continue

        if datalist[0] == None or datalist[0] == "":
            continue

        d1 = datalist[0] - 1

        CateDict[d1] = {}
        CateDict[d1]["CateName"] = datalist[1]
        CateDict[d1]["List"] = []

    # Main Sheet 읽기
    for data in wb["Main"]:
        datalist = [x.value for x in data[:]]

        #파일 걸러내기
        if datalist[0] and not isinstance(datalist[0], int):
            continue

        if datalist[0] == None or datalist[0] == "":
            continue

        d1 = datalist[0] - 1
        d2 = datalist[2] - 1
        
        CateDict[d2]["List"].append(d1)

        if d1 not in MyDict:
            MyDict[d1] = {}

        for idx_data, data in enumerate(datalist[3:8]):
            if data == None:
                MyDict[d1][f"Song{idx_data+1}"] = ""
            else:
                MyDict[d1][f"Song{idx_data+1}"] = str(data)

        MyDict[d1]["Address"] = str(datalist[8])
        MyDict[d1]["Time"] = [x if x else 0 for x in [datalist[9], datalist[10]]]

        MyDict[d1]["Ans"] =[]

        ansidx = 11
        MyDict[d1]["Hint"] = makehint(datalist[ansidx])

        for i in numberCut:
            MyDict[d1]["Ans"].append([str(x) for x in datalist[ansidx:ansidx+i] if x])
            ansidx += i

        for idx, anslist in enumerate(MyDict[d1]["Ans"]):
            for ans in anslist:
                for a in makeAnswer(ans):
                    if a not in AnswerDict:
                        AnswerDict[a] = []
                    AnswerDict[a].append(d1 + 1000*(idx+2))

        SCount[0] += 1


def MakeTxt():
    TriggerDict = {}
    newdx = 10000

    key10000keys = []
    key10000vals = []

    DupleDict = {}

    ErrMSG = {
        "SingleLine":[],
        "MultiLine":[]
    }

    print(DeleteAllFiles(txtpath, ".txt"))

    DupleTxt = open(txtpath + "\\" + "!중복 여부 확인용.txt", "w", encoding="utf-8")

    for val in AnswerDict.keys():
        key = AnswerDict[val]
        for v in key:
            if key.count(v) > 1:
                if val not in ErrMSG["SingleLine"]:
                    ErrMSG["SingleLine"].append(val)

        if len(key) > 1:
            if val not in ErrMSG["MultiLine"]:
                ErrMSG["MultiLine"].append(val)
            if str(key) not in DupleDict.keys():
                DupleDict[str(key)] = []
            DupleDict[str(key)] += [val]
        else:
            if key[0] not in TriggerDict:
                TriggerDict[key[0]] = []
            TriggerDict[key[0]] += [val]

    for key, val in ErrMSG.items():
        DupleTxt.write(f"{key}\n: {val}\n")
    DupleTxt.close()

    if ErrMSG["SingleLine"]:
        print("한 줄에서, 같은 정답이 2개 이상 사용되었습니다.")
        print("종료합니다...")
        input()
        exit()

    TriggerTxt = open(txtpath + "\\" + "정답 트리거.txt", "w", encoding="utf-8")
    TriggerTxt.write("[chatEvent]\n__addr__: 0x58D900\n")

    for key in sorted(TriggerDict.keys()):
        if 2000 <= key < 10000:
            TriggerTxt.write("\n")
            
        for val in TriggerDict[key]:
            TriggerTxt.write(f"{val}: {key}\n")

    TriggerTxt.write("\n")
    for key in DupleDict.keys():
        DpKeyList = [int(x) for x in key[1:-1].split(", ")]

        key10000keys.append(newdx)
        key10000vals.append(DpKeyList)

        for val in DupleDict[key]:
            TriggerTxt.write(f"{val}: {newdx}\n")

        newdx += 1    

    key10000L = [0]
    key10000 = []
    for v in key10000vals:
        key10000L += [key10000L[-1] + len(v)]
        key10000 += v
        
    if not key10000:
        key10000 = [0]

    Key10000Txt = open(txtpath + "\\" + "Key10000.txt", "w", encoding="utf-8")
    Key10000Txt.write(str(key10000L) + "\n\n")
    Key10000Txt.write(str(key10000))
    Key10000Txt.close()

    Song1Txt = open(txtpath + "\\" + "노래 정보 1.txt", "w", encoding="utf-8")
    Song2Txt = open(txtpath + "\\" + "노래 정보 2.txt", "w", encoding="utf-8")
    Song3Txt = open(txtpath + "\\" + "노래 정보 3.txt", "w", encoding="utf-8")
    Song4Txt = open(txtpath + "\\" + "노래 정보 4.txt", "w", encoding="utf-8")
    Song5Txt = open(txtpath + "\\" + "노래 정보 5.txt", "w", encoding="utf-8")

    LengthTxt = open(txtpath + "\\" + "노래 길이.txt", "w", encoding="utf-8")

    Hint1Txt = open(txtpath + "\\" + "초성 - 1 번째.txt", "w", encoding="utf-8")
    Hint2Txt = open(txtpath + "\\" + "초성 - 2 번째.txt", "w", encoding="utf-8")
    Hint3Txt = open(txtpath + "\\" + "초성 - 3 번째.txt", "w", encoding="utf-8")

    CateTxt = open(txtpath + "\\" + "CateList.txt", "w", encoding="utf-8")
    CateNameTxt = open(txtpath + "\\" + "CateName.txt", "w", encoding="utf-8")
    CateLengthTxt = open(txtpath + "\\" + "CateLengthList.txt", "w", encoding="utf-8")

    SongAnswerTxt = open(txtpath + "\\" + "정답 시 (노래정보 1 & 2 합진 것).txt", "w", encoding="utf-8")

    keylist = MyDict.keys()

    for key in sorted(keylist):
        ASDF = MyDict[key]

        val = ASDF["Song1"]
        if ASDF["Song2"] and ASDF["Song1"] != ASDF["Song2"]:
            val = f"{val}({ASDF['Song2']})"

        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        SongAnswerTxt.write(mytext)

        val = ASDF["Song1"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        Song1Txt.write(mytext)

        val = ASDF["Song2"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        Song2Txt.write(mytext)

        val = ASDF["Song3"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        Song3Txt.write(mytext)

        val = ASDF["Song4"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        Song4Txt.write(mytext)

        val = ASDF["Song5"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        Song5Txt.write(mytext)

        val = round(ASDF["Time"][1] - ASDF["Time"][0])
        LengthTxt.write(f"{val}, ")

        vals = ASDF["Hint"]

        if "'" in vals[0]:
            mytext = 'Db("{}"), '.format(vals[0].replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(vals[0])
        Hint1Txt.write(mytext)

        if "'" in vals[1]:
            mytext = 'Db("{}"), '.format(vals[1].replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(vals[1])
        Hint2Txt.write(mytext)

        if "'" in vals[2]:
            mytext = 'Db("{}"), '.format(vals[2].replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(vals[2])
        Hint3Txt.write(mytext)

    for k2 in sorted(CateDict.keys()):
        if CateDict[k2]["List"]:
            CateTxt.write("\n\t" + str(CateDict[k2]["List"]) + ",")
        else:
            CateTxt.write("\n\t" + str([0]) + ",")
        CateLengthTxt.write(f"{len(CateDict[k2]['List'])}, ")
        
        val = CateDict[k2]["CateName"]
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "\\\""))
        else:
            mytext = "Db('{}'), ".format(val)
        CateNameTxt.write(mytext)

    CateTxt.close()

    CateNameTxt.close()

    CateLengthTxt.close()

    Song1Txt.close()
    Song2Txt.close()
    Song3Txt.close()
    Song4Txt.close()
    Song5Txt.close()

    LengthTxt.close()

    Hint1Txt.close()
    Hint2Txt.close()
    Hint3Txt.close()

    SongAnswerTxt.close()

    TriggerTxt.write("\n")
    TriggerTxt.write("!강퇴1: 1990\n!강퇴2: 1991\n!강퇴3: 1992\n!강퇴4: 1993\n!강퇴5: 1994\n!강퇴6: 1995\n!강퇴7: 1996\n")

    TriggerTxt.close()


# 함수 작동
def Running():
    try:
        ReadData()
        MakeTxt()

        wantDL = None
        isMono = None

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
        for elememtKey in sorted(MyDict.keys()):
            song = MyDict[elememtKey]

            idx+= 1
            in_dict = {"addr":song["Address"], "SongName":song["Song1"], "idx":idx, "total":SCount[0]}
            YouTubeDownload(**in_dict)

        idx = 0
    except Exception as e:
        print(f"에러 발생!: {e}")
        input()
        exit()

    print(DeleteAllFiles(wavpath + "\\cut", ".wav"))

    for elememtKey in sorted(MyDict.keys()):
        song = MyDict[elememtKey]

        idx+= 1
        in_dict = {"addr":song["Address"], "SongName":song["Song1"], "idx":idx, "total":SCount[0], "cut1": song["Time"][0], "cut2": song["Time"][1], "SI":SI, "mono":isMono}
        CutFile(**in_dict)