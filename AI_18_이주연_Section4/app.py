from flask import Flask, request, render_template
from joblib import load
import pandas as pd
import json

app = Flask(__name__)

@app.route("/")
def index():
    val = request.form
    return render_template("index.html", result = val)

regr = load('./models/model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    # json 데이터를 받아 모델의 예측 input으로 넣어준다.
    # 예측 결과 리턴
    form_data = request.form
    data = form_data.to_dict()
    if data['month'] == '해당 월':
        return "해당 월을 선택해주세요."
    elif data['cntr'] == '전기계약종별':
        return "전기계약종별을 선택해주세요."
    elif data['custCnt'] == '':
        return "전기사용 고객 호수를 입력해주세요."
    elif data['pa'] == '':
        return "평균 현지기압(hPa)을 입력해주세요."
    elif data['avgtamax'] == '':
        return "최고기온의 평균(℃)을 입력해주세요."
    elif data['avgtamin'] == '':
        return "최저기온의 평균(℃)을 입력해주세요."
    elif data['taavg'] == '':
        return "평균 기온(℃)을 입력해주세요."
    elif data['avghm'] == '':
        return "평균상대습도(%)를 입력해주세요."
    elif data['sumssday'] == '':
        return "일조 총 시간(hr)을 입력해주세요."
    elif data['daydur'] == '':
        return "일조-일조율(%)을 입력해주세요."
    
    else:
        df = pd.DataFrame(data=[list(data.values())], columns=(list(data.keys())))
        prediction = int(regr.predict(df))

        return render_template("predict.html", predict = str(prediction)), 200

if __name__ == '__main__':
    app.run()