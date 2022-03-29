from os import listdir, rename
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
temp = "가사맞 \t[22/02/05 수정]"
num = 8
wb = None
MyDict = {}
AnswerDict = {}
ShowDict = {}

SCount = [0]

txtpath = None
wavpath = None
mypath = None

UpperSetting = [1, 1, 1]    # Org, Up, Down
SpaceSetting = [1, 1]       # Org, Off

numberCut = []

def AnswerChanger(answer):
    checkdict = {"\\":"\\\\", ":":"\\:", "=": "\\="}
    res = ""

    for w in str(answer):
        if w in checkdict.keys():
            res += checkdict[w]
        else:
            res += w

    return res

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
            if answer[a] != " ":
                k += 1

    return hint2text, hint3text, hint4text


# 동영상 다운로드
def YouTubeDownload(addr, SongName, idx1, idx2, total):
    orgpath = wavpath + "\\" + "org" + "\\"

    superpath = [x for x in listdir(mypath + "\\__RESULT") if isdir(x)]

    extList = [".mp3", ".wav", ".m4a", ".mp4"]

    # 지정 파일명
    for ext in extList:
        if ext in addr:
            filename = addr
            filepath = orgpath + filename
            if isfile(filepath):
                print(f"{filename} is already exist.")
                print(f"count:\t {idx1:03}-{idx2:03}/ {total:03} \t[{SongName}]")
                return
            print(f"지정한 파일 [{filename}]이 현재 경로에 존재하지 않습니다.")
            print(f"→ {filepath}")
            input()
            exit()
            
    # 니코동 및 유튜브 주소
    if "nicovideo" in addr:
        filename = f"{addr.split('watch/')[1]}.wav"
    else:
        filename = f"{addr.split('?v=')[1].split('&list=')[0]}.wav"
    filepath = orgpath + filename

    if isfile(filepath):
        print(f"{filename} is already exist.")
        print(f"count:\t {idx1:03}-{idx2:03} / {total:03} \t[{SongName}]")
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


def CutFile(addr, SongName, idx1, idx2, total, cut1, cut2, SI, mono=False):
    orgpath = wavpath + "\\" + "org" + "\\"
    cutmidpath = wavpath + "\\" + "cut_saved" + "\\"
    cutpath = wavpath + "\\" + "cut" + "\\"

    extList = [".mp3", ".wav", ".m4a", ".mp4"]

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
        filename = f"{addr.split('?v=')[1].split('&list=')[0]}.wav"

    length = round(cut2 - cut1, 5)

    filename2 = f'{idx1:03}-{idx2:03}.wav'

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

    print(f"count:\t {idx1:03}-{idx2:03} / {total:03}")


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


# 답판정 변경
def makeAnswer(word):
    res = []

    UpperFunction = [nonChange, changeUpperAnswer, changeLowerAnswer]
    Spaceword = [str(word).replace("\\","\\\\").replace(":","\:"), str(word).replace(" ","").replace("\\","\\\\").replace(":","\:")]

    UpperSetting = [1, 0, 0]    # Org, Up, Down
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
    # Main Sheet 읽기
    idx = 0
    idx3 = 0

    for data in wb["Sheet1"]:
        datalist = [x.value for x in data[:]]

        #파일 걸러내기
        if datalist[0] and not isinstance(datalist[0], int):
            continue

        if datalist[0] == None or datalist[0] == "":
            continue

        d1 = datalist[0] - 1

        if d1 not in MyDict:
            MyDict[d1] = {}

        MyDict[d1]["SongName"] = datalist[1]
        MyDict[d1]["SongTName"] = datalist[2]

        MyDict[d1]["SType"] = datalist[4]
        MyDict[d1]["GenreName"] = datalist[5]
        MyDict[d1]["CoverName"] = datalist[6]
        MyDict[d1]["LyricCount"] = datalist[7]

        MyDict[d1]["Address"] = []
        MyDict[d1]["Time"] = []
        MyDict[d1]["Length"] = []
        MyDict[d1]["LyricLength"] = []
        MyDict[d1]["LyricList"] = []
        MyDict[d1]["LyricBar2List"] = []

        for i in range(MyDict[d1]["LyricCount"]):
            MyDict[d1]["Address"].append(datalist[8+i*21])
            MyDict[d1]["Time"].append([x if x else 0 for x in [datalist[9+i*21], datalist[10+i*21]]])
            MyDict[d1]["Length"].append(0 if datalist[11+i*21] == None else round(datalist[11+i*21], 2))
            MyDict[d1]["LyricLength"].append(0 if datalist[12+i*21] == None else datalist[12+i*21])
            dummmy_list = [x for x in datalist[13+i*21:29+i*21] if x]
            MyDict[d1]["LyricList"].append([x.split(" / ") for x in dummmy_list])
            MyDict[d1]["LyricBar2List"].append([makebar2(x[0]) for x in MyDict[d1]["LyricList"][-1]])

            idx2 = 0

            for idx4 in range(MyDict[d1]["LyricLength"][-1]):
                W1 = MyDict[d1]["LyricList"][-1][idx4]
                W2 = MyDict[d1]["LyricList"][-1][idx4+1] if idx4+1< MyDict[d1]["LyricLength"][-1] else None
                W3 = MyDict[d1]["LyricList"][-1][idx4+2] if idx4+2< MyDict[d1]["LyricLength"][-1] else None

                for w1 in W1:
                    if "(N)" not in w1:
                        w1_list = makeAnswer(f"{w1}")
                        for w in w1_list:
                            if w not in AnswerDict.keys():
                                AnswerDict[w] = []
                            AnswerDict[w].append((5000 + idx3 * 100 + idx2)*10+1)

                        if W2:
                            for w2 in W2:
                                if "(N)" not in w2:
                                    w2_list = makeAnswer(f"{w1} {w2}")
                                    for w in w2_list:
                                        if w not in AnswerDict.keys():
                                            AnswerDict[w] = []
                                        AnswerDict[w].append((5000 + idx3 * 100 + idx2)*10+2)

                                    if W3:
                                        for w3 in W3:
                                            if "(N)" not in w3:
                                                w3_list = makeAnswer(f"{w1} {w2} {w3}")
                                                for w in w3_list:
                                                    if w not in AnswerDict.keys():
                                                        AnswerDict[w] = []
                                                    AnswerDict[w].append((5000 + idx3 * 100 + idx2)*10+3)
                idx2 += 1

            idx3 += 1
        idx += 1
        SCount[0] += 1


def MakeTxt():
    STypeDict = {}

    for idx_s, song in MyDict.items():
        SType = str(song["SType"]).replace(" ","")
        if SType not in STypeDict.keys():
            STypeDict[SType] = []
        STypeDict[SType].append(idx_s+1)

    STypeList = []
    for SType in STypeDict.values():
        STypeList.append(SType)

    STypeTxt = open(txtpath + "\\" + "SType별 분류.txt", "w", encoding="utf-8")
    STypeTxt.write(str(STypeList))
    STypeTxt.write("\n\n" + str(len(STypeList)) + "\t예상개수: " + str(len(STypeList) - [len(x) for x in STypeList].count(1)) + " + " + str( [len(x) for x in STypeList].count(1)//2))
    STypeTxt.write("\n\n" + str([len(x) for x in STypeList]))

    STypeTxt.write("\n\n\n\n\n" + str(dict(sorted(STypeDict.items()))))
    STypeTxt.close()


    LyricTriggerTxt = open(txtpath + "\\" + "Lyric 정답 트리거.txt", "w", encoding="utf-8")
    LyricTriggerTxt.write("[chatEvent]\n__addr__: 0x58D900\n")

    newdx = 2000

    keyarrow = []
    KeyDict = {}
    TriggerDict = {}

    key2000List = []
    key2000Lenght = [0]


    for val in AnswerDict.keys():
        key = AnswerDict[val]
        for v in key:
            if key.count(v) > 1:
                print(f"{val} 중복!!!")
                raise NameError
        if len(key) > 1:
            print(f"{val} 가 여러개!, {newdx}에 배정!!")

            TriggerDict[newdx] = [val]

            for v in key:
                KeyDict[v] = newdx

            key2000List += key
            key2000Lenght += [key2000Lenght[-1] + len(key)]
            
            newdx += 1
        
        else:
            if key[0] not in TriggerDict:
                TriggerDict[key[0]] = []
            TriggerDict[key[0]] += [val]

            KeyDict[key[0]] = key[0]

    Key2000 = open(txtpath + "\\" + "key2000List.txt", "w", encoding="utf-8")
    Key2000Len = open(txtpath + "\\" + "key2000Lenght.txt", "w", encoding="utf-8")

    Key2000.write(str(key2000List))
    Key2000.close()

    Key2000Len.write(str(key2000Lenght))
    Key2000Len.close()

    LyricArrowTxt = open(txtpath + "\\" + "Lyric Arrow.txt", "w", encoding="utf-8")


    LyricArrowTxt.write("[")
    for key in sorted(KeyDict.keys()):
        val = KeyDict[key]
        # print(key, end= " / ")
        if (key % 1000) / 10 == 0 and key > 50001:
            LyricArrowTxt.write("],\n[")

        LyricArrowTxt.write(f"{val}, ")

    LyricArrowTxt.write("],")
    LyricArrowTxt.close()

    LyricTriggerTxt.write("\n")

    check_key = 50000 // 250

    mykeys = [x//100 for x in sorted(TriggerDict.keys())]
    mykeys = list(set(mykeys))

    for key in sorted(TriggerDict.keys()):
        for val in TriggerDict[key]:
            if (check_key != (key // 250)) and (key >= 50000):
                check_key = key // 250
                LyricTriggerTxt.write("\n")
            LyricTriggerTxt.write(f"{val}: {key}\n")
            # if val != changeUpperAnswer(val):
            #     LyricTriggerTxt.write(f"{changeUpperAnswer(val)}: {key}\n")

    LyricTriggerTxt.write("\n!강퇴1: 1000\n!강퇴2: 1001\n!강퇴3: 1002\n!강퇴4: 1003\n!강퇴5: 1004\n!강퇴6: 1005\n!강퇴7: 1006\n")

    LyricTriggerTxt.close()

    NameAnswerTxt = open(txtpath + "\\" + "정답 시 - 가수.txt", "w", encoding="utf-8")
    GenreAnswerTxt = open(txtpath + "\\" + "정답 시 - 장르.txt", "w", encoding="utf-8")
    SongAnswerTxt = open(txtpath + "\\" + "정답 시 - 노래.txt", "w", encoding="utf-8")

    SongLengthTxt = open(txtpath + "\\" + "노래 길이.txt", "w", encoding="utf-8")

    LyricTxt = open(txtpath + "\\" + "가사 리스트.txt", "w", encoding="utf-8")
    LyricBar2Txt = open(txtpath + "\\" + "Bar 리스트2.txt", "w", encoding="utf-8")
    LyricLengthTxt = open(txtpath + "\\" + "가사 길이.txt", "w", encoding="utf-8")
    LyricCountTxt = open(txtpath + "\\" + "가사 개수 리스트.txt", "w", encoding="utf-8")
    LyricInitialTxt = open(txtpath + "\\" + "가사 초기 상태 리스트.txt", "w", encoding="utf-8")

    isDoubleListxt = open(txtpath + "\\" + "isDoubleList.txt", "w", encoding="utf-8")
    isDoubleCountTxt = open(txtpath + "\\" + "IsDoubleCount.txt", "w", encoding="utf-8")
    
    LyricTxt.write("const LyricList = [\n")
    LyricBar2Txt.write("const LyricBarList = [\n")
    LyricCount = 0

    TriggerKeyList = TriggerDict.keys()
    myidx = 50000

    keylist = sorted(MyDict.keys())

    for key in keylist:
        ASDF = MyDict[key]
        val = f'{ASDF["SongName"]}'
        if ASDF["SongName"] != ASDF["SongTName"]:
            val += f' ({ASDF["SongTName"]})'
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "'"))
        else:
            mytext = "Db('{}'), ".format(val)
        SongAnswerTxt.write(mytext)

        val = ASDF["LyricCount"]
        LyricCountTxt.write(f"{LyricCount}, ")

        val = f'{ASDF["GenreName"]}'
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "'"))
        else:
            mytext = "Db('{}'), ".format(val)
        GenreAnswerTxt.write(mytext)

        val = f'{ASDF["CoverName"]}'
        if "'" in val:
            mytext = 'Db("{}"), '.format(val.replace('"', "'"))
        else:
            mytext = "Db('{}'), ".format(val)
        NameAnswerTxt.write(mytext)

        LyricCount += ASDF["LyricCount"]

        for i in range(ASDF["LyricCount"]):
            val = ASDF["Length"][i]
            SongLengthTxt.write(f"{round(val/2)*2}, ")

            val = ASDF["LyricLength"][i]
            LyricLengthTxt.write(f"{val}, ")

            LyricInitialTxt

            vals = ASDF["LyricList"][i]
            LyricTxt.write("[")
            LyricInitialTxt.write("[")
            for val in vals:
                val = f"{val[0]}"

                if "(N)" in val:
                    val = val.replace("(N)", "")
                    LyricInitialTxt.write("1, ")
                else:
                    LyricInitialTxt.write("0, ")

                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "'"))
                else:
                    mytext = "Db('{}'), ".format(val)
                LyricTxt.write(mytext)
            LyricTxt.write("],\n")
            LyricInitialTxt.write("],\n")

            vals = ASDF["LyricBar2List"][i]
            LyricBar2Txt.write("[")
            for val in vals:
                val = f"{val}"
                if "'" in val:
                    mytext = 'Db("{}"), '.format(val.replace('"', "'"))
                else:
                    mytext = "Db('{}'), ".format(val)
                LyricBar2Txt.write(mytext)
            LyricBar2Txt.write("],\n")

            MyCount = 0
            MyList = []

            for j in range(myidx, myidx + ASDF["LyricLength"][i]):
                if j not in TriggerKeyList:
                    MyList += [j%100]
                    MyCount += 1

            if len(MyList) == 0:
                MyList = [0]

            isDoubleListxt.write(str(MyList) + ", ")
            isDoubleCountTxt.write(str(MyCount) + ", ")

            myidx += 100

    LyricTxt.write("];")
    LyricBar2Txt.write("];")

    isDoubleListxt.close()
    isDoubleCountTxt.close()

    LyricCountTxt.write(f"{LyricCount}, ")

    NameAnswerTxt.close()
    GenreAnswerTxt.close()
    SongAnswerTxt.close()

    SongLengthTxt.close()

    LyricTxt.close()
    LyricBar2Txt.close()

    LyricLengthTxt.close()
    LyricCountTxt.close()


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

        idx1 = 0
        for elememtKey in sorted(MyDict.keys()):
            song = MyDict[elememtKey]

            idx1+= 1
            for idx2 in range(len(song["Address"])):
                in_dict = {"addr":song["Address"][idx2], "SongName":song["SongName"], "idx1":idx1, "idx2":idx2, "total":SCount[0]}
                YouTubeDownload(**in_dict)

        idx1 = 0
    except Exception as e:
        print(f"에러 발생!: {e}")
        input()
        exit()

    for elememtKey in sorted(MyDict.keys()):
        song = MyDict[elememtKey]

        idx1+= 1
        for idx2 in range(len(song["Address"])):
            in_dict = {"addr":song["Address"][idx2], "SongName":song["SongName"], "idx1":idx1, "idx2":idx2, "total":SCount[0], "cut1": song["Time"][idx2][0], "cut2": song["Time"][idx2][1], "SI":SI, "mono":isMono}
            CutFile(**in_dict)