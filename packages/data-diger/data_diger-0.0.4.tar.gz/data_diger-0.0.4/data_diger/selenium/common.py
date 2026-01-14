import io
import re
import json
import base64
import zipfile

from selenium_stealth import stealth


def get_extension(manifest_json, background_js):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    zip_buffer.seek(0)
    encoded_extension = base64.b64encode(zip_buffer.read()).decode('utf-8')
    return encoded_extension


def auth_http_proxy(host, port, user, password):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (host, port, user, password)

    return get_extension(manifest_json, background_js)


def find_requests_and_responses(logs, search_pattern):
    """
    Функция для поиска всех запросов и их ответов в логах по заданному регулярному выражению.

    :param logs: Список логов, полученных из браузера
    :param search_pattern: Регулярное выражение для поиска в логах
    :return: Список словарей с данными запросов и ответов
    """
    results = []
    request_id_map = {}  # Для хранения найденных requestId и их запросов

    # Компиляция регулярного выражения
    pattern = re.compile(search_pattern)

    # Поиск запросов
    for log in logs:
        log_message = json.loads(log['message'])
        message = log_message['message']

        if message['method'] == 'Network.requestWillBeSent':
            request = message['params']['request']
            url = request['url']
            if pattern.search(url):
                request_id = message['params']['requestId']
                request_id_map[request_id] = request

    # Поиск ответов на запросы
    for log in logs:
        log_message = json.loads(log['message'])
        message = log_message['message']

        if message['method'] == 'Network.responseReceived':
            request_id = message['params']['requestId']
            if request_id in request_id_map:
                response = message['params']['response']
                request = request_id_map[request_id]
                results.append({
                    'request': request,
                    'response': response
                })

    return results


def chrome_stealth(driver, config: dict = None):
    cn = config or dict(
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    stealth(driver, **cn)
