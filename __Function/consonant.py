from numpy import full


def makeSingleConsonant(word):
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
            

def makeConsonants(input_string, convert_type):
    fullConsonant = "".join([makeSingleConsonant(w) for w in input_string])

    if len(fullConsonant) == 1:
        return fullConsonant
    
    output_string = ""
    cnt = 0
    type_len = len(convert_type)
    for idx in range(len(fullConsonant)):
        if convert_type[cnt%type_len] == "*":
            output_string += input_string[idx]
        else:
            output_string += fullConsonant[idx]
        
        if "가" <= input_string[idx] <= "힣":
            cnt += 1

    return output_string
