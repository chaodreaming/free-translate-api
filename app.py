import time
from flask import Flask, request
import json
from untils import supertranslate
app = Flask(__name__)
trans=supertranslate(model_dir="models/damo/nlp_csanmt_translation_en2zh_base")

@app.route("/predict", methods=["POST"])
def predict():
    raw_data = request.data
    json_data = json.loads(raw_data.decode())
    print(json_data,flush=True)
    res=[]
    textlists=json_data['textlists']
    if type(textlists)==list:
        t1 = time.time()
        trans_result = trans.translate(textlists)
        print(time.time() - t1)
        print(trans_result,flush=True)
        res.append(trans_result)
    return json.dumps({'prediction': res})
if __name__ == '__main__':
    app.run(threaded=False,port=6006,debug=False)