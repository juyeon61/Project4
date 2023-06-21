import psycopg2
import requests
from xml.etree import ElementTree
import json

# Database 연결
host = 'drona.db.elephantsql.com'
user = 'rzdqhkrx'
password = 'ZXxLzVgHRopX8mgUqreVyxsWCq04LYmD'
database = 'rzdqhkrx'

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# weather 테이블 생성
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS weather;")
cursor.execute("""CREATE TABLE weather(
                    Id SERIAL PRIMARY KEY,
                    month DATE,
                    stnko VARCHAR(12),
                    pa FLOAT,
                    avgtamax FLOAT,
                    avgtamin FLOAT,
                    taavg FLOAT,
                    avghm INTEGER,
                    sumssday FLOAT,
                    daydur INTEGER
                )""")

# electricity 테이블 생성

cursor.execute("DROP TABLE IF EXISTS electricity;")
cursor.execute("""CREATE TABLE electricity(
                    Id SERIAL PRIMARY KEY,
                    month DATE,
                    metro VARCHAR(12),
                    cntr VARCHAR(12),
                    custCnt INTEGER,
                    powerUsage BIGINT,
                    bill BIGINT,
                    unitCost FLOAT
                )""")
# INTEGER로 설정하면 NumericValueOutOfRange: integer out of range에러 발생하여 BIGINT로 교체

# 날씨 정보 API 데이터 읽어오기
skey = "ZuBqZjyJe/E7XpQz6gTx8hPJT3+BZX2AL5MgHPaZlC/aZsqAQC2ktJmQS0nbzjkjJ9iPav+4cmDMfWO4GnSBsQ=="

url = 'http://apis.data.go.kr/1360000/SfcMtlyInfoService/getMmSumry'
params ={'serviceKey' : skey,
         'pageNo' : '1',
         'numOfRows' : '10',
         'dataType' : 'xml',
         'year' : '2022',
         'month' : '01'}

years = ['2020', '2021', '2022']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

weather = []
for nyeon in years:
    for dal in months:
        params['year'] = nyeon
        params['month'] = dal

        response = requests.get(url, params=params)
        root =  ElementTree.fromstring(response.content)

        for item in root.iter('info'):
            if item.find('stnko').text == '세종':
                item_dict={}
                item_dict['month'] = f"{nyeon}-{dal}-01"
                item_dict['stnko'] = item.find('stnko').text # 지역명(국문)
                item_dict['pa'] = item.find('pa').text # 평균 현지기압(hPa)
                item_dict['avgtamax'] = item.find('avgtamax').text # 최고기온의 평균(℃)
                item_dict['avgtamin'] = item.find('avgtamin').text # 최저기온의 평균(℃) 
                item_dict['taavg'] = item.find('taavg').text # 평균 기온(℃)
                item_dict['avghm'] = item.find('avghm').text # 평균상대습도(%)
                item_dict['sumssday'] = item.find('sumssday').text # 일조 총 시간(hr)
                item_dict['daydur'] = item.find('daydur').text # 일조-일조율(%)
                weather.append(item_dict)
            else:
                pass

# 읽어온 데이터 저장
for values in weather:
    cursor.execute("""INSERT INTO weather (month, stnko, pa, avgtamax, avgtamin, taavg, avghm, sumssday, daydur)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    (values['month'], values['stnko'], values['pa'], values['avgtamax'], values['avgtamin'], values['taavg'], values['avghm'], values['sumssday'], values['daydur']))

connection.commit()


# 전기 사용량 API 읽어오기
skey = "9Rzc30R5q4bC5vUP252gc9Wci2pEb2RKE5d7uK2A"

url = 'https://bigdata.kepco.co.kr/openapi/v1/powerUsage/contractType.do'
params ={'year' : '2022',
         'month' : '04',
         'metroCd' : '41', ## 광역자치단체 코드, 미선택 시 모든 시도 응답
        #  'cityCd' : '60', ## 기초자치단체 코드, 미선택 시 모든 시군구 응답
        #  'cntrCd' : '100', ## 전기계약종별(ex:100-주택용, 200-일반용), 미선택 시 모든 계약종별 응답
         'apiKey' : skey,
         'returnType' : 'json'}

elec = []

years = ['2020', '2021', '2022']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
cntrs = ['100', '200', '250', '300', '500', '600', '900']
for nyeon in years:
    for dal in months:
        for cntr in cntrs:
            params['month'] = dal
            params['year'] = nyeon
            params['cntrCd'] = cntr
            response = requests.get(url, params=params)
            data_json = json.loads(response.text)
            for item in data_json['data']:
                item_dict={}
                item_dict['month'] = f"{item['year']}-{item['month']}-01"
                item_dict['metro'] = item['metro'][:2]
                item_dict['cntr'] = item['cntr']
                item_dict['custCnt'] = item['custCnt']
                item_dict['powerUsage'] = item['powerUsage']
                item_dict['bill'] = item['bill']
                item_dict['unitCost'] = item['unitCost']
            elec.append(item_dict)


# 읽어온 데이터 저장
for values in elec:
    cursor.execute("""INSERT INTO electricity (month, metro, cntr, custCnt, powerUsage, bill, unitCost)
    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
    (values['month'], values['metro'], values['cntr'], values['custCnt'], values['powerUsage'], values['bill'], values['unitCost']))

connection.commit()
cursor.close()
connection.close()