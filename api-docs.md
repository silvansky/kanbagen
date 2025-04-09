# API документация

## Вступление

Fusion Brain API - это новый раздел платформы, который позволяет пользователям платформы получить доступ к моделям искусственного интеллекта по API. Одной из первых моделей, которая доступна по API, стала модель Kandinsky.

Kandinsky - это модель искусственного интеллекта, которая может создавать реалистичные изображения и произведения искусства на основе описания на естественном языке.

В настоящее время по API доступна версия Kandinsky 3.1 с более реалистичными, точными изображениями.

В настоящий момент данный раздел функционирует в beta.

## Возможности и ограничения использования API

Давайте рассмотрим подробнее технические характеристики модели и примеры запросов к каждому из параметров. А если хотите поскорее приступить к действиям - двигайтесь ниже.

### Режимы работы модели

В настоящее время Kandinsky доступен по API в одном режиме по работе с изображениями:

- режим генерация `generate`: создание изображений с нуля на основе текстового описания

Данный параметр указывается как:
```json
"type": "GENERATE",
```

### Размеры изображений

Сгенерированные изображения могут иметь размер до 1024 пикселей с каждой из сторон. Также в версии 3.1 поддерживается генерация изображения с разными соотношением сторон (самые оптимальные aspect ratio - 1:1 / 2:3 / 3:2 / 9:16 / 16:9).

Данные параметры указываются как (соотношение вам необходимо подобрать самостоятельно):
```json
"width": 1024,
"height": 1024,
```
Рекомендуем использовать значения кратные 64 с каждой из сторон для более качественных результатов.

### Количество изображений

Вы можете запросить только 1 изображение одновременно по одному и тому же запросу.
```json
"numImages": 1,
```

### Запрос

Вы и ваши пользователи можете составлять запросы на русском, английском или любом другом языке. Допускается также использование emoji в текстовом описании.

Максимальный размер текстового описания - 1000 символов.

Пример запроса:
```json
"query": "Пушистый кот в очках",
```

### Стиль

Вы и ваши пользователи могут также использовать несколько стилей из наших пресетов для генераций.
```json
"style": "ANIME",
```
Получение актуального списка стилей осуществляется по URL: [cdn.fusionbrain.ai/static/styles/key](http://cdn.fusionbrain.ai/static/styles/key)

### Негативный промпт

В поле Негативный промпт можно прописать, какие цвета и приёмы модель не должна использовать при генерации изображения.
```json
"negativePromptDecoder": "яркие цвета, кислотность, высокая контрастность",
```

### Пример передачи запроса:
```json
{
  "type": "GENERATE",
  "style": "string",
  "width": 1024,
  "height": 1024,
  "numImages": 1,
  "negativePromptDecoder": "яркие цвета, кислотность, высокая контрастность",
  "generateParams": {
    "query": "Пушистый кот в очках",
  }
}
```

### Результаты генерации

Вне зависимости от выбранного режима результатом работы модели является изображение. Каждое изображение может быть возвращено в виде данных Base64, используя параметр files.
```json
"files": ["string"]
```

### Модерация контента

Запросы на генерацию и изображения проходят соответствующие фильтры цензуры в соответствии с нашей политикой в отношении контента, возвращая ошибку, когда запрос или изображение не соответствует. Пример отработки данного параметра:
```json
"censored": true
```

Если у вас есть какие-либо примеры ложных срабатываний или связанных с ними проблемах, пожалуйста, свяжитесь с нами через почту обратной связи по адресу [hello@fusionbrain.ai](mailto:hello@fusionbrain.ai).

## Описание запросов

### Аутентификация API ключа

Первым шагом после получения ключа вам необходимо провести его аутентификацию.

API ключ и Secret необходимо передавать при любом обращении в сервис.

Для передачи используются заголовки HTTP запроса: `X-Key` и `X-Secret`, префиксы `Key`, `Secret` соответственно. Подготовим все необходимые значения:
```python
def __init__(self, url, api_key, secret_key):
    self.URL = url
    self.AUTH_HEADERS = {
        'X-Key': f'Key {api_key}',
        'X-Secret': f'Secret {secret_key}',
    }
```

Далее вам необходимо будет обратиться к списку доступных моделей и выбрать Kandinsky 3.1 (в настоящий момент это единственная модель, доступная для подключения по API). Обращение происходит по URL: [https://api-key.fusionbrain.ai/](https://api-key.fusionbrain.ai/).

Для этого совершите следующий запрос:
```python
def get_pipeline(self):
    response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
    data = response.json()
    return data[0]['id']
```

Структура ответа:
```json
[
  {
    "uuid": "ХХХХ-ХХХХ-ХХХХХХ",
    "name": "Kandinsky",
    "nameEn": "Kandinsky",
    "description": "",
    "descriptionEn": "",
    "tags": [],
    "version": 3.1,
    "imagePreview": null,
    "status": "ACTIVE",
    "type": "TEXT2IMAGE",
    "createdDate": "2025-ХХ-ХХTХХ:ХХ:ХХ",
    "lastModified": "2025-ХХ-ХХTХХ:ХХ:ХХ"
  }
]
```

Напомним, что API Kandinsky поддерживает один режим работы модели: generate. 

### Запрос к модели (на примере режима generate)

Метод `generate` принимает текстовое описание изображения в качестве входных данных и генерирует соответствующее ему изображение. Для вызова этого метода необходимо отправить POST запрос на URL `/key/api/v1/pipeline/run`.

Запрос должен содержать следующие параметры:

- `query`: текстовое описание изображения
- `height width`: размеры выходного изображения
- `numImages`: количество изображений по данному запросу

Прочие параметры мы рекомендуем оставить в дефолтных состояниях из примера ниже, так как они дают оптимальный результат генерации.

Пример запроса:
```python
def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
    params = {
        "type": "GENERATE",
        "numImages": images,
        "width": width,
        "height": height,
        "generateParams": {
            "query": "{prompt}"
        }
    }
    data = {
        'pipeline_id': (None, pipeline),
        'params': (None, json.dumps(params), 'application/json')
    }
    response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
    data = response.json()
    return data['uuid']
```

Структура ответа:
```json
{
    "uuid": "string",
    "status": "INITIAL"
}
```

### Доступность сервиса

При большой нагрузке или технических работах сервис может быть временно недоступен для приема новых задач. Можно заранее проверить текущее состояние с помощью GET запроса на URL `/key/api/v1/pipeline/{pipeline_id}/availability`. Во время недоступности задачи не будут приниматься и в ответе на запрос к модели вместо uuid вашего задания будет возвращен текущий статус работы сервиса.

Пример:
```json
{
  "pipeline_status": "DISABLED_BY_QUEUE"
}
```

### Запросы для проверки статуса check_status

Метод `check_status` позволяет проверить статус генерации изображения. Для вызова этого метода необходимо отправить GET запрос на URL `/key/api/v1/pipeline/status/{uuid}`, где `uuid` - идентификатор задания, полученный при вызове запроса к модели.

Пример запроса:
```python
def check_generation(self, request_id, attempts=10, delay=10):
    while attempts > 0:
        response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
        data = response.json()
        if data['status'] == 'DONE':
            return data['result']['files']
        attempts -= 1
        time.sleep(delay)
```

Ответ содержит текущий статус задания:
```json
{
  "uuid": "string",
  "status": "string",
  "errorDescription": "string",
  "result": {
    "files": ["string"],
    "censored": false
  }
}
```

Важно отметить, что получение картинки осуществляется только один раз, повторно запросить нельзя.

#### Возможные значения поля status:

- `INITIAL` - запрос получен, находится в очереди на обработку
- `PROCESSING` - запрос находится в процессе обработки
- `DONE` - задание выполнено
- `FAIL` - задание не удалось выполнить.

### Обработка ошибок

API может вернуть следующие ошибки:

- 401 Unauthorized - ошибка авторизации
- 404 Not found - ресурс не найден
- 400 Bad Request - неверные параметры запроса или текстовое описание слишком длинное
- 500 Internal Server Error - ошибка сервера при выполнении запроса
- 415 Unsupported Media Type - формат содержимого не поддерживается сервером

При возникновении 415 ошибки рекомендуем воспользоваться данным скриптом, который необходимо отправить в postman.

```bash
curl --location --request POST 'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run' \
--header 'X-Key: Key YOUR_KEY' \
--header 'X-Secret: Secret YOUR_SECRET' \
-F 'params="{
  \"type\": \"GENERATE\",
  \"generateParams\": {
    \"query\": \"море\"
  }
}";type=application/json' \
--form 'pipeline_id="uuid"'
```
Не забудьте указать именно ваш `YOUR_KEY` и `YOUR_SECRET`.

## Примеры использования

### Python

Пример использования API в Python:
```python
import json
import time
import requests

class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": "{prompt}"
            }
        }
        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']
            attempts -= 1
            time.sleep(delay)

if __name__ == '__main__':
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', 'YOUR_API_KEY', 'YOUR_SECRET_KEY')
    pipeline_id = api.get_pipeline()
    uuid = api.generate("Sun in sky", pipeline_id)
    files = api.check_generation(uuid)
    print(files)
```
Не забудьте указать именно ваш `YOUR_KEY` и `YOUR_SECRET`.

