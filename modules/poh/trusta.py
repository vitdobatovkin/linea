from helpers.utils import *
from eth_account.messages import encode_defunct

class Trusta():

    def __init__(self, helper, logger, w3):

        self.w3 = w3
        self.logger = logger
        self.help = helper
        self.project = 'TRUSTA'

    def get_headers(self, auth=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/json',
            'Authorization': 'TOKEN null',
            'Origin': 'https://trustgo.trustalabs.ai',
            'Connection': 'keep-alive',
            'Referer': 'https://trustgo.trustalabs.ai/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        if auth:
            headers['Authorization'] = f"TOKEN {auth}"

        return headers

    def get_auth(self, account):
        for i in range(3):
            try:
                message_ = 'Please sign this message to confirm you are the owner of this address and Sign in to TrustGo App'
                message = message_.encode()
                message_to_sign = encode_defunct(primitive=message)
                signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
                sig = signed_message.signature.hex()
                payload = {
                    "address": account.address,
                    "message": message_,
                    "mode": 'evm',
                    "signature": sig
                }
                result = self.help.fetch_url(url='https://mp.trustalabs.ai/accounts/check_signed_message', type='post', headers=self.get_headers(), payload=payload)
                return result['data']['token']
            except:
                time.sleep(1)
        return None

    def get_prev_attests(self, type, auth):
        for i in range(3):
            try:
                URL = f"https://mp.trustalabs.ai/accounts/attestation?attest_type={type.lower}"
                result = self.help.fetch_url(url=URL, type='get', headers=self.get_headers(auth))
                return result['data']
            except:
                time.sleep(3)
        return

    def get_tx_data(self, type, auth):
        for i in range(3):
            try:
                URL = f"https://mp.trustalabs.ai/accounts/attest_calldata?attest_type={type.lower()}"
                result = self.help.fetch_url(url=URL, type='get',headers=self.get_headers(auth))
                return result['data']
            except:
                time.sleep(3)
        return

    def main(self, private_key, attempt=0, type='MEDIA'):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        auth = self.get_auth(account)
        if not auth:
            return self.main(private_key=private_key, attempt=attempt+1, type=type)

        prev_attestations = self.get_prev_attests(type, auth)
        if not prev_attestations:
            return self.main(private_key=private_key, attempt=attempt+1, type=type)

        if int(prev_attestations['total']) != 0:
            if type == 'HUMANITY':
                if int(prev_attestations['items'][0]['decode_data'][1]) >= -1:
                    self.logger.log_error( f"{self.project} | Аттестация POH с нужным сконором уже была получена, пропускаю",account.address)
                    return
            if type == 'MEDIA':
                if int(prev_attestations['items'][0]['decode_data'][1]) > 20:
                    self.logger.log_error(f"{self.project} | Аттестация MEDIA с нужным сконором уже была получена, пропускаю",account.address)
                    return

        tx_data = self.get_tx_data(type=type, auth=auth)
        if not tx_data:
            return self.main(private_key=private_key, attempt=attempt + 1, type=type)

        if type == 'MEDIA':
            if int(tx_data['message']['score']) <= 20:
                self.logger.log_error(f"{self.project} | Текущий MEDIA SCORE ({tx_data['message']['score']}) меньше или равен 20, пропускаю", account.address)
                return
        if type == 'HUMANITY':
            if int(tx_data['message']['score']) <= -2:
                self.logger.log_error(f"{self.project} | Текущий POH SCORE ({tx_data['message']['score']}) меньше или равен -2, пропускаю", account.address)
                return

        tx = make_tx(new_w3, account, value=int(tx_data['calldata']['value']), data=tx_data['calldata']['data'], to=new_w3.to_checksum_address(tx_data['calldata']['to']))

        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, attempt=attempt + 1, type=type)

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, attempt=attempt + 1, type=type)
        self.logger.log_success(f"{self.project} | Успешно заминтил аттестацию {type}!", account.address)
        return new_w3.to_hex(hash)

