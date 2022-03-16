import requests
from Crypto.Cipher import AES

headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1",
    "Referer": "http://www.szaitai.com/"
}


def aesDecode(data, key):
    '''
    Decode the data
    :param data: stream, the data need to decode
    :param key: secret key
    :return: decode the data
    '''
    crypt = AES.new(key, AES.MODE_CBC, key)
    plain_text = crypt.decrypt(data)
    return plain_text.rstrip(b'\0')


def CatchVideos(i):
    # ts文件链接
    url = "https://v3.dious.cc/20220312/lKc9iA7g/2000kb/hls/JDjqh18W.ts"
    r = requests.get(url, verify=False)
    with open('m.mp4', 'ab') as f:
        f.write(aesDecode(r.content, b'0fc90196cc89b9df'))


if __name__ == '__main__':
    CatchVideos(0)
    # 我发现的ts文件链接规律，即每一个ts链接后缀是有顺序的，因此改变后缀数字即可
    # for i in range(139, 400):
    #     try:
    #         CatchVideos(i)
    #         print(i)
    #     except:
    #         print("Eorr!!!!")
    #         break
