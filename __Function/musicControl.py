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


class Downloader:
    def __init__(self):
        self.__platform = "Windows"

        self.__filePath = None
        self.__superPath = None

        self.extList = [".mp3", ".wav", ".m4a", ".mp4", ".MP3", ".WAV", ".M4A", ".MP4"]

        self.__download_failed = []

        self.mono = False
    
    def return_download_failed(self):
        return self.__download_failed

    def setPlatform(self, platform):
        self.__platform = platform

    def slash(self):
        return "/" if self.__platform == "Linux" else "\\"

    def setPath(self, filePath, resultPath):
        self.__filePath = filePath
        self.__superPath = [x for x in listdir(resultPath) if isdir(x)]

        self.__orgPath = self.__filePath + self.slash() + "org" + self.slash()
        self.__cutMidPath = self.__filePath + self.slash() + "cut_saved" + self.slash()
        self.__cutPath = self.__filePath + self.slash() + "cut" + self.slash()

        
    def YouTubeDownload(self, addr, showName, saveName, currentCnt, totalCnt):
        if self.__filePath == None:
            return False

        # 지정 파일명
        for ext in self.extList:
            if ext in addr:
                filename = addr
                filepath = self.__orgPath + filename

                if isfile(filepath):
                    print(f"{filename} is already exist.")
                    print(f"count:\t <{saveName}({currentCnt:03}) / {totalCnt:03}> \t[{showName}]")

                    return True

                e = f"지정한 파일 [{filename}]이 현재 경로에 존재하지 않습니다."
                print(e)
                print(f"→ {filepath}")
                self.__download_failed.append({
                    "songname": showName,
                    "address": addr,
                    "error": e
                })
                return False
        
        # 니코동 및 유튜브 주소
        if "nicovideo" in addr:
            filename = f"{addr.split('watch/')[1]}.wav"
        else:
            if "youtu.be/" in addr:
                filename = f"{addr.split('youtu.be/')[1].split('&')[0]}.wav"
            elif "youtube" in addr:
                filename = f"{addr.split('?v=')[1].split('&')[0]}.wav"
        filepath = self.__orgPath + filename

        if isfile(filepath):
            print(f"{filename} is already exist.")
            print(f"count:\t <{saveName}({currentCnt:03}) / {totalCnt:03}> \t[{showName}]")

            return True
        else:
            for sp in self.__superPath:
                spname = sp + self.slash() + filename
                if isfile(spname):
                    copy2(spname, filepath)
                    print(f"Copy File: {spname} to {filepath} \t[{showName}]")
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
                        print(f"Over ERROR {z} in Youbube_dl ({e}) \t[{showName}]")
                        if z >= 4:
                            print("상기의 이유로 인해 다운로드가 불가능합니다.")
                            self.__download_failed.append({
                                "songname": showName,
                                "address": addr,
                                "error": e
                            })
                            return False

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

                files = glob(self.__orgPath + "*.wa4")
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

        print(f"{filename} download complete. \t{showName}")
        print(f"count:\t <{saveName}({currentCnt:03}) / {totalCnt:03}> \t[{showName}]")
        sleep(0.5)
        return True

    def CutFile(self, addr, showName, saveName, currentCnt, totalCnt, cut1, cut2, SI):
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

        filename2 = f'{saveName}.wav'

        filepath = self.__orgPath + filename

        fileinpath = filepath
        filemidpath = self.__cutMidPath + f"↓{cut1}↓{length}↓{self.mono}↓{SI}↓{filename}"
        fileoutpath = self.__cutPath + filename2

        # 이미 잘라놓은 파일 쓰는 경우
        if isfile(filemidpath):
            print(f"Song {filename2[:-4]} {showName} Convert Complete.")

            copy2(filemidpath, fileoutpath)
        else:
            y, sr = libLoad(fileinpath, sr=44100, mono=self.mono)

            wanttime = [cut1, cut2]

            if cut1 >= cut2:
                print(f"[{showName}] 의 StartTime({cut1}) 이 EndTime({cut2}) 보다 큽니다!")
                print(f"FullTime 곡으로 대체합니다.")
                wanttime = [0, 9999]

            # 모노
            if self.mono:
                y2 = y[int(sr * wanttime[0]):int(sr * wanttime[1])]

                meter = Meter(sr)
                loudness = meter.integrated_loudness(y2)

                loudness2 = loudness

                a = 1

                y3 = y2
            # 스테레오
            else:
                y4 =y[:, int(sr * wanttime[0]):int(sr * wanttime[1])]

                sfWrite(self.__cutMidPath + "임시저장.wav", y4.T, sr, format='WAV',
                    endian='LITTLE', subtype='PCM_16')
                y2, sr = libLoad(self.__cutMidPath + "임시저장.wav", sr=44100, mono=True)

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

                if self.mono:
                    y3 = y2 * round(a, 5)
                else:
                    y3 = y4 * round(a, 5)

            # 파일 저장
            sfWrite(filemidpath, y3.T, sr, format='WAV',
                    endian='LITTLE', subtype='PCM_16')

            copy2(filemidpath, fileoutpath)

            print(
                f"Song {filename2[:-4]} - {showName} Cut Complete. (highLight = {cut1})")
            print(f"{loudness} \t-> \t{loudness2}")
            sleep(0.5)

        print(f"count:\t <{saveName}({currentCnt:03}) / {totalCnt:03}>")
        return True