import random, time, uuid
from eth_account.messages import encode_defunct
from urllib.parse import urlparse, parse_qs
from web3.auto import w3

class Tomo():

    def __init__(self, voager, account, user_auth, proxy):

        self.v = voager
        self.account = account
        self.proxy = proxy
        self.user_auth = user_auth
        self.client_id = 'Vk13WDBPTmdJdURTS25YcUNUSDA6MTpjaQ'

    def get_twitter_headers_cookies(self, auth_token, need_auth=False, ct0=None):
        cookies = {
            'auth_token': auth_token,
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Opera";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }
        if need_auth:
            headers['authorization'] = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
        if ct0 is not None:
            cookies['ct0'] = ct0
            headers['x-csrf-token'] = ct0
        return cookies, headers

    def get_auth_code(self, auth_token, ct0):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=True, ct0=ct0)
                auth_code = self.v.helper.fetch_url(url='https://twitter.com/i/api/2/oauth2/authorize?code_challenge=challenge&code_challenge_method=plain&client_id=Vk13WDBPTmdJdURTS25YcUNUSDA6MTpjaQ&redirect_uri=tomo%3A%2F%2F&response_type=code&scope=tweet.read%20users.read&state=tomo_x_twitter', cookies=cookies, headers=headers, type='get', proxies=self.proxy)
                return auth_code['auth_code']
            except:
                pass
        return None

    def get_ct0(self, auth_token):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=False)
                cock = self.v.helper.fetch_url(url='https://twitter.com/i/flow/login', cookies=cookies, headers=headers, type='get', return_cookies=True, proxies=self.proxy)
                return cock['ct0']
            except:
                pass
        return None

    def make_approve(self, code, auth_token, ct0):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=True, ct0=ct0)
                payload = {
                    'approval': 'true',
                    'code': str(code),
                }
                approve = self.v.helper.fetch_url(url='https://twitter.com/i/api/2/oauth2/authorize', payload=payload, cookies=cookies, headers=headers, type='post', proxies=self.proxy)
                return approve['redirect_uri']
            except:
                pass
        return None

    def go_to_redirect(self, url):

        for i in range(3):
            try:
                headers = self.v.get_headers(self.user_auth)
                status = self.v.helper.fetch_url(url=url, headers=headers, type='get', proxies=self.proxy)
                return status
            except Exception:
                time.sleep(i+1)
        return None

    def get_client_id(self):
        uuid_part = uuid.uuid4()
        time_str = int(time.time() * 1000)
        combined_id = f"{uuid_part}{time_str}"
        return combined_id

    def make_callback_action(self, code):

        for i in range(3):
            try:
                headers = {
                    'user-agent': 'Dart/3.1 (dart:io)',
                    'content-type': 'application/json',
                    'accept-encoding': 'gzip'
                }
                payload = {"code":code,"clientId":self.get_client_id(),"platform":2}
                status = self.v.helper.fetch_url(url='https://apps-prod.unyx.tech/api/login/v2/twitter', payload=payload, headers=headers, type='post', proxies=self.proxy)
                if status['message'].lower() == 'Success'.lower():
                    return status['result']
                else:
                    raise Exception
            except Exception:
                time.sleep(i+1)
        return None

    def make_allow(self, callback):
        for i in range(3):
            try:
                headers = {
                    'clientid': 'BFgGXGggqneW4AieI1uBxROtxT5QdxtsnkVkloQBKw40YpbwFxmMG-jVwRROdJQH2oxEQwKmjhwnSR_d64CISog',
                    'verifierid': str(callback['imName']),
                    'user-agent': 'Mozilla/5.0 (Linux; Android 13; sdk_gphone_x86_64 Build/TE1A.220922.028; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36',
                    'verifier': 'tomo-verifier',
                    'x-api-key': 'torus-default',
                    'network': 'sapphire_mainnet',
                    'accept': '*/*',
                    'origin': 'http://localhost',
                    'x-requested-with': 'tomo.app.unyx',
                    'sec-fetch-site': 'cross-site',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': 'http://localhost/',
                    'accept-encoding': 'gzip, deflate',
                    'accept-language': 'en-US,en;q=0.9'
                }
                status = self.v.helper.fetch_url(url='https://signer.tor.us/api/allow', headers=headers, type='get', proxies=self.proxy)
                if status['success']:
                    return True
                else:
                    raise Exception
            except Exception:
                time.sleep(i+1)
        return None

    def make_set(self):
        for i in range(3):
            try:
                payload = {
                    "key": "04e046e4cf40186ae6079a176cdc30b68b6fe9e7bed57635f881f4bd916292ded1109e689fa93cc382da45f1817f1403ef761a575c2166534389cd917a0ee075e9",
                    "data": "{\"iv\":\"dedbb1f7038f617518f7bf15178b285e\",\"ephemPublicKey\":\"0409664310df0019da76cc171661261c3b8e463aa6c7bef7628db5b07493bed82c888fb1be7ba93ab4f67d50b4ff389224d50391dd9385465f22c25a3aeb7810cb\",\"ciphertext\":\"5d214158d2e8767fd226ddc69862e52380d605216ee110aef3f33772cc0e4bf0dfea4ed31d99348b8a65bee8300910319f8ea14aa9dec0160fc795a3d9aa0407422e63bcd1f02e2b6b4269d2dcb0b7ed\",\"mac\":\"2b5c2b84d9ded1d6d66b7358d7997dfb894709899d6f68b37117e7518a2564b1\"}",
                    "signature": "30450221008b06342443a4d35780a7e0cc1684bc449072d061d6e5b243b2c35f11764a215f02205bb413eb084dbc5e7360bb48fbfb6a23c077ed02e0c5d91038a0ccb5b76b2408",
                    "timeout": 86400}
                status = self.v.helper.fetch_url(url='https://broadcast-server.tor.us/store/set', type='post', payload=payload, proxies=self.proxy)
                if status['success']:
                    return True
                else:
                    raise Exception
            except Exception:
                time.sleep(i + 1)
        return None

    def make_wallet(self, callback):
        for i in range(3):
            try:
                headers = {
                    'user-agent': 'Dart/3.1 (dart:io)',
                    'content-type': 'application/json',
                    'accept-encoding': 'gzip',
                    'content-length': '273',
                    'authorization': f'Bearer {callback["token"]}',
                    'host': 'apps-prod.unyx.tech'
                }
                payload = {"walletAddress": w3.eth.account.create().address, "eoaAddress": w3.eth.account.create().address, "authType": "WEB3AUTH","factoryAddress": "0x3fbe35a874284e41c955331a363c1ea085301a8d","implementationAddress": "0x185dd8cf226f535b9B766d9999A1c9c10888e56c"}
                status = self.v.helper.fetch_url(url='https://apps-prod.unyx.tech/api/user/walletAddress', type='post',payload=payload, headers=headers, proxies=self.proxy)

                if status['result']:
                    return True
                else:
                    raise Exception
            except Exception:
                time.sleep(i + 1)
        return None

    def start_bound(self, auth_token, attempt=0):

        if attempt>1:
            return

        ct0 = self.get_ct0(auth_token)
        if not ct0:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        auth_code = self.get_auth_code(auth_token, ct0)
        if not auth_code:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        approve = self.make_approve(auth_code, auth_token, ct0)
        if not approve:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        callback = self.make_callback_action(auth_code)
        if not callback:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        allow = self.make_allow(callback)
        if not allow:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        set = self.make_set()
        if not set:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)

        wallet = self.make_wallet(callback)
        if not wallet:
            return self.start_bound(auth_token=auth_token, attempt=attempt + 1)
        return True


class Twitter():

    def __init__(self, voager, account, user_auth, proxy):

        self.v = voager
        self.account = account
        self.proxy = proxy
        self.user_auth = user_auth

    def get_twitter_headers_cookies(self, auth_token, need_auth=False, ct0=None):
        cookies = {
            'auth_token': auth_token,
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Opera";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }
        if need_auth:
            headers['authorization'] = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
        if ct0 is not None:
            cookies['ct0'] = ct0
            headers['x-csrf-token'] = ct0
        return cookies, headers

    def get_real_twitter_url(self, url, auth_token):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=False)
                real_url = self.v.helper.fetch_url(url=url, cookies=cookies, headers=headers, type='get', return_url=True, proxies=self.proxy)
                return real_url
            except:
                pass
        return None

    def get_ct0(self, auth_token):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=False)
                cock = self.v.helper.fetch_url(url='https://twitter.com/i/flow/login', cookies=cookies, headers=headers, type='get', return_cookies=True, proxies=self.proxy)
                return cock['ct0']
            except:
                pass
        return None

    def get_params(self, url):
        parsed_url = urlparse(url)
        params_parsed = parse_qs(parsed_url.query)
        params = {
            'code_challenge': params_parsed['code_challenge'][0],
            'code_challenge_method': params_parsed['code_challenge_method'][0],
            'client_id': params_parsed['client_id'][0],
            'redirect_uri': params_parsed['redirect_uri'][0],
            'response_type': params_parsed['response_type'][0],
            'scope': params_parsed['scope'][0],
            'state': params_parsed['state'][0],
        }
        return params

    def get_auth_code(self, url, auth_token, ct0):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=True, ct0=ct0)
                auth_code = self.v.helper.fetch_url(url='https://twitter.com/i/api/2/oauth2/authorize', cookies=cookies, headers=headers, params=self.get_params(url), type='get', proxies=self.proxy)
                return auth_code['auth_code']
            except:
                pass
        return None

    def make_approve(self, code, auth_token, ct0):

        for i in range(3):
            try:
                cookies, headers = self.get_twitter_headers_cookies(auth_token=auth_token, need_auth=True, ct0=ct0)
                payload = {
                    'approval': 'true',
                    'code': str(code),
                }
                approve = self.v.helper.fetch_url(url='https://twitter.com/i/api/2/oauth2/authorize', payload=payload, cookies=cookies, headers=headers, type='post', proxies=self.proxy)
                return approve['redirect_uri']
            except:
                pass
        return None

    def go_to_redirect(self, url):

        for i in range(3):
            try:
                headers = self.v.get_headers(self.user_auth)
                status = self.v.helper.fetch_url(url=url, headers=headers, type='get', proxies=self.proxy)
                return status
            except Exception:
                time.sleep(i+1)
        return None

    def check_poll(self, poll_id):

        for i in range(3):
            try:
                headers = self.v.get_headers(self.user_auth)
                payload = {"pollId": str(poll_id)}
                status = self.v.helper.fetch_url(url='https://api.intract.io/api/qv1/auth/oauth/poll', payload=payload, headers=headers, type='post', proxies=self.proxy)
                #print(status)
                if status['status'] == 'SUCCESS':
                    return status
                else:
                    raise Exception
            except Exception:
                time.sleep(i+1)
        return None

    def make_callback_action(self, check_poll):

        for i in range(3):
            try:
                headers = {
                    'Authorization': f"Bearer {self.user_auth}"
                }
                payload = {"code":check_poll['code'],"source":"TWITTER","state":str(check_poll['state']),"referralCode":None,"referralLink":None,"referralSource":None}
                status = self.v.helper.fetch_url(url='https://api.intract.io/api/qv1/auth/oauth/callback', payload=payload, headers=headers, type='post', proxies=self.proxy)
                if status['isTwitterLoggedIn']:
                    return True
                else:
                    raise Exception
            except Exception:
                time.sleep(i+1)
        return None

    def start_bound(self, auth_token, poll_id=None, attempt=0):

        if attempt>1:
            return

        if poll_id is None: #НАХУЙ НАДО
            poll_id = uuid.uuid4()

        twitter_bound_url = f"https://api.intract.io/api/qv1/auth/oauth?pollId={poll_id}&source=TWITTER&isTaskLogin=true"

        real_url = self.get_real_twitter_url(twitter_bound_url, auth_token)
        if not real_url:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt+1)

        ct0 = self.get_ct0(auth_token)
        if not ct0:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt+1)

        auth_code = self.get_auth_code(real_url, auth_token, ct0)
        if not auth_code:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt+1)

        approve = self.make_approve(auth_code, auth_token, ct0)
        if not approve:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt + 1)

        go_to_redirect = self.go_to_redirect(approve)
        if not go_to_redirect:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt + 1)

        check_poll = self.check_poll(poll_id)
        if not check_poll:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt + 1)

        callback = self.make_callback_action(check_poll)
        if not callback:
            return self.start_bound(auth_token=auth_token, poll_id=poll_id, attempt=attempt + 1)
        return True


class Voyager():

    def __init__(self, settings, logger, helper, w3):

        self.project = 'VOYAGER'
        self.settings = settings
        self.logger = logger
        self.helper = helper
        self.w3 = w3
        self.quests_xp_cap = {
            '654a0e8e95c012164b1f1683': 40,
            '654a0e8d95c012164b1f1620': 150,
            '65535ae63cd33ebafe9d68f8': 270,
            '655b48ec2e9188e21c94e93e': 370,
            '65647f06731b793354cb239c': 310,
            '656db678132add9470b7595c': 350,
            '65705a282a20cd7291eb8e4b': 1,
            '6572fc0bef415b56fd67608f': 300,
            '65798e5c7d62adc325a44d92': 250,
        }
        self.quests_to_week = {
            "654a0e8e95c012164b1f1683": "week_0",
            "654a0e8d95c012164b1f1620": "week_1",
            "65535ae63cd33ebafe9d68f8": "week_2",
            "655b48ec2e9188e21c94e93e": "week_3",
            "65647f06731b793354cb239c": "week_4",
            "656db678132add9470b7595c": "week_5",
            "65705a282a20cd7291eb8e4b": 'week_6',
            "6572fc0bef415b56fd67608f": "week_7",
            "65798e5c7d62adc325a44d92": "week_8"
        }

    def get_headers(self, auth=None, user=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/json',
            'Origin': 'https://www.intract.io',
            'Connection': 'keep-alive',
            'Referer': 'https://www.intract.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        if auth:
            headers['Authorization'] = f"Bearer {auth}"
        if user:
            headers['questUserId'] = user
        return headers

    def get_auth(self, account, new_w3, proxy, auth_data=None):
        for i in range(3):
            try:
                payload = {"walletAddress": account.address}
                auth_data = self.helper.fetch_url(url='https://api.intract.io/api/qv1/auth/generate-nonce', type='post', payload=payload, headers=self.get_headers(), proxies=proxy)
                if auth_data['success']:
                    break
            except:
                time.sleep(1)
        if not auth_data:
            return

        message_ = f"{auth_data['message']}. Nonce: {auth_data['data']['nonce']}"
        message = message_.encode()
        message_to_sign = encode_defunct(primitive=message)
        signed_message = new_w3.eth.account.sign_message(message_to_sign, private_key=account.key.hex())
        sig = signed_message.signature.hex()
        payload = {
            'signature': sig,
            'userAddress': account.address,
            'chain': {
                'id': 59144,
                'name': 'Linea',
                'network': 'Linea',
                'nativeCurrency': {
                    'decimals': 18,
                    'name': 'Ether',
                    'symbol': 'ETH',
                },
                'rpcUrls': {
                    'public': {
                        'http': [
                            'https://linea.drpc.org',
                        ],
                    },
                    'default': {
                        'http': [
                            'https://linea.drpc.org',
                        ],
                    },
                },
                'blockExplorers': {
                    'etherscan': {
                        'name': 'Lineascan',
                        'url': 'https://lineascan.build/',
                    },
                    'default': {
                        'name': 'Lineascan',
                        'url': 'https://lineascan.build/',
                    },
                },
                'unsupported': False,
            },
            'isTaskLogin': False,
            'width': '590px',
            'reAuth': False,
            'connector': 'metamask',
            'referralCode': None,
            'referralLink': None,
            'referralSource': None,
        }
        resp_headers = None
        for i in range(3):
            try:
                resp_headers = self.helper.fetch_url(url='https://api.intract.io/api/qv1/auth/wallet', type='post', payload=payload, headers=self.get_headers(), resp_headers=True)
                return resp_headers['Authorization']
            except:
                time.sleep(1)
        if not resp_headers:
            return

    def set_wallet(self, auth, user_id, account, proxy):
        for i in range(3):
            try:
                payload = {"userId":user_id,"lineaWalletAddress":account.address}
                streak = self.helper.fetch_url(url='https://api.intract.io/api/qv1/linea/user/set-wallet', type='post', payload=payload, headers=self.get_headers(auth=auth, user=user_id), proxies=proxy)
                if streak.get('message', 'none').lower() == 'Linea wallet address updated successfully'.lower():
                    return True
            except:
                time.sleep(1)
        return None

    def fetch_campaign(self, auth, user_id, campaign, proxy):
        for i in range(3):
            try:
                campaign_info = self.helper.fetch_url(url=f'https://api.intract.io/api/qv1/journey/fetch?campaignId={campaign}&channelCode=DEFAULT&referralCode=null', type='get', headers=self.get_headers(auth=auth, user=user_id), proxies=proxy)
                if campaign_info['_id']:
                    return campaign_info
            except:
                time.sleep(1)
        return None

    def get_tasks(self, auth, user_id, campaign, proxy):
        for i in range(3):
            try:
                campaign_info = self.helper.fetch_url( url=f'https://api.intract.io/api/qv1/campaign/{campaign}', type='get', headers=self.get_headers(auth=auth, user=user_id), proxies=proxy)
                if campaign_info['_id']:
                    return campaign_info
            except:
                time.sleep(1)
        return None

    def get_user_info(self, auth):

        for i in range(3):
            try:
                info = self.helper.fetch_url(url='https://api.intract.io/api/qv1/auth/get-super-user', type='get', headers=self.get_headers(auth=auth))
                if info['_id']:
                    return info
            except:
                time.sleep(1)
        return None

    def get_user_info_by_campaign(self, auth, proxy, project='6549ed0333cc8772783b858b'):
        for i in range(3):
            try:
                info = self.helper.fetch_url(url=f'https://api.intract.io/api/qv1/auth/get-user?projectId={project}', type='get', headers=self.get_headers(auth=auth), proxies=proxy)
                if info['_id']:
                    return info
            except:
                time.sleep(1)
        return None

    def linea_streak(self, auth, user_id, proxy):
        for i in range(3):
            try:
                payload = {}
                streak = self.helper.fetch_url(url='https://api.intract.io/api/qv1/linea/user/streak', type='post', payload=payload, headers=self.get_headers(auth=auth, user=user_id), proxies=proxy)
                if streak.get('message', 'none').lower() == 'Linea streak already done for today'.lower():
                    return False
                if streak:
                    return True
            except:
                time.sleep(1)
        return None

    def verify_task(self, auth, user_id, task, account, proxy):
        for i in range(3):
            try:
                payload = {
                    'campaignId': self.settings['quest_id'],
                    'userInputs': {
                        'TRANSACTION_HASH': '0x',
                    },
                    'task': task,
                    'verificationObject': {
                        'questerWalletAddress': account.address.lower(),
                    },
                }

                ### WAWE 5 START ###

                if task["_id"] in ['656db678132add9470b7595d', '656db678132add9470b75961', '656db678132add9470b75965']:
                    PROJECT_TO_SUBMIT = '65647a184b53507f1de4ea8c' # СЕЙЧАС СТОИТ VELOCORE
                    payload['userInputs']['lineaProjectId'] = PROJECT_TO_SUBMIT
                    payload['verificationObject']['lineaProjectId'] = PROJECT_TO_SUBMIT

                if task['_id'] == '656db678132add9470b75969': #SINGLE LIQ | НЕ МЕНЯТЬ
                    xy_id = '65659f81646593f64862d08c'
                    payload['userInputs']['lineaProjectId'] = xy_id
                    payload['verificationObject']['lineaProjectId'] = xy_id

                ### WAWE 5 END ###

                ### WAWE 7 START ###

                if task["_id"] in ['6572fc0bef415b56fd676090']: #CORE TASK
                    PROJECT_TO_SUBMIT = '657186570d75b1844e3cfdf9'  # СЕЙЧАС СТОИТ ZKEX
                    payload['userInputs']['lineaProjectId'] = PROJECT_TO_SUBMIT
                    payload['verificationObject']['lineaProjectId'] = PROJECT_TO_SUBMIT

                if task["_id"] in ['6572fc0bef415b56fd676095']: #BONUS TASK
                    PROJECT_TO_SUBMIT = '65707fad21ef6dcd741b8a18'  # СЕЙЧАС СТОИТ AIRSWAP
                    payload['userInputs']['lineaProjectId'] = PROJECT_TO_SUBMIT
                    payload['verificationObject']['lineaProjectId'] = PROJECT_TO_SUBMIT

                ### WAWE 7 END ###

                verify = self.helper.fetch_url(url='https://api.intract.io/api/qv1/task/verify', type='post', payload=payload, headers=self.get_headers(auth=auth, user=user_id), timeout=10, retries=1, proxies=proxy)
                if verify is True:
                    return True
                if verify['message'].lower() == 'Task already submitted for verification!'.lower():
                    return 'already'
                if verify['message'].lower() == 'Task already completed'.lower():
                    return 'completed'
            except Exception:
                time.sleep(1)
        return None

    def claim_xp(self, auth, user_id, task, proxy):
        for i in range(3):
            try:
                payload = {"taskId": task}
                claim = self.helper.fetch_url(url=f'https://api.intract.io/api/qv1/campaign/{self.settings["quest_id"]}/claim-task-xp', type='post', payload=payload, headers=self.get_headers(auth=auth, user=user_id), timeout=5, retries=1, proxies=proxy)
                if claim.get('claimDetails'):
                    return True
            except:
                time.sleep(1)
        return None

    def format_results(self, data, account):
        quests_data = []
        try:
            for _id, task_data in data['campaignMetrics'].items():
                if _id == '65705a282a20cd7291eb8e4b':
                    xp = '✅' if task_data['questJourneyStatus'] == 'COMPLETED' else '❌'
                    quests_data.append({'week': self.quests_to_week[_id], 'xp': xp,'full': True})
                else:
                    quests_data.append({'week': self.quests_to_week[_id], 'xp': int(task_data['xp']), 'full': True if self.quests_xp_cap[_id] == int(task_data['xp']) else False})
        except:
            pass
        try:
            streak = int(data['lineaStreak']['streakCount'])
        except:
            streak = 0
        return {"streak": streak, 'total_xp': int(data['totalXp']), "quests_data": quests_data, "wallet": account.address}

    def main(self, private_key, attempt=0):

        if attempt != 0:
            time.sleep(1)
        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None) and self.settings['use_proxy']:
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3
        proxy = private_key.get('proxy', None)
        if not self.settings['use_proxy']:
            proxy = None

        twitter_auth_token = private_key.get('twitter_auth_token', None)
        account = new_w3.eth.account.from_key(private_key['private_key'])

        auth = self.get_auth(account, new_w3, proxy)
        if not auth:
            return self.main(private_key=private_key, attempt=attempt+1)

        user_campaign_info = self.get_user_info_by_campaign(auth, proxy)
        if not user_campaign_info:
            return self.main(private_key=private_key, attempt=attempt + 1)

        user_id = user_campaign_info['_id']

        if user_campaign_info.get('lineaWalletAddress', 'none').lower() != account.address.lower():
            wallet_setup = self.set_wallet(auth, user_id, account, proxy)
            if not wallet_setup:
                return self.main(private_key=private_key, attempt=attempt + 1)

        time.sleep(random.uniform(self.settings['min_delay'], self.settings['max_delay']))

        if self.settings['mode'] == 0:

            try:
                current_streak = int(user_campaign_info['lineaStreak']['streakCount'])
            except:
                current_streak = 0

            streak = self.linea_streak(auth, user_id, proxy)
            if streak:
                self.logger.log_success(f"{self.project} | Успешно сделал GM стрик (текущий стрик {current_streak + 1})", wallet=account.address)
            else:
                self.logger.log_warning(f"{self.project} | Сегодня уже сделан GM (текущий стрик {current_streak + 1})!", wallet=account.address)
            return self.format_results(user_campaign_info, account)

        else:
            if self.settings['mode'] == 3:
                self.settings['quest_id'] = '654a0e8e95c012164b1f1683'
            quest_info = self.fetch_campaign(auth, user_id, self.settings['quest_id'], proxy)
            if not quest_info:
                return self.main(private_key=private_key, attempt=attempt + 1)
            quest_cap = self.quests_xp_cap.get(f"{self.settings['quest_id']}", 1000)
            if int(quest_info['xp']) == quest_cap:
                self.logger.log_success(f"{self.project} | Квест уже выполнен полностью!", wallet=account.address)
                return self.format_results(user_campaign_info, account)

            tasks_info = self.get_tasks(auth, user_id, self.settings['quest_id'], proxy)
            if not tasks_info:
                return self.main(private_key=private_key, attempt=attempt + 1)
            if self.settings['mode'] == 1:

                for sub_task in tasks_info['quest']['tasks']:
                    try:
                        task_name = sub_task['userInputs']['initiateButton']['label']
                    except:
                        task_name = sub_task['_id']
                    verify = self.verify_task(auth, user_id, sub_task, account, proxy)
                    if not verify:
                        self.logger.log_warning( f"{self.project} | Не смог сделал verify в квесте '{task_name}'", wallet=account.address)
                    if verify == 'completed':
                        self.logger.log_success(f"{self.project} | Квест уже выполнен '{task_name}'", wallet=account.address)
                    if verify == 'already':
                        self.logger.log_success( f"{self.project} | Уже сделал verify для квеста '{task_name}'", wallet=account.address)
                    if verify is True:
                        self.logger.log_success(f"{self.project} | Успешно выполнил квест '{task_name}'", wallet=account.address)
                    time.sleep(random.uniform(self.settings['min_delay'], self.settings['max_delay']))

                return self.format_results(user_campaign_info, account)

            elif self.settings['mode'] == 2:

                for sub_task in tasks_info['quest']['tasks']:
                    try:
                        task_name = sub_task['userInputs']['initiateButton']['label']
                    except:
                        task_name = sub_task['_id']
                    claim = self.claim_xp(auth, user_id, sub_task['_id'], proxy)
                    if not claim:
                        self.logger.log_warning( f"{self.project} | Не смог сделал клейм в квесте '{task_name}'", wallet=account.address)
                    else:
                        self.logger.log_success( f"{self.project} | Успешно сделал клейм в квесте '{task_name}'", wallet=account.address)
                    time.sleep(random.uniform(self.settings['min_delay'], self.settings['max_delay']))

                return self.format_results(user_campaign_info, account)

            elif self.settings['mode'] == 3:

                super_user = self.get_user_info(auth)
                if not super_user:
                    return self.main(private_key=private_key, attempt=attempt + 1)
                if super_user['isTwitterLoggedIn']:
                    self.logger.log_success('Twitter уже привязан, пропускаю', account.address)
                else:
                    self.logger.log('Twitter не привязан, начинаю привязку...', account.address)
                    twitter = Twitter(self, account, auth, proxy)
                    if twitter_auth_token is None:
                        self.logger.log_error('Не указан AUTH TOKEN для Twitter, пропускаю!', account.address)
                        return self.format_results(user_campaign_info, account)
                    twi_bound = twitter.start_bound(twitter_auth_token)
                    if not twi_bound:
                        self.logger.log_error('Не смог привязать Twitter, пропускаю', account.address)
                        return self.format_results(user_campaign_info, account)
                    else:
                        self.logger.log_success('Успешно привязал Twitter!', account.address)
                for sub_task in tasks_info['quest']['tasks']:
                    try:
                        task_name = sub_task['userInputs']['initiateButton']['label']
                    except:
                        task_name = sub_task['_id']
                    verify = self.verify_task(auth, user_id, sub_task, account, proxy)
                    if not verify:
                        self.logger.log_warning(f"{self.project} | Не смог сделал verify в квесте '{task_name}'", wallet=account.address)
                    if verify == 'completed':
                        self.logger.log_success(f"{self.project} | Квест уже выполнен '{task_name}'", wallet=account.address)
                    if verify == 'already':
                        self.logger.log_success(f"{self.project} | Уже сделал verify для квеста '{task_name}'", wallet=account.address)
                    if verify is True:
                        self.logger.log_success(f"{self.project} | Успешно выполнил квест '{task_name}'", wallet=account.address)
                    time.sleep(random.uniform(self.settings['min_delay'], self.settings['max_delay']))

                return self.format_results(user_campaign_info, account)

            elif self.settings['mode'] == 4:

                super_user = self.get_user_info(auth)
                if not super_user:
                    return self.main(private_key=private_key, attempt=attempt + 1)
                if not super_user['isTwitterLoggedIn']:
                    self.logger.log_error('Twitter не привязан к Intract! Сначала привяжи Twitter через "mode" 0', account.address)
                    return self.format_results(user_campaign_info, account)
                else:
                    self.logger.log('Twitter привязан, начинаю bound к Tomo...', account.address)
                    tomo = Tomo(self, account, auth, proxy)
                    if twitter_auth_token is None:
                        self.logger.log_error('Не указан AUTH TOKEN для Twitter, пропускаю!', account.address)
                        return self.format_results(user_campaign_info, account)
                    twi_bound = tomo.start_bound(twitter_auth_token)
                    if not twi_bound:
                        self.logger.log_error('Не смог привязать Twitter, пропускаю', account.address)
                        return self.format_results(user_campaign_info, account)
                    else:
                        self.logger.log_success('Успешно привязал Twitter!', account.address)

                return self.format_results(user_campaign_info, account)

            else:
                self.logger.log_error(f"{self.project} | Ошибка! Неверно указан 'mode'", wallet=account.address)
                return self.format_results(user_campaign_info, account)


