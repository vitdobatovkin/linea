import requests, time

class Helper():

    def fetch_url(self, url, type, payload=None, headers=None, params=None, data=None, cookies = None, proxies=None, content = False, text=False, return_cookies=False, return_url=False, resp_headers=False, timeout=60, retries = 15):
        if proxies:
            proxies = {"http": f"http://{proxies}", "https": f"http://{proxies}"}
        for i in range(retries):
            try:
                if type == "get":
                    response = requests.get(url, timeout=timeout, headers=headers, params=params, cookies=cookies, proxies=proxies)
                    #print(response.text)
                    if return_cookies:
                        return response.cookies
                    if return_url:
                        return response.url
                    if content:
                        return response.content
                    if text:
                        return response.text
                    if resp_headers:
                        return response.headers
                    return response.json()
                elif type == "post":
                    response = requests.post(url, timeout=timeout, json=payload, headers=headers, params=params, data=data, cookies=cookies, proxies=proxies)
                    #print(response.text)
                    if return_cookies:
                        return response.cookies
                    if return_url:
                        return response.url
                    if text:
                        return response.text
                    if resp_headers:
                        return response.headers
                    return response.json()
            except:
                time.sleep(i * 1)
        return

