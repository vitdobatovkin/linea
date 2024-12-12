import json, hashlib, uuid, base64, hmac
from helpers.data import chains_data, warmup_data, NULL_ADDRESS
from helpers.utils import *
from web3._utils.contracts import encode_abi
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from eth_account.messages import encode_defunct

class Mintfun():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'MINTFUN'

    def get_collections(self, chain):

        url = f'https://mint.fun/api/mintfun/feed/free?range=24h&chain={chain}'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                return result['collections']
            except:
                time.sleep(i*1)
        return []

    def get_data(self, collection, chain):
        url = f'https://mint.fun/api/mintfun/contract/{chain}:{collection}/transactions'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                for tx in result['transactions']:
                    if int(tx['nftCount']) == 1:
                        return tx
            except:
                time.sleep(i*1)
        return None

    def main(self, chain_from, private_key, attempt = 0):

        if attempt > 10:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        chain_code = chains_data[chain_from]['id']

        collections = self.get_collections(chain_code)
        if not collections:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        collection = random.choice(collections)

        _, contract = collection['contract'].split(':')
        tx_data = self.get_data(contract, chain_code)
        if not tx_data:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        if int(tx_data['ethValue']) > 0:
            return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)

        tx = make_tx(self.w3, account, data=tx_data['callData'], to=tx_data['to'], gas_multiplier=1, value=0)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно заминтил NFT {collection['name']} за 0 ETH",account.address)
        return self.w3.to_hex(hash)

class Lido():
    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'LIDO'

    def main(self, chain_from, private_key, attempt = 0):

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        tx = make_tx(self.w3, account, data='0xa1903eab0000000000000000000000000000000000000000000000000000000000000000', to=self.w3.to_checksum_address('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'), gas_multiplier=1, value=value)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно внёс в стейкинг {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Starknet():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.help = helper
        self.project = 'STARKNET BRIDGE'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['STARKNET']['contract']), abi=warmup_data['STARKNET']['ABI'])

    def get_message_fee(self, stark_address, value):
        url = f'https://alpha-mainnet.starknet.io/feeder_gateway/estimate_message_fee?blockNumber=pending'
        for i in range(5):
            try:
                payload = {"from_address":"993696174272377493693496825928908586134624850969","to_address":"0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82","entry_point_selector":"0x2d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5","payload":[f"0x{stark_address}",value,"0x0"]}
                result = self.help.fetch_url(url=url, type='post', payload=payload)
                return int(result['overall_fee'])
            except :
                time.sleep(i * 1)
        return 0

    def main(self, chain_from, private_key, attempt = 0):

        if attempt > 3:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        hash_object = hashlib.sha256(account.address.encode())
        stark_address = hash_object.hexdigest()
        stark_address = stark_address[:63]

        fee = self.get_message_fee(stark_address, hex(value))

        dep_func = self.contract.functions.deposit(value, int(stark_address, 16))
        dep_data = encode_abi(self.w3, dep_func.abi, [value, int(stark_address, 16)])
        data = f"0xe2bbb158{dep_data[2:]}"

        tx = make_tx(self.w3, account, value=value+fee, data=data, to=self.w3.to_checksum_address(warmup_data['STARKNET']['contract']))

        if tx == "low_native" or not tx or tx == 'error':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал бридж {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Zora():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'ZORA BRIDGE'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['ZORA']['contract']), abi=warmup_data['ZORA']['ABI'])

    def main(self, chain_from, private_key, attempt = 0):

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        func_ = getattr(self.contract.functions, 'depositTransaction')
        args = account.address, 0, 100000, False, '0x'
        tx = make_tx(self.w3, account, value=value, func=func_, args=args)

        if tx == "low_native" or not tx or tx == 'error':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал бридж {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Optimismbridge():
    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'OPTIMISM BRIDGE'

    def main(self, chain_from, private_key, attempt=0):
        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        if chain_from == 'ETH':

            data = '0xb1a1a8820000000000000000000000000000000000000000000000000000000000030d4000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000'
            to = self.w3.to_checksum_address('0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1')

            tx = make_tx(self.w3, account, data=data, to=to, gas_multiplier=1.1, value=value)

            if tx == "low_native" or not tx:
                return tx

            sign = account.sign_transaction(tx)
            hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
            tx_status = check_for_status(self.w3, hash)
            if not tx_status:
                return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)
            self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно забриджил в OPTIMISM {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        else:

            contract = self.w3.eth.contract( address=self.w3.to_checksum_address(warmup_data['OPTIMISM']['contract']), abi=warmup_data['OPTIMISM']['ABI'])
            func_ = getattr(contract.functions, 'withdraw')

            args = self.w3.to_checksum_address('DeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000'), value, 0, "0x"

            tx = make_tx(self.w3, account, value=value, func=func_, args=args)

            if tx == "low_native" or not tx:
                return tx

            sign = account.sign_transaction(tx)
            hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
            tx_status = check_for_status(self.w3, hash)
            if not tx_status:
                return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
            self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | забриджил в ETH MAINNET {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Arbitrumbridge():
    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'ARBITRUM BRIDGE'

    def main(self, chain_from, private_key, attempt=0):
        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        if chain_from == 'ETH':
            data = '0x439370b1'
            to = [{'address': self.w3.to_checksum_address('0xc4448b71118c9071Bcb9734A0EAc55D18A153949'), "chain": 'ARB NOVA'}, {'address': self.w3.to_checksum_address('0x4Dbd4fc535Ac27206064B68FfCf827b0A60BAB3f'), "chain": 'ARB ONE'}]
            to = random.choice(to)
        else:
            to = {"address": '0x0000000000000000000000000000000000000064', "chain": 'ETH MAINNET'}
            data = f'0x25e16063000000000000000000000000{account.address[2:]}'

        tx = make_tx(self.w3, account, data=data, to=to['address'], gas_multiplier=1, value=value)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно забриджил в {to['chain']} {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Polygonbridge():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'POLYGON BRIDGE'

    def main(self, chain_from, private_key, attempt=0):
        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        data = f'0x4faa8a26000000000000000000000000{account.address[2:]}'
        to = [{'address': self.w3.to_checksum_address('0xA0c68C638235ee32657e8f720a23ceC1bFc77C77'), "chain": 'POLYGON'},]
        to = random.choice(to)

        tx = make_tx(self.w3, account, data=data, to=to['address'], gas_multiplier=1, value=value)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt = attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно забриджил в {to['chain']} {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Aave():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'AAVE'

    def main(self, chain_from, private_key, attempt=0):
        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['AAVE'][chain_from]['contract']), abi=warmup_data['AAVE'][chain_from]['ABI'])
        balance = get_balance(self.w3, account, warmup_data[self.project][chain_from]['token'])
        withdraw = False if balance == 0 else random.choice([True, False])

        if not withdraw:
            func_ = getattr(contract.functions, 'depositETH')
            args = self.w3.to_checksum_address(warmup_data[self.project][chain_from]['pool']), account.address, 0
            tx = make_tx(self.w3, account, value=value, func=func_, args=args)
            action = 'SUPPLY'
        else:
            _value = balance / (10 ** 18)
            approve = check_approve(self.w3, account, warmup_data[self.project][chain_from]['token'], warmup_data[self.project][chain_from]['contract'])
            if not approve:
                make_approve(self.w3, account, warmup_data[self.project][chain_from]['token'], warmup_data[self.project][chain_from]['contract'])
            func_ = getattr(contract.functions, 'withdrawETH')
            args = self.w3.to_checksum_address(warmup_data[self.project][chain_from]['pool']), 115792089237316195423570985008687907853269984665640564039457584007913129639935, account.address
            tx = make_tx(self.w3, account, value=0, func=func_, args=args)
            action = 'WITHDRAW'

        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал {action} на сумму {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Radiant():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'RADIANT'

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 3:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data[self.project][chain_from]['contract']), abi=warmup_data[self.project][chain_from]['ABI'])

        balance = get_balance(self.w3, account, warmup_data[self.project][chain_from]['token'])
        withdraw = False if balance == 0 else random.choice([True,False])

        if not withdraw:
            func_ = getattr(contract.functions, 'depositETH')
            args = self.w3.to_checksum_address(warmup_data[self.project][chain_from]['pool']), account.address, 0
            tx = make_tx(self.w3, account, value=value, func=func_, args=args)
            action = 'SUPPLY'
        else:
            _value = balance / (10 ** 18)
            approve = check_approve(self.w3, account, warmup_data[self.project][chain_from]['token'], warmup_data[self.project][chain_from]['contract'])
            if not approve:
                make_approve(self.w3, account, warmup_data[self.project][chain_from]['token'], warmup_data[self.project][chain_from]['contract'])
            func_ = getattr(contract.functions, 'withdrawETH')
            args = self.w3.to_checksum_address(warmup_data[self.project][chain_from]['pool']), balance, account.address
            tx = make_tx(self.w3, account, value=0, func=func_, args=args)
            action = 'WITHDRAW'
        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал {action} на сумму {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class Approve():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'RANDOM APPROVE'
        self.headers = {
                'authority': 'api.uniswap.org',
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'text/plain;charset=UTF-8',
                'origin': 'https://app.uniswap.org',
                'referer': 'https://app.uniswap.org/',
                'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            }

    def get_tokens(self, chain):
        url = 'https://gateway.ipfs.io/ipns/tokens.uniswap.org'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                tokens = []
                for token in result['tokens']:
                    if int(token['chainId']) == chain:
                        tokens.append(token)
                return tokens
            except:
                time.sleep(i * 1)
        return []

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        chain_code = chains_data[chain_from]['id']
        tokens = self.get_tokens(chain_code)

        token = random.choice(tokens)

        random_dapp = random.choice(list(warmup_data['APPROVE'][chain_from]))
        dapp_address = self.w3.to_checksum_address(warmup_data['APPROVE'][chain_from][random_dapp])

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(token['address']), abi=TOKEN_ABI)
        func_ = getattr(contract.functions, 'approve')
        args = dapp_address, random.randint(10000000000000000000000000000000, 115792089237316195423570985008687907853269984665640564039457584007913129)
        tx = make_tx(self.w3, account, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)

        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал APPROVE токена {token['symbol']} для {random_dapp}",account.address)
        return self.w3.to_hex(hash)

class Uniswap():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'UNISWAP'
        self.headers = {
                'authority': 'api.uniswap.org',
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'text/plain;charset=UTF-8',
                'origin': 'https://app.uniswap.org',
                'referer': 'https://app.uniswap.org/',
                'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            }

    def get_tokens(self, chain):
        url = 'https://gateway.ipfs.io/ipns/tokens.uniswap.org'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                tokens = []
                for token in result['tokens']:
                    if int(token['chainId']) == chain:
                        tokens.append(token)
                return tokens
            except:
                time.sleep(i * 1)
        return []

    def get_quote(self, token, amount, chain, account):
        url = 'https://api.uniswap.org/v2/quote'
        payload = {"tokenInChainId":chain,"tokenIn":"ETH","tokenOutChainId":chain,"tokenOut":token,"amount":str(amount),"type":"EXACT_INPUT","configs":[{"useSyntheticQuotes":False,"recipient":account.address,"swapper":account.address,"routingType":"DUTCH_LIMIT"},{"protocols":["V2","V3","MIXED"],"routingType":"CLASSIC"}]}
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='post', payload=payload, headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)
        chain_code = chains_data[chain_from]['id']
        tokens = self.get_tokens(chain_code)

        token = random.choice(tokens)

        quote = self.get_quote(token['address'], value, chain_code, account)
        if quote.get('detail', '').lower() == 'No quotes available'.lower():
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        command = '0x0b00'
        address_this = self.w3.to_checksum_address("0x0000000000000000000000000000000000000002")
        address_sender = self.w3.to_checksum_address("0x0000000000000000000000000000000000000001")
        amount_out = int(int(quote['quote']['quote']))
        deadline = int(time.time()) + 30 * 60
        ABI_wrap = '[{"inputs":[{"name":"recipient","type":"address"},{"name":"amountMin","type":"uint256"}],"name":"WRAP_ETH","type":"function"}]'
        wrap_contract = self.w3.eth.contract(abi=ABI_wrap)
        wrap_func = wrap_contract.functions.WRAP_ETH(address_this, int(quote['quote']['amount']))
        wrap_data = encode_abi(self.w3, wrap_func.abi, [address_this, int(quote['quote']['amount'])])

        path = [self.w3.to_checksum_address(quote['quote']['route'][0][0]['tokenIn']['address']), self.w3.to_checksum_address(quote['quote']['route'][0][0]['tokenOut']['address'])]
        try:
            fee = int(quote['quote']['route'][0][0]['fee'])
        except:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        fee_encoded = '{:06X}'.format(fee)
        args = address_sender, int(quote['quote']['amount']), amount_out, path, False
        ABI_sub = '[{"inputs":[{"name":"recipient","type":"address"},{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"payerIsSender","type":"bool"}],"name":"V2_SWAP_EXACT_IN","type":"function"}]'
        sub_contract = self.w3.eth.contract(abi=ABI_sub)
        sub_func = sub_contract.functions.V2_SWAP_EXACT_IN(*args)
        sub_data = encode_abi(self.w3, sub_func.abi, args)

        sub_data = sub_data[:384]

        sub_data = f"{sub_data}2b{path[0][2:]}{fee_encoded}{path[1][2:]}000000000000000000000000000000000000000000"

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['UNISWAP'][chain_from]), abi=warmup_data['UNISWAP']['ABI'])

        func_ = getattr(contract.functions, 'execute')
        args = command, [wrap_data, sub_data], deadline
        tx = make_tx(self.w3, account, value=value, func=func_, args=args)

        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал SWAP {'{:.6f}'.format(round(float(quote['quote']['amountDecimals']), 7)).rstrip('0').rstrip('.')} ETH на {'{:.6f}'.format(round(float(quote['quote']['quoteDecimals']), 7)).rstrip('0').rstrip('.')} {token['symbol']}", account.address)
        return self.w3.to_hex(hash)

class Sushiswap():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'SUSHISWAP'
        self.headers = {
            'authority': 'tokens.sushi.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'if-none-match': 'W/"756ee-w1dk83JILWDmBka0UFzgRhFEbww"',
            'origin': 'https://www.sushi.com',
            'referer': 'https://www.sushi.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

    def get_tokens(self, chain):
        url = 'https://tokens.sushi.com/v0'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                tokens = []
                for token in result:
                    if int(token['chainId']) == chain:
                        tokens.append(token)
                return tokens
            except:
                time.sleep(i * 1)
        return []

    def get_quote(self, token, amount, chain, account):
        url = f'https://swap.sushi.com/{"v3.1" if chain != 10 else ""}?chainId={str(chain)}&tokenIn=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&tokenOut={token}&fromTokenId=ETH&toTokenId={token}&amount={str(amount)}&maxPriceImpact=0.01&to={account.address}&preferSushi=true'
        for i in range(2):
            try:
                result = self.helper.fetch_url(url=url, type='get', headers=self.headers, retries=5, timeout=5)
                return json.loads(result)
            except:
                time.sleep(i * 1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)
        chain_code = chains_data[chain_from]['id']
        tokens = self.get_tokens(chain_code)

        token = random.choice(tokens)

        quote = self.get_quote(token['address'], value, chain_code, account)
        if not quote.get('route', {}).get('status') == 'Success':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        route = quote['route']
        if float(route['priceImpact']) > 0.5:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['SUSHI'][chain_from]), abi=warmup_data['SUSHI']['ABI'])
        func_ = getattr(contract.functions, 'processRoute')
        args = quote['args']['tokenIn'], int(route['amountIn']), quote['args']['tokenOut'], int(route['amountOut']), account.address, quote['args']['routeCode']
        tx = make_tx(self.w3, account, value=int(route['amountIn']), func=func_, args=args)

        if tx == "low_native" or not tx or tx == 'error':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        to_value = int(route['amountOut']) / (10 ** int(route['toToken']['decimals']))
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал SWAP {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH на {'{:.6f}'.format(round(to_value, 7)).rstrip('0').rstrip('.')} {route['toToken']['symbol']}", account.address)
        return self.w3.to_hex(hash)

class Inch():

    def __init__(self, w3, logger, helper):
        self.project = '1INCH'
        self.headers = {
            'authority': 'api.odos.xyz',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://app.odos.xyz',
            'referer': 'https://app.odos.xyz/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-sec-fetch-site': 'same-origin',
        }
        self.w3 = w3
        self.logger = logger
        self.helper = helper

    def get_tokens(self, chain):
        url = 'https://gateway.ipfs.io/ipns/tokens.uniswap.org'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                tokens = []
                for token in result['tokens']:
                    if int(token['chainId']) == chain:
                        tokens.append(token)
                return tokens
            except:
                time.sleep(i * 1)
        return []

    def quote(self, amount, token_to, account, chain):
        for i in range(5):
            try:
                url = f"https://api-symbiosis.1inch.io/v5.0/{chain}/swap?fromTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&toTokenAddress={token_to}&amount={amount}&fromAddress={account.address}&destReceiver={account.address}&slippage=33&disableEstimate=true&allowPartialFill=false"
                result = self.helper.fetch_url(url=url, type='get', headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 15:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)
        chain_code = chains_data[chain_from]['id']
        tokens = self.get_tokens(chain_code)

        token = random.choice(tokens)

        quote = self.quote(str(value), token['address'], account, chain_code)
        if not quote:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        if quote.get('description', 'none').lower() == 'insufficient liquidity':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        elif quote.get('error', False):
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        tx = make_tx(self.w3, account, value=int(quote['tx']['value']), to=self.w3.to_checksum_address(quote['tx']['to']), data=quote['tx']['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        to_value = int(quote['toTokenAmount']) / 10 ** int(quote['toToken']['decimals'])
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал SWAP {'{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.')} ETH на {'{:.6f}'.format(round(to_value, 7)).rstrip('0').rstrip('.')} {token['symbol']}",account.address)
        return self.w3.to_hex(hash)

class Mirror():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'MIRROR'
        self.headers = {
            'authority': 'mirror.xyz',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://mirror.xyz',
            'referer': 'https://mirror.xyz/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

    def get_collections(self, chain=10):

        for i in range(5):
            try:
                payload = {
                    'operationName': 'projectCollection',
                    'variables': {
                        'projectAddress': '0xe60aC07Be8bD7f7f33d446e1399c329928Ba8114',
                        'limit': 1000,
                        'cursorStart': int(time.time() * 1000 - 10000),
                    },
                    'query': 'query projectCollection($projectAddress: String!, $limit: Int!, $cursorStart: Float, $cursorEnd: Float, $filterDigests: [String]) {\n  projectCollects(\n    projectAddress: $projectAddress\n    limit: $limit\n    cursorStart: $cursorStart\n    cursorEnd: $cursorEnd\n    filterDigests: $filterDigests\n  ) {\n    cursorStart\n    cursorEnd\n    wnfts {\n      _id\n      address\n      eventTimestamp\n      entry {\n        ...entryDetails\n        publisher {\n          ...publisherDetails\n          __typename\n        }\n        settings {\n          ...entrySettingsDetails\n          __typename\n        }\n        writingNFT {\n          ...writingNFTDetails\n          purchases {\n            ...writingNFTPurchaseDetails\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment entryDetails on entry {\n  _id\n  body\n  hideTitleInEntry\n  publishStatus\n  publishedAtTimestamp\n  digest\n  timestamp\n  title\n  arweaveTransactionRequest {\n    transactionId\n    __typename\n  }\n  featuredImageId\n  featuredImage {\n    mimetype\n    url\n    __typename\n  }\n  publisher {\n    ...publisherDetails\n    __typename\n  }\n  __typename\n}\n\nfragment publisherDetails on PublisherType {\n  project {\n    ...projectDetails\n    __typename\n  }\n  member {\n    ...projectDetails\n    __typename\n  }\n  __typename\n}\n\nfragment projectDetails on ProjectType {\n  _id\n  address\n  avatarURL\n  description\n  displayName\n  domain\n  ens\n  gaTrackingID\n  ga4TrackingID\n  mailingListURL\n  twitterUsername\n  wnftChainId\n  externalUrl\n  headerImage {\n    ...mediaAsset\n    __typename\n  }\n  theme {\n    ...themeDetails\n    __typename\n  }\n  __typename\n}\n\nfragment mediaAsset on MediaAssetType {\n  id\n  cid\n  mimetype\n  sizes {\n    ...mediaAssetSizes\n    __typename\n  }\n  url\n  __typename\n}\n\nfragment mediaAssetSizes on MediaAssetSizesType {\n  og {\n    ...mediaAssetSize\n    __typename\n  }\n  lg {\n    ...mediaAssetSize\n    __typename\n  }\n  md {\n    ...mediaAssetSize\n    __typename\n  }\n  sm {\n    ...mediaAssetSize\n    __typename\n  }\n  __typename\n}\n\nfragment mediaAssetSize on MediaAssetSizeType {\n  src\n  height\n  width\n  __typename\n}\n\nfragment themeDetails on UserProfileThemeType {\n  accent\n  colorMode\n  __typename\n}\n\nfragment entrySettingsDetails on EntrySettingsType {\n  description\n  metaImage {\n    ...mediaAsset\n    __typename\n  }\n  title\n  __typename\n}\n\nfragment writingNFTDetails on WritingNFTType {\n  _id\n  contractURI\n  contentURI\n  deploymentSignature\n  deploymentSignatureType\n  description\n  digest\n  fee\n  fundingRecipient\n  imageURI\n  canMint\n  media {\n    id\n    cid\n    __typename\n  }\n  nonce\n  optimisticNumSold\n  owner\n  price\n  proxyAddress\n  publisher {\n    project {\n      ...writingNFTProjectDetails\n      __typename\n    }\n    __typename\n  }\n  quantity\n  renderer\n  signature\n  symbol\n  timestamp\n  title\n  version\n  network {\n    ...networkDetails\n    __typename\n  }\n  __typename\n}\n\nfragment writingNFTProjectDetails on ProjectType {\n  _id\n  address\n  avatarURL\n  displayName\n  domain\n  ens\n  __typename\n}\n\nfragment networkDetails on NetworkType {\n  _id\n  chainId\n  __typename\n}\n\nfragment writingNFTPurchaseDetails on WritingNFTPurchaseType {\n  numSold\n  __typename\n}',
                }
                result = self.helper.fetch_url(url='https://mirror.xyz/api/graphql', type='post', payload=payload, headers=self.headers)
                eligable_collections = []
                for col in result['data']['projectCollects']['wnfts']:
                    try:
                        if int(col['entry']['writingNFT']['network']['chainId']) == chain:
                            eligable_collections.append(col['entry'])
                    except:
                        pass
                return eligable_collections
            except:
                time.sleep(i*1)
        return []

    def main(self, chain_from, private_key, attempt = 0):

        if attempt > 10:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)

        collections = self.get_collections()
        if not collections:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)
        collection = random.choice(collections)

        contract = collection['writingNFT']['proxyAddress']
        col_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract), abi=warmup_data[self.project]['ABI'])
        price = col_contract.functions.price().call()
        if price != 0:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        func_ = getattr(col_contract.functions, 'purchase')

        tx = make_tx(self.w3, account, value=int(0.00069 * 10 ** 18), func=func_, args=(account.address, ""), args_positioning=True)
        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно заминтил статью {collection['writingNFT']['title']} за 0.00069 ETH",account.address)
        return self.w3.to_hex(hash)

class Blur():
    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'BLUR'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data['BLUR']['contract']),  abi=warmup_data['BLUR']['ABI'])

    def main(self, chain_from, private_key, attempt = 0):

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        BETH_balance = self.contract.functions.balanceOf(account.address).call()
        action = random.choice(['deposit', 'withdraw']) if BETH_balance != 0 else 'deposit'

        func_ = getattr(self.contract.functions, action)
        args = BETH_balance if action == 'withdraw' else None
        tx = make_tx(self.w3, account, value=value if action == 'deposit' else 0, func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx or tx == 'error':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        formatted_value = '{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.') if action == 'deposit' else '{:.6f}'.format(round(BETH_balance / (10 ** 18), 7)).rstrip('0').rstrip('.')
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал {'вывод' if action == 'withdraw' else 'депозит'} {formatted_value} ETH", account.address)
        return self.w3.to_hex(hash)

class Wrapper():
    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'WRAPPER'

    def main(self, chain_from, private_key, attempt = 0):

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data[self.project][chain_from]), abi=warmup_data[self.project]['ABI'])

        account = self.w3.eth.account.from_key(private_key)
        _value = random.uniform(0.00001, 0.000001)
        value = int(_value * 10 ** 18)

        BETH_balance = contract.functions.balanceOf(account.address).call()
        action = random.choice(['deposit', 'withdraw']) if BETH_balance != 0 else 'deposit'

        func_ = getattr(contract.functions, action)
        args = BETH_balance if action == 'withdraw' else None
        tx = make_tx(self.w3, account, value=value if action == 'deposit' else 0, func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx or tx == 'error':
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        formatted_value = '{:.6f}'.format(round(_value, 7)).rstrip('0').rstrip('.') if action == 'deposit' else '{:.6f}'.format(round(BETH_balance / (10 ** 18), 7)).rstrip('0').rstrip('.')
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно сделал WRAP из {formatted_value} {'WETH' if action == 'withdraw' else 'ETH'} в {'WETH' if action != 'withdraw' else 'ETH'} ", account.address)
        return self.w3.to_hex(hash)

class OkxNFT():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'OKX NFT'

    def get_items(self, chain, account):
        items = []
        start_page = random.randint(0, 10)
        for i in range(10):
            for i in range(3):
                try:
                    payload = {"address":[account.address.lower()],"chainIn":[chain],"projectCertificated":True,"stateIn":["buyNow"],"priceRangeCurrency":"ETH","priceRangeMax":"0.0001","priceRangeMin":"0.00001","cursor":"","pageNum":i+start_page,"pageSize":50}
                    res = self.helper.fetch_url(url=f"https://www.okx.com/priapi/v1/nft/secondary/market?t={int(time.time())}", type='post', payload=payload)
                    if int(res['code']) == 0:
                        for item in res['data']['list']:
                            items.append(item)
                    break
                except:
                    time.sleep(1)
        return items

    def get_order_id(self, nft_id):
        for i in range(3):
            try:
                res = self.helper.fetch_url(url=f"https://www.okx.com/priapi/v1/nft/order/orders?t={int(time.time())}&showAllOrder=False&nftId={nft_id}&ownerAddress=&page=1&pageSize=1", type='get')
                if int(res['code']) == 0:
                    return res['data']['list'][0]['id']
            except:
                time.sleep(1)
        return None

    def get_buy_data(self, order_id, nft_id, account, chain):
        for i in range(3):
            try:
                payload = {"chain":chain,"items":[{"orderId":order_id,"nftId":str(nft_id),"takeCount":1}],"walletAddress":account.address.lower()}
                res = self.helper.fetch_url(url=f"https://www.okx.com/priapi/v1/nft/trading/buy?t={int(time.time())}", type='post', payload=payload)
                if int(res['code']) == 0:
                    return res['data']['steps'][0]['items'][0]
            except:
                time.sleep(1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 3:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        chain_code = chains_data[chain_from]['id']
        items = self.get_items(chain_code, account)
        if len(items) == 0:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        item = random.choice(items)
        order_id = self.get_order_id(int(item['id']))
        if not order_id:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        buy_data = self.get_buy_data(order_id, int(item['id']), account, chain_code)
        if not buy_data:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        tx = make_tx(self.w3, account, value=int(buy_data['value']), data=buy_data['input'], to=self.w3.to_checksum_address(buy_data['contractAddress']))
        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        if chain_from == 'ETH' and int(tx['gas']) > 500000:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно купил NFT {item['projectName']} за {buy_data['totalPrice']} ETH", account.address)
        return self.w3.to_hex(hash)

class TofuNFT():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'TOFU NFT'

    def generate_sig(self):
        random_uuid = str(uuid.uuid4())
        aes_key = bytes.fromhex('1b74605c06a8088d6865f58dd3391034')
        aes_iv = bytes.fromhex('ec03f33b265acb43e22e5f3f5c74e7b9')
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(random_uuid.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_b64 = base64.urlsafe_b64encode(encrypted).decode('utf-8').rstrip('=')
        sig = f"{random_uuid}{encrypted_b64}"
        return sig

    def get_headers(self, auth=None):
        headers = {
            'authority': 'tofunft.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json; charset=utf-8',
            'origin': 'https://tofunft.com',
            'referer': 'https://tofunft.com/discover/items?category=fixed-price&isBundle=0&network=42161&priceMax=0.0001&priceMin=0.00001',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'x-tofu-signature': self.generate_sig(),
        }
        if auth:
            headers['authorization'] = f"Bearer {auth}"
        return headers

    def get_items(self, chain):
        offset = random.randint(0, 10)
        for i in range(3):
            try:
                payload = {"filters":{"category":"fixed-price","priceMin":0.00001,"priceMax":0.0001,"isBundle":False,"attributes":{},"network":chain,"contracts":[]},"offset":offset,"limit":1000}
                res = self.helper.fetch_tls(url=f"https://tofunft.com/api/searchOrders", type='post', payload=payload, session=self.helper.get_tls_session(), headers=self.get_headers())
                return res['right']['data']
            except:
                time.sleep(1)
        return []

    def get_order_data(self, nft_id):
        for i in range(3):
            try:
                payload = {"filters":{"nft":nft_id,"category":"all"},"offset":0,"limit":1}
                res = self.helper.fetch_tls(url="https://tofunft.com/api/searchActivities", type='post', payload=payload, session=self.helper.get_tls_session(), headers=self.get_headers())
                if int(res['right']['total']) == 0:
                    return
                return res['right']['data'][0]
            except:
                time.sleep(1)
        return None

    def get_buy_data(self, order_id, price, account, auth):
        for i in range(3):
            try:
                payload = {"caller":account.address,"coupon":0,"orderId":order_id,"currency":"0x0000000000000000000000000000000000000000","price":str(price),"opcode":1}
                res = self.helper.fetch_tls(url=f"https://tofunft.com/api/market/detail", type='post', payload=payload, session=self.helper.get_tls_session(), headers=self.get_headers(auth))
                return res['right']['data']
            except:
                time.sleep(1)
        return None

    def get_auth(self, account):
        for i in range(3):
            try:
                msg_ = f"Please sign to let us verify that you are the owner of this address:\n{account.address}\n\n[12.12.2222, 22:22:22]"
                message = msg_.encode()
                message_to_sign = encode_defunct(primitive=message)
                signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
                sig = signed_message.signature.hex()
                payload = {"address":account.address,"msg":msg_,"signedMsg":sig,"dappName":"injected"}
                res = self.helper.fetch_tls(url=f"https://tofunft.com/api/user/signIn", type='post', payload=payload, session=self.helper.get_tls_session(), headers=self.get_headers())
                self.helper.fetch_tls(url=f"https://tofunft.com/api/user/refreshToken", type='post', payload={"refreshToken": res['right']['refreshToken']}, session=self.helper.get_tls_session(), headers=self.get_headers())
                return res['right']['refreshToken']
            except:
                time.sleep(1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 3:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)
        chain_code = chains_data[chain_from]['id']
        items = self.get_items(chain_code)
        if len(items) == 0:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        item = random.choice(items)
        order_id = self.get_order_data(int(item['nft']['id']))
        if order_id is None:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        auth = self.get_auth(account)
        if auth is None:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        price_uint = self.w3.to_wei(float(item['price']), 'ether')

        buy_data = self.get_buy_data(int(order_id['order']['id']), price_uint, account, auth)
        if buy_data is None:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        cont = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data[self.project][chain_from]), abi=warmup_data[self.project]['ABI'])
        func_ = getattr(cont.functions, 'run')

        DATA_detail = bytes.fromhex(buy_data['detail'][2:])
        DATA_intention = bytes.fromhex(buy_data['intention'][2:])
        intent_types = ['(address,(address,uint256,uint256,uint8,bytes)[],address,uint256,uint256,bytes32,uint8)']
        detail_types = ['(bytes32,address,uint256,bytes32,uint256,uint8,address,address,uint256,uint256,(uint256[],uint256,uint256,uint256,address,address),(address,uint256,uint256,uint8,bytes)[],uint256)']

        decoded_detail = list(self.w3.codec.decode(detail_types, DATA_detail)[0])
        decoded_intention = list(self.w3.codec.decode(intent_types, DATA_intention)[0])

        def to_checksum_nested(item):
            if isinstance(item, tuple):
                return tuple(to_checksum_nested(list(item)))
            elif isinstance(item, list):
                return [to_checksum_nested(x) for x in item]
            elif isinstance(item, str) and len(item) == 42 and item.startswith('0x'):
                return self.w3.to_checksum_address(item)
            else:
                return item

        args = to_checksum_nested(decoded_intention), to_checksum_nested(decoded_detail), bytes.fromhex(buy_data['sigIntent'][2:]), bytes.fromhex(buy_data['sigDetail'][2:])

        tx = make_tx(self.w3, account, value=price_uint, args=args, args_positioning=True, func=func_)
        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        if chain_from == 'ETH' and int(tx['gas']) > 500000:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно купил NFT {item['nft']['meta']['name']} за {item['price']} ETH", account.address)
        return self.w3.to_hex(hash)

class ElementNFT():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'ELEMENT NFT'
        self.chain_ids = {'ARB': 601, 'ETH': 1}

    def generate_xapi_signature(self, api_key='zQbYj7RhC1VHIBdWU63ki5AJKXloamDT', secret='UqCMpfGn3VyQEdsjLkzJv9tNlgbKFD7O'):
        random_number = random.randint(1000, 9999)
        timestamp = int(time.time())
        message = f"{api_key}{random_number}{timestamp}"
        signature = hmac.new(bytes(secret, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
        return f"{signature}.{random_number}.{timestamp}"

    def get_headers(self, chain, auth=False):
        headers = {
            'authority': 'api.element.market',
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://element.market',
            'referer': 'https://element.market/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-api-key': 'zQbYj7RhC1VHIBdWU63ki5AJKXloamDT',
            'x-api-sign': str(self.generate_xapi_signature()),
            'x-viewer-chainmid': str(chain),
        }
        if auth:
            headers['auth'] = auth
        return headers

    def get_items(self, chain):
        items = []
        last_res = None
        for i in range(10):
            for i in range(3):
                try:
                    payload = {
                        'operationName': 'ExploreAssetsList',
                        'variables': {
                            'thirdStandards': [],
                            'blockChains': [
                                {
                                    'chain': 'arbitrum' if chain == 'ARB' else 'eth',
                                    'chainId': '0xa4b1' if chain == 'ARB' else '0x1',
                                },
                            ],
                            'first': 50,
                            'uiFlag': 'MARKET',
                            'sortAscending': False,
                            'sortBy': 'RecentlyListed',
                            'toggles': [
                                'BUY_NOW',
                            ],
                            'priceFilter': {
                                'symbol': 'ETH',
                                'min': '0.00001',
                                'max': '0.0001',
                            },
                        },
                        'query': 'query ExploreAssetsList($before: String, $after: String, $first: Int, $last: Int, $querystring: String, $categorySlugs: [String!], $collectionSlugs: [String!], $sortBy: SearchSortBy, $sortAscending: Boolean, $toggles: [SearchToggle!], $ownerAddress: Address, $creatorAddress: Address, $blockChains: [BlockChainInput!], $paymentTokens: [String!], $priceFilter: PriceFilterInput, $stringTraits: [StringTraitInput!], $contractAliases: [String!], $thirdStandards: [String!], $uiFlag: SearchUIFlag, $markets: [String!]) {\n  search(\n    \n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    search: {querystring: $querystring, categorySlugs: $categorySlugs, collectionSlugs: $collectionSlugs, sortBy: $sortBy, sortAscending: $sortAscending, toggles: $toggles, ownerAddress: $ownerAddress, creatorAddress: $creatorAddress, blockChains: $blockChains, paymentTokens: $paymentTokens, priceFilter: $priceFilter, stringTraits: $stringTraits, contractAliases: $contractAliases, uiFlag: $uiFlag, markets: $markets}\n  ) {\n    totalCount\n    edges {\n      cursor\n      node {\n        asset {\n          chain\n          chainId\n          contractAddress\n          tokenId\n          tokenType\n          name\n          imagePreviewUrl\n          animationUrl\n          rarityRank\n          isFavorite\n          assetOwners(first: 1) {\n            ...AssetOwnersEdges\n          }\n          orderData(standards: $thirdStandards) {\n            bestAsk {\n              ...BasicOrder\n            }\n            bestBid {\n              ...BasicOrder\n            }\n          }\n          assetEventData {\n            lastSale {\n              lastSalePrice\n              lastSalePriceUSD\n              lastSaleTokenContract {\n                name\n                address\n                icon\n                decimal\n                accuracy\n              }\n            }\n          }\n          collection {\n            name\n            isVerified\n            slug\n            imageUrl\n            royalty\n            royaltyAddress\n            contracts {\n              blockChain {\n                chain\n                chainId\n              }\n            }\n          }\n          uri\n          pendingTx {\n            time\n            hash\n            gasFeeMax\n            gasFeePrio\n            txFrom\n            txTo\n            market\n          }\n        }\n      }\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      startCursor\n      endCursor\n    }\n  }\n}\n\nfragment BasicOrder on OrderV3Type {\n  __typename\n  chain\n  chainId\n  chainMId\n  expirationTime\n  listingTime\n  maker\n  taker\n  side\n  saleKind\n  paymentToken\n  quantity\n  priceBase\n  priceUSD\n  price\n  standard\n  contractAddress\n  tokenId\n  schema\n  extra\n  paymentTokenCoin {\n    name\n    address\n    icon\n    chain\n    chainId\n    decimal\n    accuracy\n  }\n}\n\nfragment AssetOwnersEdges on AssetOwnershipTypeConnection {\n  __typename\n  edges {\n    cursor\n    node {\n      chain\n      chainId\n      owner\n      balance\n      account {\n        identity {\n          address\n          blockChain {\n            chain\n            chainId\n          }\n        }\n        user {\n          id\n          address\n          profileImageUrl\n          userName\n        }\n        info {\n          profileImageUrl\n          userName\n        }\n      }\n    }\n  }\n}\n',
                    }
                    if last_res:
                        payload['variables']['after'] = last_res
                    res = self.helper.fetch_tls(url=f"https://api.element.market/graphql", type='post', params={'args': 'ExploreAssetsList'}, payload=payload, session=self.helper.get_tls_session(), headers=self.get_headers(601 if chain == 'ARB' else 1))
                    last_res = res['data']['search']['pageInfo']['endCursor']
                    for i in res['data']['search']['edges']:
                        items.append(i['node'])
                    break
                except:
                    time.sleep(1)
        return items

    def get_buy_data(self, contract, token_id, type, chain, account):
        for i in range(5):
            try:
                type = 'buyERC721Ex' if type == 'ERC721' else 'buyERC1155Ex'
                headers = self.get_headers(601 if chain == 'ARB' else 1)
                json_data = {
                    'chainMId': self.chain_ids[chain],
                    'buyer': account.address.lower(),
                    'data': [
                        {
                            'contractAddress': str(contract).lower(),
                            'tokenId': str(token_id),
                            'callFuncName': str(type),
                        },
                    ],
                    'standards': [],
                }
                result = self.helper.fetch_tls(session=self.helper.get_tls_session(), url='https://api.element.market/v3/orders/exSwapTradeDataByItem', type='post', headers=headers, payload=json_data)
                return result['data']['commonData'][0]
            except Exception as e:
                print(e)
                time.sleep((i + 1) * i)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 3:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)

        items = self.get_items(chain_from)
        if len(items) == 0:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt+1)

        item = random.choice(items)['asset']

        buy_data = self.get_buy_data(item['contractAddress'], int(item['tokenId']), item['tokenType'], chain_from, account)
        if buy_data is None:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        if buy_data['data'] == '0x':
            exchange_data = json.loads(buy_data['exchangeData'])

            # data1
            start_nonce = int(exchange_data['startNonce'])
            v = int(exchange_data['v'])
            listing_time = int(exchange_data['listingTime'])
            maker = int(exchange_data['maker'], 16)
            data1 = (start_nonce << 200) + (v << 192) + (listing_time << 160) + maker

            # data2
            expiry_time = int(exchange_data['expirationTime'])
            data_hex = account.address[:18].lower() + self.w3.to_hex(expiry_time)[2:]
            while len(data_hex) < 66:
                data_hex += "e"
            data2 = int(data_hex, 16)

            # data3
            taker_part2 = int(account.address.lower()[18:], 16)
            platform_fee_recipient = int(exchange_data['platformFeeRecipient'], 16)
            binary_string = bin(taker_part2)[2:].zfill(96) + bin(platform_fee_recipient)[2:].zfill(160)
            data3 = int(binary_string, 2)

            r = exchange_data['r']
            s = exchange_data['s']

            def encode_bits(args):
                data = '0x'
                for arg in args:
                    value, bit_count = arg
                    if isinstance(value, str):
                        if value.startswith('0x'):
                            data += to_hex_bytes(value, bit_count)
                        else:
                            data += to_hex_bytes(hex(int(value)), bit_count)
                    else:
                        data += to_hex_bytes(hex(value), bit_count)
                return data

            def to_hex_bytes(hex_str, bit_count):
                count = bit_count // 4
                str_val = hex_str.lower()[2:] if hex_str.lower().startswith('0x') else hex_str.lower()
                if len(str_val) > count:
                    return str_val[-count:]
                zeros = '0' * (count - len(str_val))
                return zeros + str_val

            def get_items_count(order):
                count = 0
                if order['basicCollections']:
                    for basic_collection in order['basicCollections']:
                        items = basic_collection['items']
                        if not items or len(items) > 255:
                            raise ValueError(f"The BatchSignedERC721Order(orderHash={order['hash']}) is invalid.")
                        count += len(items)

                if order['collections']:
                    for collection in order['collections']:
                        items = collection['items']
                        if not items or len(items) > 255:
                            raise ValueError(f"The BatchSignedERC721Order(orderHash={order['hash']}) is invalid.")
                        count += len(items)

                return count

            def to_collections_bytes(order, nonces):
                bytes_str = '0x'
                value = 0
                filled_nonce_set = set()
                royalty_fee_stat = {}

                collection_start_nonce = order['startNonce']
                index = 0

                def handle_collection(coll, collection_type):
                    nonlocal bytes_str, value, filled_nonce_set, royalty_fee_stat, collection_start_nonce, index
                    items_count = len(coll['items'])
                    start_nonce = collection_start_nonce
                    end_nonce = start_nonce + items_count
                    collection_start_nonce = end_nonce

                    filled_index_list = []

                    i = 0
                    while index < len(nonces) and start_nonce <= nonces[index] < end_nonce:
                        if i < 16:
                            filled_nonce_set.add(nonces[index])
                            filled_index_list.append(nonces[index] - start_nonce)
                            value += int(coll['items'][filled_index_list[i]]['erc20TokenAmount'])
                        index += 1
                        i += 1

                    filled_index_list_part1 = '0'
                    filled_index_list_part2 = '0'
                    if filled_index_list:
                        if coll['royaltyFeeRecipient'] != NULL_ADDRESS:
                            key = coll['royaltyFeeRecipient'].lower()
                            royalty_fee_stat[key] = royalty_fee_stat.get(key, 0) + 1

                        filled_index_list_hex = ''.join(
                            ['0' + hex(x)[2:] if x < 16 else hex(x)[2:] for x in filled_index_list])
                        filled_index_list_hex = filled_index_list_hex.ljust(32, '0')
                        filled_index_list_part1 = '0x' + filled_index_list_hex[:24]
                        filled_index_list_part2 = '0x' + filled_index_list_hex[24:]

                    head1 = encode_bits([
                        [filled_index_list_part1, 96],
                        [coll['nftAddress'], 160]
                    ])

                    head2 = encode_bits([
                        [collection_type, 8],
                        [items_count, 8],
                        [len(filled_index_list), 8],
                        [0, 8],
                        [filled_index_list_part2, 32],
                        [coll['platformFee'], 16],
                        [coll['royaltyFee'], 16],
                        [coll['royaltyFeeRecipient'], 160]
                    ])

                    items_bytes = '0x'
                    for item in coll['items']:
                        item_bytes = encode_bits([
                            [item['erc20TokenAmount'], 96],
                            [item['nftId'], 160]
                        ])
                        items_bytes += item_bytes[2:]

                    bytes_str += head1[2:] + head2[2:] + items_bytes[2:]

                if order['basicCollections']:
                    for basic_collection in order['basicCollections']:
                        handle_collection(basic_collection, 0)

                if order['collections']:
                    for collection in order['collections']:
                        handle_collection(collection, 1)

                return {
                    "value": value,
                    "royalty_fee_stat": royalty_fee_stat,
                    "bytes": bytes_str,
                    "filled_nonce_set": filled_nonce_set
                }

            def to_collections_bytes_list(order, nonce):
                if nonce is None:
                    return None

                nonces = [nonce]
                nonce_limit = order['startNonce'] + get_items_count(order)
                if nonces[-1] >= nonce_limit:
                    raise ValueError(
                        f"The BatchSignedERC721Order(orderHash={order.hash}) is invalid, nonce={nonces[-1]}, nonceLimit={nonce_limit}.")

                value = 0
                royalty_fee_stat = {}
                bytes_list = []

                filled_nonce_set = set()

                while len(filled_nonce_set) < len(nonces):
                    unfilled_nonce_list = [nonce for nonce in nonces if nonce not in filled_nonce_set]

                    r = to_collections_bytes(order, unfilled_nonce_list)
                    value += r["value"]
                    for k, v in r["royalty_fee_stat"].items():
                        if k in royalty_fee_stat:
                            royalty_fee_stat[k] += v
                        else:
                            royalty_fee_stat[k] = v
                    bytes_list.append(r["bytes"])

                    filled_nonce_set.update(r["filled_nonce_set"])

                return {
                    "value": str(value),
                    "royaltyFeeStat": royalty_fee_stat,
                    "bytesList": bytes_list
                }

            bytes_list = to_collections_bytes_list(exchange_data, int(exchange_data['nonce']))

            contract = self.w3.eth.contract(address=self.w3.to_checksum_address(warmup_data[self.project][chain_from]), abi=warmup_data[self.project]['ABI'])
            func_ = getattr(contract.functions, 'fillBatchSignedERC721Order')

            args = (data1, data2, data3, r, s), bytes_list['bytesList'][0]

            tx = make_tx(self.w3, account, value=int(bytes_list['value']), args=args, args_positioning=True, func=func_)

            price = int(bytes_list['value'])
        else:
            print()
            price = int(buy_data['value'])
            tx = make_tx(self.w3, account, value=int(buy_data['value']), data=buy_data['data'], to=self.w3.to_checksum_address(buy_data['toAddress']))

        if tx == "low_native" or not tx:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        if chain_from == 'ETH' and int(tx['gas']) > 500000:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно купил NFT ({item['name']}) за {'{:.6f}'.format(round(price / 10 ** 18, 7)).rstrip('0').rstrip('.')} ETH", account.address)
        return self.w3.to_hex(hash)

class OpenseaNFT():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'OPENSEA NFT'
        self.os_codes = {
            "RankingsPageTopPaginationQuery": '43d206f912f78f33454b8f958460f066df21e612482dccca3fd7bd2b5f045bfb',
            "authLoginMutation": '856ed51d371b833d93a6d0dcf69be76ffc010d88dc7d2980466f178a77a8c28b',
            "challengeLoginMessageQuery": '05649d324b3f3db988d5065ea33599bca390adf00e3f46952dd59ff5cc61e1e0',
            "RankingsPageTrendingQuery": '82e3e1549c27ae11258aecbe7ca0144fa9c7f4c793f2efb02e113b1f165d5fb9',
            "CollectionAssetSearchListQuery": '642c6474ecd06e22676ea678fa721c85bb1e9feb9dfc7e691a8300183f25b647',
            "FulfillActionModalQuery": 'f06d6357e2c153142ccd8e0d3ad35872522bfe9d1fa818137208e01b22f7602b',
            "useHandleBlockchainActionsCreateOrderMutation": '18153293ebaa96627ccfdf9b29fbaa92539438162b8b61add8feef6f0eb321d5',
            "AssetSellPageQuery": '373428b700e52dea14d194d667673e430ba62c8b1922a5687cecaff70789b29c',
            "AccountCollectedAssetSearchListQuery": '487ab8a857d60b3e546c98612a657cbb35e67db054e59b58d2deaa9326b53e69',
            "CreateListingActionModalQuery": 'd2434da5e36eafbc126f332a59e09568b7f66b1a28adddf6bcca76267f1424ac',
        }
        self.chain_name = {'ARB': "ARBITRUM", 'ETH': "ETHEREUM", 'OPT': "OPTIMISM"}

    def get_headers(self, account, operation=None, auth=None):
        headers = {
            'authority': 'opensea.io',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://opensea.io',
            'referer': 'https://opensea.io/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'x-app-id': 'opensea-web',
            'x-build-id': 'b82583d5d20f76d6f591fb08e369371931819542',
            'x-signed-query': self.os_codes[operation],
            'x-viewer-address': account.address,
        }
        if auth:
            headers['authorization'] = f'JWT {auth}'
        return headers

    def get_auth(self, account, session):
        for i in range(5):
            try:
                json_data = {
                    'id': 'challengeLoginMessageQuery',
                    'query': 'query challengeLoginMessageQuery(\n  $address: AddressScalar!\n) {\n  auth {\n    loginMessage(address: $address)\n  }\n}\n',
                    'variables': {
                        'address': account.address,
                    },
                }
                response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post', headers=self.get_headers(account, operation=json_data['id']), payload=json_data, session=session)
                message_ = response['data']['auth']['loginMessage']
                message = message_.encode()
                message_to_sign = encode_defunct(primitive=message)
                signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
                sig = signed_message.signature.hex()

                json_data = {
                    'id': 'authLoginMutation',
                    'query': 'mutation authLoginMutation(\n  $address: AddressScalar!\n  $message: String!\n  $signature: String!\n  $chain: ChainScalar\n) {\n  auth {\n    webLogin(address: $address, message: $message, signature: $signature, chain: $chain) {\n      token\n      account {\n        address\n        isEmployee\n        moonpayKycStatus\n        moonpayKycRejectType\n        id\n      }\n    }\n  }\n}\n',
                    'variables': {
                        'address': account.address.lower(),
                        'message': message_,
                        'signature': sig,
                        'chain': 'BASE',
                    },
                }
                response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post', headers=self.get_headers(account, operation=json_data['id']), payload=json_data, session=session)

                return response['data']['auth']['webLogin']['token']
            except:
                time.sleep(i*1)
        return None

    def get_collections(self, account, auth, session, chain):
        for i in range(5):
            try:
                collections = []
                if chain != 'ETH':
                    json_data = {
                        'id': 'RankingsPageTrendingQuery',
                        'query': 'query RankingsPageTrendingQuery(\n  $chain: [ChainScalar!]\n  $count: Int!\n  $cursor: String\n  $categories: [CategoryV2Slug!]!\n  $eligibleCount: Int!\n  $trendingCollectionsSortBy: TrendingCollectionSort\n  $timeWindow: StatsTimeWindow\n) {\n  ...RankingsPageTrending_data\n}\n\nfragment RankingsPageTrending_data on Query {\n  trendingCollectionsByCategory(after: $cursor, chains: $chain, first: $count, sortBy: $trendingCollectionsSortBy, categories: $categories, topCollectionLimit: $eligibleCount) {\n    edges {\n      node {\n        createdDate\n        name\n        slug\n        logo\n        isVerified\n        relayId\n        ...StatsCollectionCell_collection\n        ...collection_url\n        statsV2 {\n          totalQuantity\n        }\n        windowCollectionStats(statsTimeWindow: $timeWindow) {\n          floorPrice {\n            unit\n            eth\n            symbol\n          }\n          numOwners\n          totalSupply\n          totalListed\n          numOfSales\n          volumeChange\n          volume {\n            unit\n            eth\n            symbol\n          }\n        }\n        id\n        __typename\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment StatsCollectionCell_collection on CollectionType {\n  name\n  imageUrl\n  isVerified\n  slug\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n',
                        'variables': {
                            'chain': [
                                self.chain_name[chain],
                            ],
                            'count': 1000,
                            'cursor': None,
                            'categories': [],
                            'eligibleCount': 1000,
                            'trendingCollectionsSortBy': 'ONE_DAY_SALES',
                            'timeWindow': 'ONE_DAY',
                        },
                    }
                    response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post', headers=self.get_headers(account, operation=json_data['id'], auth=auth), payload=json_data,  session=session)
                    for col in response['data']['trendingCollectionsByCategory']['edges']:
                        try:
                            col = col['node']
                            if int(col['windowCollectionStats']['totalListed']) > 0 and float(col['windowCollectionStats']['floorPrice']['eth']) <= 0.00015:
                                collections.append(col)
                        except:
                            pass
                else:
                    json_data = {
                        'id': 'RankingsPageTopPaginationQuery',
                        'query': 'query RankingsPageTopPaginationQuery(\n  $categories: [CategoryV2Slug!]!\n  $chain: [ChainScalar!]\n  $count: Int\n  $createdAfter: DateTime\n  $cursor: String\n  $floorPricePercentChange: Boolean!\n  $parents: [CollectionSlug!]\n  $sortBy: CollectionSort\n  $timeWindow: StatsTimeWindow\n  $topCollectionsSortBy: TrendingCollectionSort\n) {\n  ...RankingsPageTop_data\n}\n\nfragment RankingsPageTop_data on Query {\n  rankings(after: $cursor, chains: $chain, first: $count, sortBy: $sortBy, parents: $parents, createdAfter: $createdAfter) {\n    edges {\n      node {\n        createdDate\n        name\n        slug\n        logo\n        isVerified\n        relayId\n        ...StatsCollectionCell_collection\n        ...collection_url\n        statsV2 {\n          totalQuantity\n        }\n        windowCollectionStats(statsTimeWindow: $timeWindow) {\n          floorPrice {\n            unit\n            eth\n            symbol\n          }\n          numOwners\n          totalSupply\n          totalListed\n          numOfSales\n          volumeChange\n          volume {\n            eth\n            unit\n            symbol\n          }\n        }\n        floorPricePercentChange(statsTimeWindow: $timeWindow) @include(if: $floorPricePercentChange)\n        id\n        __typename\n      }\n      cursor\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n  topCollectionsByCategory(after: $cursor, chains: $chain, first: $count, sortBy: $topCollectionsSortBy, categories: $categories) {\n    edges {\n      node {\n        createdDate\n        name\n        slug\n        logo\n        isVerified\n        relayId\n        ...StatsCollectionCell_collection\n        ...collection_url\n        statsV2 {\n          totalQuantity\n        }\n        windowCollectionStats(statsTimeWindow: $timeWindow) {\n          floorPrice {\n            unit\n            eth\n            symbol\n          }\n          numOwners\n          totalSupply\n          totalListed\n          numOfSales\n          volumeChange\n          volume {\n            eth\n            unit\n            symbol\n          }\n        }\n        floorPricePercentChange(statsTimeWindow: $timeWindow) @include(if: $floorPricePercentChange)\n        id\n      }\n    }\n  }\n}\n\nfragment StatsCollectionCell_collection on CollectionType {\n  name\n  imageUrl\n  isVerified\n  slug\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n',
                        'variables': {
                            'categories': [],
                            'chain': [
                                'ETHEREUM',
                            ],
                            'count': 1000,
                            'createdAfter': None,
                            'cursor': None,
                            'floorPricePercentChange': False,
                            'parents': None,
                            'sortBy': 'THIRTY_DAY_VOLUME',
                            'timeWindow': 'THIRTY_DAY',
                            'topCollectionsSortBy': 'THIRTY_DAY_VOLUME',
                        },
                    }
                    response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post',  headers=self.get_headers(account, operation=json_data['id'], auth=auth), payload=json_data, session=session)
                    for col in response['data']['rankings']['edges']:
                        try:
                            col = col['node']
                            if int(col['windowCollectionStats']['totalListed']) > 0 and float(col['windowCollectionStats']['floorPrice']['eth']) <= 0.00015:
                                collections.append(col)
                        except:
                            pass
                return collections
            except:
                time.sleep(i*1)
        return []

    def get_nfts(self, account, auth, session, collection):
        for i in range(5):
            try:
                json_data = {
                    'id': 'CollectionAssetSearchListQuery',
                    'query': 'query CollectionAssetSearchListQuery(\n  $collections: [CollectionSlug!]!\n  $count: Int!\n  $numericTraits: [TraitRangeType!]\n  $paymentAssets: [PaymentAssetSymbol]\n  $priceFilter: PriceFilterType\n  $query: String\n  $rarityFilter: RarityFilterType\n  $resultModel: SearchResultModel\n  $sortAscending: Boolean\n  $sortBy: SearchSortBy\n  $stringTraits: [TraitInputType!]\n  $toggles: [SearchToggle!]\n  $shouldShowBestBid: Boolean!\n  $owner: IdentityInputType\n  $filterOutListingsWithoutRequestedCreatorFees: Boolean\n) {\n  ...CollectionAssetSearchListPagination_data_1eC64m\n}\n\nfragment AccountLink_data on AccountType {\n  address\n  config\n  isCompromised\n  user {\n    publicUsername\n    id\n  }\n  displayName\n  ...ProfileImage_data\n  ...wallet_accountKey\n  ...accounts_url\n}\n\nfragment AddToCartAndQuickBuyButton_order on OrderV2Type {\n  ...useIsQuickBuyEnabled_order\n  ...ItemAddToCartButton_order\n  ...QuickBuyButton_order\n}\n\nfragment AssetContextMenu_data on AssetType {\n  relayId\n}\n\nfragment AssetMediaAnimation_asset on AssetType {\n  ...AssetMediaImage_asset\n  ...AssetMediaContainer_asset\n  ...AssetMediaPlaceholderImage_asset\n}\n\nfragment AssetMediaAudio_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMediaContainer_asset on AssetType {\n  backgroundColor\n  ...AssetMediaEditions_asset_1mZMwQ\n  collection {\n    ...useIsRarityEnabled_collection\n    id\n  }\n}\n\nfragment AssetMediaContainer_asset_1LNk0S on AssetType {\n  backgroundColor\n  ...AssetMediaEditions_asset_1mZMwQ\n  collection {\n    ...useIsRarityEnabled_collection\n    id\n  }\n}\n\nfragment AssetMediaContainer_asset_4a3mm5 on AssetType {\n  backgroundColor\n  ...AssetMediaEditions_asset_1mZMwQ\n  defaultRarityData {\n    ...RarityIndicator_data\n    id\n  }\n  collection {\n    ...useIsRarityEnabled_collection\n    id\n  }\n}\n\nfragment AssetMediaEditions_asset_1mZMwQ on AssetType {\n  decimals\n}\n\nfragment AssetMediaImage_asset on AssetType {\n  backgroundColor\n  imageUrl\n  collection {\n    displayData {\n      cardDisplayStyle\n    }\n    id\n  }\n}\n\nfragment AssetMediaPlaceholderImage_asset on AssetType {\n  collection {\n    displayData {\n      cardDisplayStyle\n    }\n    id\n  }\n}\n\nfragment AssetMediaVideo_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMediaWebgl_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMedia_asset on AssetType {\n  animationUrl\n  displayImageUrl\n  imageUrl\n  isDelisted\n  ...AssetMediaAnimation_asset\n  ...AssetMediaAudio_asset\n  ...AssetMediaContainer_asset_1LNk0S\n  ...AssetMediaImage_asset\n  ...AssetMediaPlaceholderImage_asset\n  ...AssetMediaVideo_asset\n  ...AssetMediaWebgl_asset\n}\n\nfragment AssetMedia_asset_1mZMwQ on AssetType {\n  animationUrl\n  displayImageUrl\n  imageUrl\n  isDelisted\n  ...AssetMediaAnimation_asset\n  ...AssetMediaAudio_asset\n  ...AssetMediaContainer_asset_1LNk0S\n  ...AssetMediaImage_asset\n  ...AssetMediaPlaceholderImage_asset\n  ...AssetMediaVideo_asset\n  ...AssetMediaWebgl_asset\n}\n\nfragment AssetMedia_asset_5MxNd on AssetType {\n  animationUrl\n  displayImageUrl\n  imageUrl\n  isDelisted\n  ...AssetMediaAnimation_asset\n  ...AssetMediaAudio_asset\n  ...AssetMediaContainer_asset_4a3mm5\n  ...AssetMediaImage_asset\n  ...AssetMediaPlaceholderImage_asset\n  ...AssetMediaVideo_asset\n  ...AssetMediaWebgl_asset\n}\n\nfragment AssetQuantity_data on AssetQuantityType {\n  asset {\n    ...Price_data\n    id\n  }\n  quantity\n}\n\nfragment AssetSearchListViewTableAssetInfo_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ...PortfolioTableItemCellTooltip_item\n}\n\nfragment AssetSearchListViewTableQuickBuy_order on OrderV2Type {\n  maker {\n    address\n    id\n  }\n  item {\n    __typename\n    chain {\n      identifier\n    }\n    ...itemEvents_dataV2\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  openedAt\n  relayId\n}\n\nfragment AssetSearchList_data_4hkUTB on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  ...ItemCard_data_1kHswz\n  ... on AssetType {\n    collection {\n      isVerified\n      relayId\n      id\n    }\n  }\n  ... on AssetBundleType {\n    bundleCollection: collection {\n      isVerified\n      relayId\n      id\n    }\n  }\n  chain {\n    identifier\n  }\n  ...useAssetSelectionStorage_item_3j1bgC\n}\n\nfragment BulkPurchaseModal_orders on OrderV2Type {\n  relayId\n  item {\n    __typename\n    relayId\n    chain {\n      identifier\n    }\n    ... on AssetType {\n      collection {\n        slug\n        isSafelisted\n        id\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  payment {\n    relayId\n    symbol\n    id\n  }\n  ...useTotalPrice_orders\n  ...useFulfillingListingsWillReactivateOrders_orders\n}\n\nfragment CancelItemOrdersButton_items on ItemType {\n  __isItemType: __typename\n  __typename\n  chain {\n    identifier\n  }\n  ... on AssetType {\n    relayId\n  }\n  ... on AssetBundleType {\n    relayId\n  }\n  ...CancelOrdersConfirmationModal_items\n}\n\nfragment CancelOrdersConfirmationModal_items on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    ...StackedAssetMedia_assets\n  }\n  ... on AssetBundleType {\n    assetQuantities(first: 18) {\n      edges {\n        node {\n          asset {\n            ...StackedAssetMedia_assets\n            id\n          }\n          id\n        }\n      }\n    }\n  }\n}\n\nfragment CollectionAssetSearchListPagination_data_1eC64m on Query {\n  queriedAt\n  collectionItems(first: $count, collections: $collections, numericTraits: $numericTraits, paymentAssets: $paymentAssets, priceFilter: $priceFilter, querystring: $query, rarityFilter: $rarityFilter, resultType: $resultModel, sortAscending: $sortAscending, sortBy: $sortBy, stringTraits: $stringTraits, toggles: $toggles, owner: $owner, prioritizeBuyNow: true, filterOutListingsWithoutRequestedCreatorFees: $filterOutListingsWithoutRequestedCreatorFees) {\n    edges {\n      node {\n        __typename\n        ...readItemHasBestAsk_item\n        ...AssetSearchList_data_4hkUTB\n        ...useGetEligibleItemsForSweep_items\n        ... on Node {\n          __isNode: __typename\n          id\n        }\n      }\n      cursor\n    }\n    totalCount\n    pageInfo {\n      endCursor\n      hasNextPage\n    }\n  }\n}\n\nfragment CollectionLink_assetContract on AssetContractType {\n  address\n  blockExplorerLink\n}\n\nfragment CollectionLink_collection on CollectionType {\n  name\n  slug\n  verificationStatus\n  ...collection_url\n}\n\nfragment CollectionTrackingContext_collection on CollectionType {\n  relayId\n  slug\n  isVerified\n  isCollectionOffersEnabled\n  defaultChain {\n    identifier\n  }\n}\n\nfragment CreateListingButton_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    ...CreateQuickSingleListingFlowModal_asset\n  }\n  ...itemEvents_dataV2\n  ...item_sellUrl\n}\n\nfragment CreateQuickSingleListingFlowModal_asset on AssetType {\n  relayId\n  chain {\n    identifier\n  }\n  ...itemEvents_dataV2\n}\n\nfragment EditListingButton_item on ItemType {\n  __isItemType: __typename\n  chain {\n    identifier\n  }\n  ...EditListingModal_item\n  ...itemEvents_dataV2\n}\n\nfragment EditListingButton_listing on OrderV2Type {\n  ...EditListingModal_listing\n}\n\nfragment EditListingModal_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    tokenId\n    assetContract {\n      address\n      id\n    }\n    chain {\n      identifier\n    }\n  }\n}\n\nfragment EditListingModal_listing on OrderV2Type {\n  relayId\n}\n\nfragment ItemAddToCartButton_order on OrderV2Type {\n  maker {\n    address\n    id\n  }\n  taker {\n    address\n    id\n  }\n  item {\n    __typename\n    ... on AssetType {\n      isCurrentlyFungible\n    }\n    ...itemEvents_dataV2\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  openedAt\n  ...ShoppingCartContextProvider_inline_order\n}\n\nfragment ItemCardContent on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  ... on AssetType {\n    relayId\n    name\n    ...AssetMedia_asset_1mZMwQ\n  }\n  ... on AssetBundleType {\n    assetQuantities(first: 18) {\n      edges {\n        node {\n          asset {\n            relayId\n            ...AssetMedia_asset\n            id\n          }\n          id\n        }\n      }\n    }\n  }\n}\n\nfragment ItemCardContent_1mZMwQ on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  ... on AssetType {\n    relayId\n    name\n    ...AssetMedia_asset_1mZMwQ\n  }\n  ... on AssetBundleType {\n    assetQuantities(first: 18) {\n      edges {\n        node {\n          asset {\n            relayId\n            ...AssetMedia_asset\n            id\n          }\n          id\n        }\n      }\n    }\n  }\n}\n\nfragment ItemCardCta_item_2qvZ6X on ItemType {\n  __isItemType: __typename\n  __typename\n  orderData {\n    bestAskV2 {\n      ...AddToCartAndQuickBuyButton_order\n      ...EditListingButton_listing\n      ...QuickBuyButton_order\n      id\n    }\n  }\n  ...useItemCardCta_item_2qvZ6X\n  ...itemEvents_dataV2\n  ...CreateListingButton_item\n  ...EditListingButton_item\n}\n\nfragment ItemCardFooter_EmmWh on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  name\n  orderData {\n    bestBidV2 {\n      orderType\n      priceType {\n        unit\n      }\n      ...ItemCardPrice_data\n      id\n    }\n    bestAskV2 {\n      ...ItemCardFooter_bestAskV2\n      id\n    }\n  }\n  ...ItemMetadata_4xFTFU\n  ... on AssetType {\n    tokenId\n    isDelisted\n    defaultRarityData {\n      ...RarityIndicator_data\n      id\n    }\n    collection {\n      slug\n      name\n      isVerified\n      ...collection_url\n      ...useIsRarityEnabled_collection\n      id\n    }\n    largestOwner {\n      owner {\n        ...AccountLink_data\n        id\n      }\n      id\n    }\n    ...AssetSearchListViewTableAssetInfo_item\n  }\n  ... on AssetBundleType {\n    bundleCollection: collection {\n      slug\n      name\n      isVerified\n      ...collection_url\n      ...useIsRarityEnabled_collection\n      id\n    }\n  }\n  ...useItemCardCta_item_2qvZ6X\n  ...item_url\n  ...ItemCardContent\n}\n\nfragment ItemCardFooter_bestAskV2 on OrderV2Type {\n  orderType\n  priceType {\n    unit\n  }\n  maker {\n    address\n    id\n  }\n  ...ItemCardPrice_data\n  ...ItemAddToCartButton_order\n  ...AssetSearchListViewTableQuickBuy_order\n  ...useIsQuickBuyEnabled_order\n}\n\nfragment ItemCardPrice_data on OrderV2Type {\n  perUnitPriceType {\n    unit\n  }\n  payment {\n    symbol\n    id\n  }\n  ...useIsQuickBuyEnabled_order\n}\n\nfragment ItemCard_data_1kHswz on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  chain {\n    identifier\n  }\n  orderData {\n    bestAskV2 {\n      priceType {\n        eth\n      }\n      id\n    }\n  }\n  ... on AssetType {\n    isDelisted\n    totalQuantity\n    collection {\n      slug\n      ...CollectionTrackingContext_collection\n      id\n    }\n    ...itemEvents_data\n  }\n  ... on AssetBundleType {\n    bundleCollection: collection {\n      slug\n      ...CollectionTrackingContext_collection\n      id\n    }\n  }\n  ...ItemCardContent_1mZMwQ\n  ...ItemCardFooter_EmmWh\n  ...ItemCardCta_item_2qvZ6X\n  ...item_url\n  ...ItemTrackingContext_item\n}\n\nfragment ItemMetadata_4xFTFU on ItemType {\n  __isItemType: __typename\n  __typename\n  orderData {\n    bestAskV2 {\n      openedAt\n      createdDate\n      closedAt\n      id\n    }\n  }\n  assetEventData {\n    lastSale {\n      unitPriceQuantity {\n        ...AssetQuantity_data\n        quantity\n        asset {\n          symbol\n          decimals\n          id\n        }\n        id\n      }\n    }\n  }\n  ... on AssetType {\n    bestAllTypeBid @include(if: $shouldShowBestBid) {\n      perUnitPriceType {\n        unit\n        symbol\n      }\n      id\n    }\n    mintEvent @include(if: $shouldShowBestBid) {\n      perUnitPrice {\n        unit\n        symbol\n      }\n      id\n    }\n  }\n}\n\nfragment ItemTrackingContext_item on ItemType {\n  __isItemType: __typename\n  relayId\n  verificationStatus\n  chain {\n    identifier\n  }\n  ... on AssetType {\n    tokenId\n    isReportedSuspicious\n    assetContract {\n      address\n      id\n    }\n  }\n  ... on AssetBundleType {\n    slug\n  }\n}\n\nfragment OrderListItem_order on OrderV2Type {\n  relayId\n  makerOwnedQuantity\n  item {\n    __typename\n    displayName\n    ... on AssetType {\n      assetContract {\n        ...CollectionLink_assetContract\n        id\n      }\n      collection {\n        ...CollectionLink_collection\n        id\n      }\n      ...AssetMedia_asset\n      ...asset_url\n      ...useItemFees_item\n    }\n    ... on AssetBundleType {\n      assetQuantities(first: 30) {\n        edges {\n          node {\n            asset {\n              displayName\n              relayId\n              assetContract {\n                ...CollectionLink_assetContract\n                id\n              }\n              collection {\n                ...CollectionLink_collection\n                id\n              }\n              ...StackedAssetMedia_assets\n              ...AssetMedia_asset\n              ...asset_url\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ...itemEvents_dataV2\n    ...useIsItemSafelisted_item\n    ...ItemTrackingContext_item\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  remainingQuantityType\n  ...OrderPrice\n}\n\nfragment OrderList_orders on OrderV2Type {\n  item {\n    __typename\n    ... on AssetType {\n      __typename\n      relayId\n    }\n    ... on AssetBundleType {\n      __typename\n      assetQuantities(first: 30) {\n        edges {\n          node {\n            asset {\n              relayId\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  relayId\n  ...OrderListItem_order\n  ...useFulfillingListingsWillReactivateOrders_orders\n}\n\nfragment OrderPrice on OrderV2Type {\n  priceType {\n    unit\n  }\n  perUnitPriceType {\n    unit\n  }\n  payment {\n    ...TokenPricePayment\n    id\n  }\n}\n\nfragment PortfolioTableItemCellTooltip_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ...AssetMedia_asset_5MxNd\n  ...PortfolioTableTraitTable_asset\n  ...asset_url\n}\n\nfragment PortfolioTableTraitTable_asset on AssetType {\n  assetContract {\n    address\n    chain\n    id\n  }\n  isCurrentlyFungible\n  tokenId\n}\n\nfragment Price_data on AssetType {\n  decimals\n  symbol\n  usdSpotPrice\n}\n\nfragment ProfileImage_data on AccountType {\n  imageUrl\n}\n\nfragment QuickBuyButton_order on OrderV2Type {\n  maker {\n    address\n    id\n  }\n  taker {\n    address\n    ...wallet_accountKey\n    id\n  }\n  item {\n    __typename\n    chain {\n      identifier\n    }\n    ...itemEvents_dataV2\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  openedAt\n  relayId\n}\n\nfragment RarityIndicator_data on RarityDataType {\n  rank\n  rankPercentile\n  rankCount\n  maxRank\n}\n\nfragment ShoppingCartContextProvider_inline_order on OrderV2Type {\n  relayId\n  makerOwnedQuantity\n  item {\n    __typename\n    chain {\n      identifier\n    }\n    relayId\n    ... on AssetBundleType {\n      assetQuantities(first: 30) {\n        edges {\n          node {\n            asset {\n              relayId\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  maker {\n    relayId\n    id\n  }\n  taker {\n    address\n    ...wallet_accountKey\n    id\n  }\n  priceType {\n    usd\n  }\n  payment {\n    relayId\n    id\n  }\n  remainingQuantityType\n  ...useTotalItems_orders\n  ...ShoppingCart_orders\n}\n\nfragment ShoppingCartDetailedView_orders on OrderV2Type {\n  relayId\n  item {\n    __typename\n    chain {\n      identifier\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  supportsGiftingOnPurchase\n  ...useTotalPrice_orders\n  ...OrderList_orders\n}\n\nfragment ShoppingCart_orders on OrderV2Type {\n  ...ShoppingCartDetailedView_orders\n  ...BulkPurchaseModal_orders\n}\n\nfragment StackedAssetMedia_assets on AssetType {\n  relayId\n  ...AssetMedia_asset\n  collection {\n    logo\n    id\n  }\n}\n\nfragment SweepContextProvider_items on ItemType {\n  __isItemType: __typename\n  relayId\n  orderData {\n    bestAskV2 {\n      relayId\n      payment {\n        symbol\n        id\n      }\n      perUnitPriceType {\n        unit\n      }\n      ...BulkPurchaseModal_orders\n      ...useTotalPrice_orders\n      id\n    }\n  }\n}\n\nfragment TokenPricePayment on PaymentAssetType {\n  symbol\n}\n\nfragment accounts_url on AccountType {\n  address\n  user {\n    publicUsername\n    id\n  }\n}\n\nfragment asset_url on AssetType {\n  assetContract {\n    address\n    id\n  }\n  tokenId\n  chain {\n    identifier\n  }\n}\n\nfragment bundle_url on AssetBundleType {\n  slug\n  chain {\n    identifier\n  }\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n\nfragment itemEvents_data on AssetType {\n  relayId\n  assetContract {\n    address\n    id\n  }\n  tokenId\n  chain {\n    identifier\n  }\n}\n\nfragment itemEvents_dataV2 on ItemType {\n  __isItemType: __typename\n  relayId\n  chain {\n    identifier\n  }\n  ... on AssetType {\n    tokenId\n    assetContract {\n      address\n      id\n    }\n  }\n}\n\nfragment item_sellUrl on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    ...asset_url\n  }\n  ... on AssetBundleType {\n    slug\n    chain {\n      identifier\n    }\n    assetQuantities(first: 18) {\n      edges {\n        node {\n          asset {\n            relayId\n            id\n          }\n          id\n        }\n      }\n    }\n  }\n}\n\nfragment item_url on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    ...asset_url\n  }\n  ... on AssetBundleType {\n    ...bundle_url\n  }\n}\n\nfragment readItemHasBestAsk_item on ItemType {\n  __isItemType: __typename\n  orderData {\n    bestAskV2 {\n      __typename\n      id\n    }\n  }\n}\n\nfragment useAssetSelectionStorage_item_3j1bgC on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  chain {\n    identifier\n    isTradingEnabled\n  }\n  ... on AssetType {\n    bestAllTypeBid @include(if: $shouldShowBestBid) {\n      relayId\n      id\n    }\n    ...asset_url\n    isCompromised\n  }\n  ... on AssetBundleType {\n    orderData {\n      bestBidV2 @include(if: $shouldShowBestBid) {\n        relayId\n        id\n      }\n    }\n  }\n  ...item_sellUrl\n  ...AssetContextMenu_data\n  ...CancelItemOrdersButton_items\n}\n\nfragment useFulfillingListingsWillReactivateOrders_orders on OrderV2Type {\n  ...useTotalItems_orders\n}\n\nfragment useGetEligibleItemsForSweep_items on ItemType {\n  __isItemType: __typename\n  __typename\n  relayId\n  chain {\n    identifier\n  }\n  orderData {\n    bestAskV2 {\n      relayId\n      orderType\n      maker {\n        address\n        id\n      }\n      perUnitPriceType {\n        usd\n        unit\n        symbol\n      }\n      payment {\n        relayId\n        symbol\n        usdPrice\n        id\n      }\n      id\n    }\n  }\n  ...SweepContextProvider_items\n}\n\nfragment useIsItemSafelisted_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    collection {\n      slug\n      verificationStatus\n      id\n    }\n  }\n  ... on AssetBundleType {\n    assetQuantities(first: 30) {\n      edges {\n        node {\n          asset {\n            collection {\n              slug\n              verificationStatus\n              id\n            }\n            id\n          }\n          id\n        }\n      }\n    }\n  }\n}\n\nfragment useIsQuickBuyEnabled_order on OrderV2Type {\n  orderType\n  item {\n    __typename\n    ... on AssetType {\n      isCurrentlyFungible\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n}\n\nfragment useIsRarityEnabled_collection on CollectionType {\n  slug\n  enabledRarities\n}\n\nfragment useItemCardCta_item_2qvZ6X on ItemType {\n  __isItemType: __typename\n  __typename\n  chain {\n    identifier\n    isTradingEnabled\n  }\n  orderData {\n    bestAskV2 {\n      orderType\n      maker {\n        address\n        id\n      }\n      id\n    }\n  }\n  ... on AssetType {\n    isDelisted\n    isListable\n    isCurrentlyFungible\n  }\n}\n\nfragment useItemFees_item on ItemType {\n  __isItemType: __typename\n  __typename\n  ... on AssetType {\n    totalCreatorFee\n    collection {\n      openseaSellerFeeBasisPoints\n      isCreatorFeesEnforced\n      id\n    }\n  }\n  ... on AssetBundleType {\n    bundleCollection: collection {\n      openseaSellerFeeBasisPoints\n      totalCreatorFeeBasisPoints\n      isCreatorFeesEnforced\n      id\n    }\n  }\n}\n\nfragment useTotalItems_orders on OrderV2Type {\n  item {\n    __typename\n    relayId\n    ... on AssetBundleType {\n      assetQuantities(first: 30) {\n        edges {\n          node {\n            asset {\n              relayId\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n}\n\nfragment useTotalPrice_orders on OrderV2Type {\n  relayId\n  perUnitPriceType {\n    usd\n    unit\n  }\n  payment {\n    symbol\n    ...TokenPricePayment\n    id\n  }\n}\n\nfragment wallet_accountKey on AccountType {\n  address\n}\n',
                    'variables': {
                        'collections': [
                            collection,
                        ],
                        'count': 10,
                        'numericTraits': None,
                        'paymentAssets': None,
                        'priceFilter': None,
                        'query': None,
                        'rarityFilter': None,
                        'resultModel': 'ASSETS',
                        'sortAscending': True,
                        'sortBy': 'UNIT_PRICE',
                        'stringTraits': None,
                        'toggles': [
                            'IS_LISTED',
                        ],
                        'shouldShowBestBid': False,
                        'owner': None,
                        'filterOutListingsWithoutRequestedCreatorFees': None,
                    },
                }
                response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post', headers=self.get_headers(account, operation=json_data['id'], auth=auth), payload=json_data, session=session)
                nfts = []
                for nft in response['data']['collectionItems']['edges']:
                    nft = nft['node']
                    if float(nft['orderData']['bestAskV2']['priceType']['eth']) <= 0.0001:
                        nfts.append(nft)
                return random.choice(nfts)
            except:
                time.sleep(i * 1)
        return None

    def get_buy_data(self, account, auth, session, nft_order):

        for i in range(5):
            try:
                json_data = {
                    'id': 'FulfillActionModalQuery',
                    'query': 'query FulfillActionModalQuery(\n  $orderId: OrderRelayID!\n  $itemFillAmount: BigNumberScalar!\n  $takerAssetsForCriteria: ArchetypeInputType\n  $giftRecipientAddress: AddressScalar\n  $optionalCreatorFeeBasisPoints: Int\n) {\n  order(order: $orderId) {\n    relayId\n    side\n    fulfill(itemFillAmount: $itemFillAmount, takerAssetsForCriteria: $takerAssetsForCriteria, giftRecipientAddress: $giftRecipientAddress, optionalCreatorFeeBasisPoints: $optionalCreatorFeeBasisPoints) {\n      actions {\n        __typename\n        ... on FulfillOrderActionType {\n          giftRecipientAddress\n        }\n        ...BlockchainActionList_data\n      }\n    }\n    id\n  }\n}\n\nfragment AskForDepositAction_data on AskForDepositType {\n  asset {\n    chain {\n      identifier\n    }\n    decimals\n    symbol\n    usdSpotPrice\n    id\n  }\n  minQuantity\n}\n\nfragment AskForSwapAction_data on AskForSwapType {\n  __typename\n  fromAsset {\n    chain {\n      identifier\n    }\n    decimals\n    symbol\n    id\n  }\n  toAsset {\n    chain {\n      identifier\n    }\n    symbol\n    id\n  }\n  minQuantity\n  maxQuantity\n  ...useHandleBlockchainActions_ask_for_asset_swap\n}\n\nfragment AssetApprovalAction_data on AssetApprovalActionType {\n  __typename\n  asset {\n    chain {\n      identifier\n    }\n    ...StackedAssetMedia_assets\n    assetContract {\n      ...CollectionLink_assetContract\n      id\n    }\n    collection {\n      __typename\n      ...CollectionLink_collection\n      id\n    }\n    id\n  }\n  ...useHandleBlockchainActions_approve_asset\n}\n\nfragment AssetBurnToRedeemAction_data on AssetBurnToRedeemActionType {\n  __typename\n  ...useHandleBlockchainActions_burnToRedeem\n  asset {\n    chain {\n      identifier\n    }\n    assetContract {\n      ...CollectionLink_assetContract\n      id\n    }\n    collection {\n      __typename\n      ...CollectionLink_collection\n      id\n    }\n    displayName\n    ...StackedAssetMedia_assets\n    id\n  }\n}\n\nfragment AssetFreezeMetadataAction_data on AssetFreezeMetadataActionType {\n  __typename\n  ...useHandleBlockchainActions_freeze_asset_metadata\n}\n\nfragment AssetItem_asset on AssetType {\n  chain {\n    identifier\n  }\n  displayName\n  relayId\n  collection {\n    name\n    id\n  }\n  ...StackedAssetMedia_assets\n}\n\nfragment AssetMediaAnimation_asset on AssetType {\n  ...AssetMediaImage_asset\n  ...AssetMediaContainer_asset\n  ...AssetMediaPlaceholderImage_asset\n}\n\nfragment AssetMediaAudio_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMediaContainer_asset on AssetType {\n  backgroundColor\n  ...AssetMediaEditions_asset_1mZMwQ\n  collection {\n    ...useIsRarityEnabled_collection\n    id\n  }\n}\n\nfragment AssetMediaContainer_asset_1LNk0S on AssetType {\n  backgroundColor\n  ...AssetMediaEditions_asset_1mZMwQ\n  collection {\n    ...useIsRarityEnabled_collection\n    id\n  }\n}\n\nfragment AssetMediaEditions_asset_1mZMwQ on AssetType {\n  decimals\n}\n\nfragment AssetMediaImage_asset on AssetType {\n  backgroundColor\n  imageUrl\n  collection {\n    displayData {\n      cardDisplayStyle\n    }\n    id\n  }\n}\n\nfragment AssetMediaPlaceholderImage_asset on AssetType {\n  collection {\n    displayData {\n      cardDisplayStyle\n    }\n    id\n  }\n}\n\nfragment AssetMediaVideo_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMediaWebgl_asset on AssetType {\n  backgroundColor\n  ...AssetMediaImage_asset\n}\n\nfragment AssetMedia_asset on AssetType {\n  animationUrl\n  displayImageUrl\n  imageUrl\n  isDelisted\n  ...AssetMediaAnimation_asset\n  ...AssetMediaAudio_asset\n  ...AssetMediaContainer_asset_1LNk0S\n  ...AssetMediaImage_asset\n  ...AssetMediaPlaceholderImage_asset\n  ...AssetMediaVideo_asset\n  ...AssetMediaWebgl_asset\n}\n\nfragment AssetSwapAction_data on AssetSwapActionType {\n  __typename\n  ...useHandleBlockchainActions_swap_asset\n}\n\nfragment AssetTransferAction_data on AssetTransferActionType {\n  __typename\n  ...useHandleBlockchainActions_transfer_asset\n}\n\nfragment BlockchainActionList_data on BlockchainActionType {\n  __isBlockchainActionType: __typename\n  __typename\n  ... on AssetApprovalActionType {\n    ...AssetApprovalAction_data\n  }\n  ... on AskForDepositType {\n    __typename\n    ...AskForDepositAction_data\n  }\n  ... on AskForSwapType {\n    __typename\n    ...AskForSwapAction_data\n  }\n  ... on AssetFreezeMetadataActionType {\n    __typename\n    ...AssetFreezeMetadataAction_data\n  }\n  ... on AssetSwapActionType {\n    __typename\n    ...AssetSwapAction_data\n  }\n  ... on AssetTransferActionType {\n    __typename\n    ...AssetTransferAction_data\n  }\n  ... on CreateOrderActionType {\n    __typename\n    ...CreateOrderAction_data\n  }\n  ... on CreateBulkOrderActionType {\n    __typename\n    ...CreateBulkOrderAction_data\n  }\n  ... on CreateSwapOrderActionType {\n    __typename\n    ...CreateSwapOrderAction_data\n  }\n  ... on CancelOrderActionType {\n    __typename\n    ...CancelOrderAction_data\n  }\n  ... on CancelSwapOrdersActionType {\n    __typename\n    ...CancelSwapOrdersAction_data\n  }\n  ... on FulfillOrderActionType {\n    __typename\n    ...FulfillOrderAction_data\n  }\n  ... on FulfillSwapOrderActionType {\n    __typename\n    ...FulfillSwapOrderAction_data\n  }\n  ... on BulkAcceptOffersActionType {\n    __typename\n    ...BulkAcceptOffersAction_data\n  }\n  ... on BulkFulfillOrdersActionType {\n    __typename\n    ...BulkFulfillOrdersAction_data\n  }\n  ... on PaymentAssetApprovalActionType {\n    __typename\n    ...PaymentAssetApprovalAction_data\n  }\n  ... on MintActionType {\n    __typename\n    ...MintAction_data\n  }\n  ... on DropContractDeployActionType {\n    __typename\n    ...DeployContractAction_data\n  }\n  ... on DropMechanicsUpdateActionType {\n    __typename\n    ...UpdateDropMechanicsAction_data\n  }\n  ... on SetCreatorFeesActionType {\n    __typename\n    ...SetCreatorFeesAction_data\n  }\n  ... on CollectionTokenMetadataUpdateActionType {\n    __typename\n    ...UpdatePreRevealAction_data\n  }\n  ... on AssetBurnToRedeemActionType {\n    __typename\n    ...AssetBurnToRedeemAction_data\n  }\n  ... on MintYourOwnCollectionActionType {\n    __typename\n    ...MintYourOwnCollectionAction_data\n  }\n}\n\nfragment BulkAcceptOffersAction_data on BulkAcceptOffersActionType {\n  __typename\n  maxQuantityToFill\n  offersToAccept {\n    itemFillAmount\n    orderData {\n      chain {\n        identifier\n      }\n      item {\n        __typename\n        ... on AssetQuantityDataType {\n          asset {\n            ...StackedAssetMedia_assets\n            id\n          }\n        }\n        ... on AssetBundleType {\n          assetQuantities(first: 30) {\n            edges {\n              node {\n                asset {\n                  ...StackedAssetMedia_assets\n                  id\n                }\n                id\n              }\n            }\n          }\n        }\n        ... on Node {\n          __isNode: __typename\n          id\n        }\n      }\n      ...useTotalItems_ordersData\n    }\n    criteriaAsset {\n      relayId\n      ...StackedAssetMedia_assets\n      id\n    }\n    ...useTotalPriceOfferDataToAccept_offersToAccept\n    ...readOfferDataToAcceptPrice_offerToAccept\n  }\n  ...useHandleBlockchainActions_bulk_accept_offers\n}\n\nfragment BulkFulfillOrdersAction_data on BulkFulfillOrdersActionType {\n  __typename\n  maxOrdersToFill\n  ordersToFill {\n    itemFillAmount\n    orderData {\n      chain {\n        identifier\n      }\n      item {\n        __typename\n        ... on AssetQuantityDataType {\n          asset {\n            ...StackedAssetMedia_assets\n            id\n          }\n        }\n        ... on AssetBundleType {\n          assetQuantities(first: 30) {\n            edges {\n              node {\n                asset {\n                  ...StackedAssetMedia_assets\n                  id\n                }\n                id\n              }\n            }\n          }\n        }\n        ... on Node {\n          __isNode: __typename\n          id\n        }\n      }\n      ...useTotalItems_ordersData\n    }\n    ...useTotalPriceOrderDataToFill_ordersToFill\n    ...readOrderDataToFillPrices_orderDataToFill\n  }\n  ...useHandleBlockchainActions_bulk_fulfill_orders\n}\n\nfragment CancelOrderActionGaslessContent_action on CancelOrderActionType {\n  ordersData {\n    side\n    orderType\n    item {\n      __typename\n      ... on AssetQuantityDataType {\n        asset {\n          displayName\n          ...StackedAssetMedia_assets\n          id\n        }\n      }\n      ... on Node {\n        __isNode: __typename\n        id\n      }\n    }\n    price {\n      unit\n      symbol\n    }\n    orderCriteria {\n      collection {\n        name\n        representativeAsset {\n          ...StackedAssetMedia_assets\n          id\n        }\n        id\n      }\n    }\n  }\n}\n\nfragment CancelOrderActionOnChainContent_action on CancelOrderActionType {\n  ordersData {\n    side\n    orderType\n    ...OrderDataHeader_order\n    ...OrdersHeaderData_orders\n  }\n}\n\nfragment CancelOrderAction_data on CancelOrderActionType {\n  __typename\n  ordersData {\n    orderType\n    side\n    item {\n      __typename\n      ... on AssetQuantityDataType {\n        asset {\n          ...GaslessCancellationProcessingModal_items\n          ...GaslessCancellationFailedModal_items\n          id\n        }\n        quantity\n      }\n      ... on Node {\n        __isNode: __typename\n        id\n      }\n    }\n    orderCriteria {\n      collection {\n        representativeAsset {\n          ...GaslessCancellationProcessingModal_items\n          ...GaslessCancellationFailedModal_items\n          id\n        }\n        id\n      }\n      quantity\n    }\n  }\n  method {\n    __typename\n  }\n  ...CancelOrderActionOnChainContent_action\n  ...useHandleBlockchainActions_cancel_orders\n  ...CancelOrderActionGaslessContent_action\n}\n\nfragment CancelSwapOrdersAction_data on CancelSwapOrdersActionType {\n  __typename\n  swapsData {\n    ...SwapDataHeader_swap\n  }\n  ...useHandleBlockchainActions_cancel_swap_orders\n}\n\nfragment CollectionLink_assetContract on AssetContractType {\n  address\n  blockExplorerLink\n}\n\nfragment CollectionLink_collection on CollectionType {\n  name\n  slug\n  verificationStatus\n  ...collection_url\n}\n\nfragment CollectionOfferDetails_collection on CollectionType {\n  representativeAsset {\n    assetContract {\n      ...CollectionLink_assetContract\n      id\n    }\n    ...StackedAssetMedia_assets\n    id\n  }\n  ...CollectionLink_collection\n}\n\nfragment ConfirmationItem_asset on AssetType {\n  chain {\n    displayName\n  }\n  ...AssetItem_asset\n}\n\nfragment ConfirmationItem_asset_item_payment_asset on PaymentAssetType {\n  ...ConfirmationItem_extra_payment_asset\n}\n\nfragment ConfirmationItem_assets on AssetType {\n  ...ConfirmationItem_asset\n}\n\nfragment ConfirmationItem_extra_payment_asset on PaymentAssetType {\n  symbol\n  usdSpotPrice\n}\n\nfragment ConfirmationItem_payment_asset on PaymentAssetType {\n  ...ConfirmationItem_asset_item_payment_asset\n}\n\nfragment CreateBulkOrderAction_data on CreateBulkOrderActionType {\n  __typename\n  orderDatas {\n    item {\n      __typename\n      ... on AssetQuantityDataType {\n        asset {\n          ...StackedAssetMedia_assets\n          id\n        }\n      }\n      ... on Node {\n        __isNode: __typename\n        id\n      }\n    }\n    ...useTotalItems_ordersData\n    ...useTotalPriceOrderData_orderData\n  }\n  ...useHandleBlockchainActions_create_bulk_order\n}\n\nfragment CreateOrderAction_data on CreateOrderActionType {\n  __typename\n  orderData {\n    item {\n      __typename\n      ... on AssetQuantityDataType {\n        quantity\n      }\n      ... on Node {\n        __isNode: __typename\n        id\n      }\n    }\n    side\n    isCounterOrder\n    perUnitPrice {\n      unit\n      symbol\n    }\n    ...OrderDataHeader_order\n  }\n  ...useHandleBlockchainActions_create_order\n}\n\nfragment CreateSwapOrderAction_data on CreateSwapOrderActionType {\n  __typename\n  swapData {\n    ...SwapDataHeader_swap\n  }\n  ...useHandleBlockchainActions_create_swap_order\n}\n\nfragment DeployContractAction_data on DropContractDeployActionType {\n  __typename\n  ...useHandleBlockchainActions_deploy_contract\n}\n\nfragment FulfillOrderAction_data on FulfillOrderActionType {\n  __typename\n  orderData {\n    side\n    ...OrderDataHeader_order\n  }\n  itemFillAmount\n  criteriaAsset {\n    ...OrderDataHeader_criteriaAsset\n    id\n  }\n  ...useHandleBlockchainActions_fulfill_order\n}\n\nfragment FulfillSwapOrderAction_data on FulfillSwapOrderActionType {\n  __typename\n  swapData {\n    ...SwapDataHeader_swap\n  }\n  ...useHandleBlockchainActions_fulfill_swap_order\n}\n\nfragment GaslessCancellationFailedModal_items on ItemType {\n  __isItemType: __typename\n  ...StackedAssetMedia_assets\n}\n\nfragment GaslessCancellationProcessingModal_items on ItemType {\n  __isItemType: __typename\n  ...StackedAssetMedia_assets\n}\n\nfragment MintAction_data on MintActionType {\n  __typename\n  ...useHandleBlockchainActions_mint_asset\n}\n\nfragment MintYourOwnCollectionAction_data on MintYourOwnCollectionActionType {\n  __typename\n  ...useHandleBlockchainActions_mint_your_own_collection\n}\n\nfragment OrderDataHeader_criteriaAsset on AssetType {\n  ...ConfirmationItem_assets\n}\n\nfragment OrderDataHeader_order on OrderDataType {\n  item {\n    __typename\n    ... on AssetQuantityDataType {\n      asset {\n        ...ConfirmationItem_assets\n        id\n      }\n      quantity\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  recipient {\n    address\n    id\n  }\n  side\n  openedAt\n  closedAt\n  perUnitPrice {\n    unit\n  }\n  price {\n    unit\n    symbol\n    usd\n  }\n  payment {\n    ...ConfirmationItem_payment_asset\n    id\n  }\n  englishAuctionReservePrice {\n    unit\n  }\n  isCounterOrder\n  orderCriteria {\n    collection {\n      ...CollectionOfferDetails_collection\n      id\n    }\n    trait {\n      traitType\n      value\n      id\n    }\n    quantity\n  }\n}\n\nfragment OrdersHeaderData_orders on OrderDataType {\n  chain {\n    identifier\n  }\n  item {\n    __typename\n    ... on AssetQuantityDataType {\n      asset {\n        ...StackedAssetMedia_assets\n        id\n      }\n    }\n    ... on AssetBundleType {\n      assetQuantities(first: 20) {\n        edges {\n          node {\n            asset {\n              ...StackedAssetMedia_assets\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ... on AssetBundleToBeCreatedType {\n      assetQuantitiesToBeCreated: assetQuantities {\n        asset {\n          ...StackedAssetMedia_assets\n          id\n        }\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n  orderCriteria {\n    collection {\n      representativeAsset {\n        ...StackedAssetMedia_assets\n        id\n      }\n      id\n    }\n  }\n  orderType\n  side\n}\n\nfragment PaymentAssetApprovalAction_data on PaymentAssetApprovalActionType {\n  __typename\n  asset {\n    chain {\n      identifier\n    }\n    symbol\n    ...StackedAssetMedia_assets\n    id\n  }\n  ...useHandleBlockchainActions_approve_payment_asset\n}\n\nfragment SetCreatorFeesAction_data on SetCreatorFeesActionType {\n  __typename\n  ...useHandleBlockchainActions_set_creator_fees\n}\n\nfragment StackedAssetMedia_assets on AssetType {\n  relayId\n  ...AssetMedia_asset\n  collection {\n    logo\n    id\n  }\n}\n\nfragment SwapDataHeader_swap on SwapDataType {\n  maker {\n    address\n    displayName\n    id\n  }\n  taker {\n    address\n    displayName\n    id\n  }\n  makerAssets {\n    asset {\n      chain {\n        identifier\n      }\n      id\n    }\n    ...SwapDataSide_assets\n  }\n  takerAssets {\n    ...SwapDataSide_assets\n  }\n}\n\nfragment SwapDataSide_assets on AssetQuantityDataType {\n  asset {\n    relayId\n    displayName\n    symbol\n    assetContract {\n      tokenStandard\n      id\n    }\n    ...StackedAssetMedia_assets\n    id\n  }\n  quantity\n}\n\nfragment TokenPricePayment on PaymentAssetType {\n  symbol\n}\n\nfragment UpdateDropMechanicsAction_data on DropMechanicsUpdateActionType {\n  __typename\n  ...useHandleBlockchainActions_update_drop_mechanics\n}\n\nfragment UpdatePreRevealAction_data on CollectionTokenMetadataUpdateActionType {\n  __typename\n  ...useHandleBlockchainActions_update_drop_pre_reveal\n}\n\nfragment collection_url on CollectionType {\n  slug\n  isCategory\n}\n\nfragment readOfferDataToAcceptPerUnitPrice_offerToAccept on OfferToAcceptType {\n  orderData {\n    perUnitPrice {\n      usd\n      unit\n    }\n    payment {\n      ...TokenPricePayment\n      id\n    }\n  }\n}\n\nfragment readOfferDataToAcceptPrice_offerToAccept on OfferToAcceptType {\n  orderData {\n    perUnitPrice {\n      usd\n      unit\n    }\n    payment {\n      ...TokenPricePayment\n      id\n    }\n  }\n  itemFillAmount\n}\n\nfragment readOrderDataPrices on OrderDataType {\n  perUnitPrice {\n    usd\n    unit\n  }\n  payment {\n    ...TokenPricePayment\n    id\n  }\n  item {\n    __typename\n    ... on AssetQuantityDataType {\n      quantity\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n}\n\nfragment readOrderDataToFillPrices_orderDataToFill on OrderToFillType {\n  orderData {\n    perUnitPrice {\n      usd\n      unit\n    }\n    payment {\n      ...TokenPricePayment\n      id\n    }\n  }\n  itemFillAmount\n}\n\nfragment useHandleBlockchainActions_approve_asset on AssetApprovalActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_approve_payment_asset on PaymentAssetApprovalActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_ask_for_asset_swap on AskForSwapType {\n  fromAsset {\n    decimals\n    relayId\n    id\n  }\n  toAsset {\n    relayId\n    id\n  }\n}\n\nfragment useHandleBlockchainActions_bulk_accept_offers on BulkAcceptOffersActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n  offersToAccept {\n    orderData {\n      openedAt\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_bulk_fulfill_orders on BulkFulfillOrdersActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n  ordersToFill {\n    orderData {\n      openedAt\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_burnToRedeem on AssetBurnToRedeemActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_cancel_orders on CancelOrderActionType {\n  method {\n    __typename\n    ... on TransactionSubmissionDataType {\n      ...useHandleBlockchainActions_transaction\n    }\n    ... on SignAndPostOrderCancelType {\n      cancelOrderData: data {\n        payload\n        message\n      }\n      serverSignature\n      clientSignatureStandard\n    }\n    ... on GaslessCancelType {\n      orderRelayIds\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_cancel_swap_orders on CancelSwapOrdersActionType {\n  method {\n    __typename\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_create_bulk_order on CreateBulkOrderActionType {\n  method {\n    clientMessage\n    clientSignatureStandard\n    serverSignature\n    orderDatas\n    chain {\n      identifier\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_create_order on CreateOrderActionType {\n  method {\n    clientMessage\n    clientSignatureStandard\n    serverSignature\n    orderData\n    chain {\n      identifier\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_create_swap_order on CreateSwapOrderActionType {\n  method {\n    clientMessage\n    clientSignatureStandard\n    serverSignature\n    swapData\n    chain {\n      identifier\n    }\n  }\n}\n\nfragment useHandleBlockchainActions_deploy_contract on DropContractDeployActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_freeze_asset_metadata on AssetFreezeMetadataActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_fulfill_order on FulfillOrderActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n  orderData {\n    openedAt\n  }\n}\n\nfragment useHandleBlockchainActions_fulfill_swap_order on FulfillSwapOrderActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n  swapData {\n    openedAt\n  }\n}\n\nfragment useHandleBlockchainActions_mint_asset on MintActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n  startTime\n}\n\nfragment useHandleBlockchainActions_mint_your_own_collection on MintYourOwnCollectionActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_set_creator_fees on SetCreatorFeesActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_swap_asset on AssetSwapActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_transaction on TransactionSubmissionDataType {\n  chain {\n    identifier\n  }\n  ...useTransaction_transaction\n}\n\nfragment useHandleBlockchainActions_transfer_asset on AssetTransferActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_update_drop_mechanics on DropMechanicsUpdateActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useHandleBlockchainActions_update_drop_pre_reveal on CollectionTokenMetadataUpdateActionType {\n  method {\n    ...useHandleBlockchainActions_transaction\n  }\n}\n\nfragment useIsRarityEnabled_collection on CollectionType {\n  slug\n  enabledRarities\n}\n\nfragment useTotalItems_ordersData on OrderDataType {\n  item {\n    __typename\n    ... on AssetQuantityDataType {\n      asset {\n        relayId\n        id\n      }\n    }\n    ... on AssetBundleType {\n      assetQuantities(first: 30) {\n        edges {\n          node {\n            asset {\n              relayId\n              id\n            }\n            id\n          }\n        }\n      }\n    }\n    ... on Node {\n      __isNode: __typename\n      id\n    }\n  }\n}\n\nfragment useTotalPriceOfferDataToAccept_offersToAccept on OfferToAcceptType {\n  itemFillAmount\n  ...readOfferDataToAcceptPerUnitPrice_offerToAccept\n}\n\nfragment useTotalPriceOrderDataToFill_ordersToFill on OrderToFillType {\n  ...readOrderDataToFillPrices_orderDataToFill\n}\n\nfragment useTotalPriceOrderData_orderData on OrderDataType {\n  ...readOrderDataPrices\n}\n\nfragment useTransaction_transaction on TransactionSubmissionDataType {\n  chain {\n    identifier\n  }\n  source {\n    value\n  }\n  destination {\n    value\n  }\n  value\n  data\n}\n',
                    'variables': {
                        'orderId': nft_order,
                        'itemFillAmount': '1',
                        'takerAssetsForCriteria': None,
                        'giftRecipientAddress': None,
                        'optionalCreatorFeeBasisPoints': None,
                    },
                }
                response = self.helper.fetch_tls(url='https://opensea.io/__api/graphql/', type='post', headers=self.get_headers(account, operation=json_data['id'], auth=auth), payload=json_data, session=session)
                return response['data']['order']['fulfill']['actions'][0]['method']
            except:
                time.sleep(i * 1)
        return None

    def main(self, chain_from, private_key, attempt=0):

        if attempt > 15:
            return 'error'

        account = self.w3.eth.account.from_key(private_key)

        session = self.helper.get_tls_session()

        auth = self.get_auth(account, session)
        if not auth:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        collections = self.get_collections(account, auth, session, chain_from)
        if len(collections) == 0:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        collection = random.choice(collections)
        nft = self.get_nfts(account, auth, session, collection['slug'])
        if not nft:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        order_data = self.get_buy_data(account, auth, session, nft['orderData']['bestAskV2']['relayId'])
        if not order_data:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        tx = make_tx(self.w3, account, value=int(order_data['value']), to=order_data['destination']['value'], data=order_data['data'])
        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        if chain_from == 'ETH' and int(tx['gas']) > 500000:
            return self.main(chain_from=chain_from, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, chain_from=chain_from, attempt=attempt+1)

        self.logger.log_success(f"WARMUP-{chain_from} ({self.project}) | Успешно купил NFT ({collection['name']}) за {nft['orderData']['bestAskV2']['priceType']['eth']} ETH",wallet=account.address)
        return self.w3.to_hex(hash)

class Warmup():

    def __init__(self, w3, logger, helper, turned_warmups):
        self.project = 'WARMUP'
        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.chain_actions_dict = {
            'ETH': {
                'MINTFUN': Mintfun,
                'LIDO': Lido,
                'OPTIMISM': Optimismbridge,
                'ARBITRUM': Arbitrumbridge,
                'POLYGON': Polygonbridge,
                'AAVE': Aave,
                'RADIANT': Radiant,
                'APPROVE': Approve,
                '1INCH': Inch,
                'UNISWAP': Uniswap,
                'SUSHISWAP': Sushiswap,
                'WRAPPER': Wrapper,
                'ZORA': Zora,
                'STARKNET': Starknet,
                'BLUR': Blur,
                'MIRROR': Mirror,
                'OKXNFT': OkxNFT,
                'TOFUNFT': TofuNFT,
                'ELEMENTNFT': ElementNFT,
                'OPENSEANFT': OpenseaNFT,
            },
            'OPT': {
                'MINTFUN': Mintfun,
                'AAVE': Aave,
                'APPROVE': Approve,
                'UNISWAP': Uniswap,
                'SUSHISWAP': Sushiswap,
                '1INCH': Inch,
                'WRAPPER': Wrapper,
                'MIRROR': Mirror,
                'OPTIMISM': Optimismbridge,
                'OKXNFT': OkxNFT,
                'OPENSEANFT': OpenseaNFT,
            },
            'ARB': {
                'ARBITRUM': Arbitrumbridge,
                'AAVE': Aave,
                'RADIANT': Radiant,
                'APPROVE': Approve,
                'UNISWAP': Uniswap,
                '1INCH': Inch,
                'SUSHISWAP': Sushiswap,
                'WRAPPER': Wrapper,
                'OKXNFT': OkxNFT,
                'TOFUNFT': TofuNFT,
                'ELEMENTNFT': ElementNFT,
                'OPENSEANFT': OpenseaNFT,
            }
        }
        self.turned_warmups = turned_warmups
        self.action_method_name = 'main'

    def get_action_objects(self, chain_from, action_names, new_w3):
        chain_objects_dict = self.chain_actions_dict.get(chain_from, {})
        return [chain_objects_dict[name](new_w3, self.logger, self.helper) for name in action_names if name in chain_objects_dict]

    def main(self, chain_from, wallet_data):

        if wallet_data.get('proxy', None):
            new_w3 = self.helper.get_web3(wallet_data['proxy'], self.w3[chain_from])
        else:
            new_w3 = self.w3[chain_from]

        private_key = wallet_data['private_key']

        action_names = self.turned_warmups.get(chain_from, [])
        action_objects = self.get_action_objects(chain_from, action_names, new_w3)


        if not action_objects:
            self.logger.warning(f"{self.project} | Не выбрано ни одного модуля для сети - {chain_from}, пропускаю")
            return None

        available_actions = [lambda action=action: action.main(chain_from, private_key) for action in action_objects]

        action = random.choice(available_actions)
        return action()
