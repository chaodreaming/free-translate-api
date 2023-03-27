import requests
import json
import time
textlists=["This is a very good project","So do I"]
params={"textlists":textlists}
t1=time.time()
url="http://127.0.0.1:6006/predict"
res=requests.post(url, data=json.dumps(params))
res.encoding = 'utf-8'
res = res.content.decode('unicode-escape')
print(textlists)
print(res)
print("耗时{:.2f}s,翻译了{}字符".format(time.time()-t1,len("".join(textlists))))
