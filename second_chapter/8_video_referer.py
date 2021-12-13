import requests

url = "https://www.pearvideo.com/video_1747680"
contid = url.split("_")[1]
url_video_info = f"https://www.pearvideo.com/videoStatus.jsp?contId={contid}&mrd=0.030495253770733255"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
    # 防盗链，当前请求的上一级
    "Referer": url
}
resp = requests.get(url_video_info, headers=headers)
json_resp = resp.json()
video_url = json_resp["videoInfo"]["videos"]["srcUrl"]
systemTime = json_resp["systemTime"]
video_url = video_url.replace(systemTime, f"cont-{contid}")
# 下载视频
with open("test.mp4", "wb") as f:
    f.write(requests.get(video_url).content)