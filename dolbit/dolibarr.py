import requests


class Dolibarr:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_headers(self):
        return {
            'DOLAPIKEY': self.token,
            'Content-Type': 'application/json'
        }

    def _call(self, method, route, **kwargs):
        headers = self.get_headers()
        kwargs.update(headers=headers)
        response = requests.request(method, f'{self.url}{route}', **kwargs)
        response.raise_for_status()
        try:
            return response.json()
        except:
            return response.text

    def get(self, route, params={}):
        return self._call('GET', route, params=params)

    def post(self, route, data={}, params={}):
        return self._call('POST', route, json=data, params=params)

    def put(self, route, data={}, params={}):
        return self._call('PUT', route, json=data, params=params)

    def delete(self, route):
        return self._call('DELETE', route)
