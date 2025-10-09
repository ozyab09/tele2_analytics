import os
import time
import logging
import requests
from typing import List, Dict, Optional

import prometheus_client as prom


# === Конфигурация ===
BASE_URL = os.getenv('TELE2_API_URL', 'https://msk.tele2.ru/api/exchange/lots/stats/volumes?trafficType=')
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '8080'))
USER_AGENT = os.getenv(
    'USER_AGENT',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
)
DATA_TYPES = ['data', 'sms', 'voice']
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

# === Логирование ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Метрики ===
req_summary = prom.Summary('python_my_req_example', 'Time spent processing a request')

gauge = prom.Gauge(
    'tele2_lots',
    'Count of lots for sale',
    labelnames=["volume", "metric", "data_type"]
)


def fetch_data(data_type: str) -> Optional[List[Dict]]:
    """
    Выполняет HTTP GET-запрос к Tele2 API и возвращает данные.

    Returns:
        List[Dict]: Список словарей с данными о лотах.
    """
    url = f"{BASE_URL}{data_type}"
    headers = {"User-Agent": USER_AGENT}

    try:
        with req_summary.time():
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к {url}: {e}")
        return None

    try:
        data = response.json().get('data', [])
        if not isinstance(data, list):
            logger.warning(f"Ожидался список, получено: {type(data)}")
            return None
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON из ответа: {e}")
        return None


def update_metrics(data_type: str, data: List[Dict]) -> None:
    """
    Обновляет метрики Prometheus на основе полученных данных.
    """
    for item in data:
        volume = int(item.get('volume', 0))
        count = item.get('count', 0)
        avg_cost = item.get('avgCost', 0)

        gauge.labels(volume=volume, metric='count', data_type=data_type).set(count)
        gauge.labels(volume=volume, metric='avg_cost', data_type=data_type).set(avg_cost)


def main():
    """
    Основной цикл сбора данных и обновления метрик.
    """
    prom.start_http_server(PROMETHEUS_PORT)
    logger.info(f"Prometheus сервер запущен на порту {PROMETHEUS_PORT}")

    while True:
        for data_type in DATA_TYPES:
            logger.info(f"Запрашиваю данные для типа '{data_type}'...")
            data = fetch_data(data_type)
            if data:
                update_metrics(data_type, data)
            else:
                logger.warning(f"Не удалось получить данные для типа '{data_type}'")

        logger.debug(f"Следующая проверка через {CHECK_INTERVAL} секунд")
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()