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