import requests
from Cryptodome.Cipher import AES
from base64 import b64encode
import json

# 找到未加密的参数
# 找到网易的加密逻辑 params => encText, encSecKey => encSecKey
# 请求网易，拿到评论结果

url = "https://music.163.com/weapi/comment/resource/comments/get"

data = {
    "csrf_token": "",
    "cursor": "-1",
    "offset": "0",
    "orderType": "1",
    "pageNo": "1",
    "pageSize": "20",
    "rid": "R_SO_4_1891469546",
    "threadId": "R_SO_4_1891469546"
}

# 从 js 代码调试中固定数值抠出
i = "MBAAjfjwsNfIahdV"
encSecKey = "09681fb7a33476bfd4ed13544381c31a244734d1d529bd1a7739542f79bffef1126506226c1a79686a214ce9dd97f949a89cccfb206fa2aab7f687ce67131c7b40a9b15219e37e6a3b4db60e52afe1aeb63e5b09ae6690a5630be3e5ae1736f6e0a75865cbf0757cf3c51b51515d6640ed43391ef474a2f649bc5419b2607e54"
# 从 Console 中执行代码抠出
g = "0CoJUm6Qyw8W8jud"

def get_params(data):
    first = enc_params(data, g)
    second = enc_params(first, i)
    return second

def to_16(data):
    pad = 16 - len(data) % 16
    data += chr(pad) * pad
    return data

# 加密过程
def enc_params(data, key):
    # 创建加密器
    aes = AES.new(key.encode("utf-8"), AES.MODE_CBC, IV="0102030405060708".encode("utf-8"))
    bs = aes.encrypt(to_16(data).encode("utf-8")) # 加密，加密内容的长度必须是 16 的倍数，不够的要补
    return str(b64encode(bs), "utf-8") # 转换成字符串返回
    
resp = requests.post(url, data={
    "params": get_params(json.dumps(data)),
    "encSecKey": encSecKey
})

print(resp.text)


# 处理加密过程
"""
    function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)
            e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
        return c
    }
    function b(a, b) {
        var c = CryptoJS.enc.Utf8.parse(b)
          , d = CryptoJS.enc.Utf8.parse("0102030405060708")
          , e = CryptoJS.enc.Utf8.parse(a)
          , f = CryptoJS.AES.encrypt(e, c, { # e:数据, c:密钥, d:偏移量, mode:加密模式
            iv: d,
            mode: CryptoJS.mode.CBC
        });
        return f.toString()
    }
    function c(a, b, c) {
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) { # d:data, e:010001, f:00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7, g:0CoJUm6Qyw8W8jud
        var h = {}
          , i = a(16);
        return h.encText = b(d, g),
        h.encText = b(h.encText, i),
        h.encSecKey = c(i, e, f),
        h
    }
"""
