import pickle as pk

class Info():
    def __init__(self):
        self.idx = 1
        self.info = "기본성능"
        self.last_date = "2022/04/17"

pk.dump()

PICKLE_DEFAULT = '''customname = "DEFAULT";
ReadInfo = [
    {
        "sheetName": "Main",
        "function": "readSong",
        "range": ["start", "end"],
        "column: [
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
    },
];
writeInfo = [
    {
        "name": "musicInfo1",
        "write": "노래 정보 1.txt",
        "type": "musicInfo",
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
        "type": "musicInfoConjoin()",
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
];
configInfo = [
{
    "MusicAnswer",
    "musicInfo3",
    "musicLength",
    "musicConsonantHint1",
    "musicConsonantHint2",
    "musicConsonantHint3",
    "duple",
    "dulpeLength",
];'''

