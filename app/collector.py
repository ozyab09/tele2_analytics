import prometheus_client as prom
import random
import time
import requests
import json

req_summary = prom.Summary('python_my_req_example', 'Time spent processing a request')
data_types = ['data', 'sms', 'voice']
BASE_URL = 'https://msk.tele2.ru/api/exchange/lots/stats/volumes?trafficType='

@req_summary.time()
def process_request(t):
   time.sleep(t)


if __name__ == '__main__':

    gauge = prom.Gauge('tele2_lots', 'Count of lots for sale', ["volume", "metric", "data_type"])
    prom.start_http_server(8080)

    while True:
        for data_type in data_types:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
            r = requests.get(f'{BASE_URL}{data_type}', headers=headers)

            data = json.loads(r.text).get('data', [])

            for d in data:
                gauge.labels(volume=int(d.get('volume', 0)), metric='count', data_type=data_type).set(d.get('count', 0))
                gauge.labels(volume=int(d.get('volume', 0)), metric='avg_cost', data_type=data_type).set(d.get('avgCost', 0))

        # process_request(random.random() * 5)

        time.sleep(60)
