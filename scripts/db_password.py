source = """
0x600001f18820: 0xf5 0xfe 0xf4 0xbe 0xb2 0x49 0x44 0xb2
0x600001f18828: 0x95 0x1a 0x9e 0x23 0xed 0x5b 0x4c 0xed
0x600001f18830: 0xd6 0x5f 0x0d 0x2b 0x5c 0x5d 0x4a 0xe6
0x600001f18838: 0x8f 0x21 0xdb 0x36 0xfd 0x62 0x9d 0x42
"""


key = '0x' + ''.join(i.partition(':')[2].replace('0x', '').replace(' ', '') for i in source.split('\n')[1:5])
print(key)




0xf5fef4beb24944b2951a9e23ed5b4cedd65f0d2b5c5d4ae68f21db36fd629d42



### https://www.programmersought.com/article/2091815747/