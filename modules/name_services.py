import string
from helpers.utils import *
from helpers.data import lns_data
from web3._utils.contracts import encode_abi
from Crypto.Hash import keccak
from eth_account.messages import encode_defunct

def generate_name(min_length=7):
    prefixes = ['sync', 'zk','crypto', 'block', 'decentral', 'eth', 'token', 'dapp', 'net', 'chain', 'coin', 'web', 'tech', 'fin', 'quant',
                'ledger', 'bit', 'quantum', 'trust', 'smart', 'solid', 'relay', 'peer', 'origin', 'node', 'flash', 'cipher', 'cloud',
                'pepe', 'degen', 'lord', 'vitalik', 'sam', 'gem', 'pump', 'dump', 'crypt', 'eth', 'moon', 'hodl', 'whale', 'fud', 'fomo', 'tothemoon',
                'bagholder', 'nft', 'shill', 'satoshi', 'miner', 'gas', 'defi', 'staking', 'yield', 'fiat', 'ledger', 'wallet', 'oracle',
                'magic', 'unicorn', 'cyber', 'pixie', 'galactic', 'quantum', 'rainbow', 'kryptonite', 'space', 'time']
    suffixes = ['sync', 'zk', 'hub', 'zone', 'network', 'platform', 'base', 'world', 'pro', 'tech', 'app', 'link', 'gate', 'space', 'void',
                'vault', 'wave', 'port', 'path', 'cast', 'grid', 'core', 'shift', 'pulse', 'flow', 'arc', 'sphere', 'byte',
                'gem', 'pump', 'dump', 'crypt', 'eth', 'pepe', 'degen', 'lord', 'warp', 'spire', 'twist', 'echo', 'riddle', 'puzzle', 'dream',
                'saga', 'tales', 'dao', 'labs', 'forge', 'protocol', 'studio', 'collective', "degen", 'pro']
    names = ['john', 'alice', 'mike', 'sarah', 'lucas', 'emily', 'ethan', 'mia', 'ryan', 'zoe', 'leo', 'olivia', 'liam', 'emma',
             'max', 'sophia', 'alex', 'ava', 'ben', 'claire', 'david', 'ella', 'frank', 'grace', 'harry', 'iris', 'elon', 'vader', 'kenobi',
             'leia', 'hann', 'morpheus', 'neo', 'gollum', 'frodo', 'lana', 'oscar', 'tina', 'uma', 'victor', 'wendy', 'xander', 'yara', 'zane', 'quinn']
    surnames = ['doe', 'smith', 'jones', 'brown', 'johnson', 'evans', 'patel', 'miller', 'cooper', 'white', 'hall', 'clarke', 'wright', 'green',
                'ross', 'taylor', 'campbell', 'walker', 'baker', 'adams', 'nelson', 'hill', 'andrews', 'king', 'turner',  'blockford', 'ledgerson',
                'cryptman', 'defield', 'moonwright', 'gastings', 'satoson', 'chainwell', 'stakely', 'yieldmore', 'stardust', 'rockwell', 'pixelton',
                'novastar', 'glitch', 'nebula', 'vortex', 'quark', 'galax', 'cosmon']

    templates = [
        "{prefix}{name}{surname}",
        "{name}{suffix}",
        "{name}{random_string}{surname}",
        "{prefix}{random_string}{suffix}",
        "{prefix}{name}",
        "{surname}{suffix}",
        "{prefix}{surname}",
        "{name}{random_string}",
        "{surname}{random_string}",
        "{prefix}{random_string}",
        "{prefix}{suffix}",
        "{name}{surname}{suffix}",
        "{name}-{suffix}",
        "{prefix}-{name}",
        "{prefix}-{surname}"
    ]

    def random_capitalize(word):
        return word.capitalize() if random.choice([True, False]) else word

    def maybe_insert_number(word):
        return word + str(random.randint(0,9)) if random.choice([True, False]) else word

    attempts = 0
    while True:
        chosen_template = random.choice(templates)
        random_string_length = random.randint(1, 5)
        random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random_string_length))
        name = chosen_template.format(
            prefix=maybe_insert_number(random_capitalize(random.choice(prefixes))),
            name=maybe_insert_number(random_capitalize(random.choice(names))),
            surname=maybe_insert_number(random_capitalize(random.choice(surnames))),
            random_string=random_string,
            suffix=maybe_insert_number(random_capitalize(random.choice(suffixes)))
        )
        if len([char for char in name if char.isdigit()]) <= 1 and len(name) >= min_length:
            break
        attempts += 1
        if attempts >= 100:
            break

    return name

#0.0025 ETH
class Lin():

    def __init__(self, w3, logger, settings, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'LIN'
        self.price = 0.0026
        self.logger = logger
        self.contract = self.w3.eth.contract(self.w3.to_checksum_address(lns_data[self.project]['contract']), abi=lns_data[self.project]['ABI'])
        self.settings = settings

    def set_name(self, account, private_key, new_w3):

        try:
            tokens = self.contract.functions.walletOfOwnerName(account.address).call()
        except:
            return 'no_route'

        token = random.choice(tokens)
        name = token.replace('.bns', '')

        func_ = getattr(self.contract.functions, 'setPrimaryAddress')

        tx = make_tx(new_w3, account, func=func_, args=name, args_positioning=False)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.domain(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно поставил имя {name}.bns в качестве основного', wallet=account.address)
        return new_w3.to_hex(hash)

    def domain(self, private_key, attempt = 0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        try:
            balance = int(self.contract.functions.balanceOf(account.address).call())
        except:
            return self.domain(private_key=private_key, attempt = attempt+1)
        if balance > 0 and self.settings['multiple_domains'] is False:
            return self.set_name(account, private_key, new_w3)

        name = generate_name(min_length=6).lower()

        args = name, new_w3.to_checksum_address('0x5f67ffa4b3f77dd16c9c34a1a82cab8daea03191')

        self.logger.log(f'{self.project} | Регистрирую имя {name}.bns', wallet=account.address)

        func_ = getattr(self.contract.functions, 'Register')
        tx = make_tx(new_w3, account, value=int(0.0025 * 10 ** 18), func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.domain(private_key=private_key, attempt=attempt+1)
        self.logger.log_success(f'{self.project} | Успешно зарегистрировал имя {name}.bns за 0.0025 ETH', wallet=account.address)
        return new_w3.to_hex(hash)

#0.0031 ETH
class Lineans():
    def __init__(self, w3, logger, settings, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'LINEANS'
        self.logger = logger
        self.price = 0.0033
        self.contract = self.w3.eth.contract(self.w3.to_checksum_address(lns_data[self.project]['contract']),abi=lns_data[self.project]['ABI'])
        self.contract_sub = self.w3.eth.contract(self.w3.to_checksum_address(lns_data[self.project]['contract_sub']), abi=lns_data[self.project]['ABI_sub'])
        self.contract_domain = self.w3.eth.contract(self.w3.to_checksum_address(lns_data[self.project]['contract_domain']), abi=lns_data[self.project]['ABI_domain'])
        self.settings = settings

    def get_sub(self, account, balance, private_key):

        #token = random.choice(balance)
        sub_domen = generate_name(min_length=0).lower()
        node = self.contract_sub.functions.getNode('defi5zane.linea').call()
        print(node.hex())
        print(self.contract_sub.functions)
        args = '0x0d2ba586d129f5a918def00f030a7a3b5948dcbc4fbecc4c057f20eccf2f36a0', sub_domen, 'defi5zane.linea', account.address, self.w3.to_checksum_address('0xaEde002BbBE985DdaBD208FdFd80Fa6d7b97B9d1')

        func_ = getattr(self.contract_sub.functions, 'setSubnodeRecord')

        tx = make_tx(self.w3, account, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = self.w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(self.w3, hash)
        if not tx_status:
            return self.domain(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно сделал сабдомен ({sub_domen}) для домена {token[2]}', wallet=account.address)
        return self.w3.to_hex(hash)

    def domain(self, private_key, attempt = 0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        balance = self.contract_domain.functions.balanceOf(account.address).call()

        if balance > 0 and self.settings['multiple_domains'] is False:
            return 'no_route'#self.get_sub(account, balance, private_key)

        while True:
            name = generate_name(min_length=7).lower()
            available = self.contract.functions.isNameAvailable(name, 'linea').call()
            if available:
                break

        duration = 60 * 60 * 24 * 365
        args = name, account.address, duration, 'linea', new_w3.to_checksum_address('0xaEde002BbBE985DdaBD208FdFd80Fa6d7b97B9d1'), account.address, '0x0000000000000000000000000000000000000000000000000000000000000000'

        self.logger.log(f'{self.project} | Регистрирую имя {name}.base', wallet=account.address)

        price = self.contract.functions.getCost(name, duration).call()
        func_ = getattr(self.contract.functions, 'directRegister')
        tx = make_tx(new_w3, account, value=int(price), func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.domain(private_key=private_key, attempt=attempt+1)
        self.logger.log_success(f'{self.project} | Успешно зарегистрировал имя {name}.base за {price / (10 ** 18)} ETH', wallet=account.address)
        return new_w3.to_hex(hash)

#FREE
class Openname():

    def __init__(self, w3, logger, settings, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'OPENNAME'
        self.price = 0
        self.logger = logger
        self.contract = self.w3.eth.contract(self.w3.to_checksum_address(lns_data[self.project]['contract']),abi=lns_data[self.project]['ABI'])
        self.settings = settings
        self.prefixes = [
            "shib", "pepe", "duo", "web3.0", "hiroba", "block", "pizza",
            "open", "ai", "game", "pay", "cat", "doll", "money", "summer",
            "ethereum", "coffee", "verse", "avax", "play", "matic", "metaverse",
            "🚀", "💎", "gas", "❤️", "👽", "wtf", "newyork", "bibi", "서울", "東京",
            "london", "expelliarmus", "barbie", "ザ"
        ]

    def get_headers(self, auth=None):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://app.open.name',
            'Referer': 'https://app.open.name/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        if auth:
            headers['Authorization'] = f'Bearer {auth}'
        return headers

    def get_auth(self, account, chain=59144):
        for i in range(5):
            try:
                message = f"{account.address}".encode()
                message_to_sign = encode_defunct(primitive=message)
                signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
                sig = signed_message.signature.hex()
                payload = {"msg":account.address,"signedMessage":sig,"chainId":chain,"ip":"","ipDetail":"","os":"Win10","divice":"windows","browser":"chrome","inviteCode":"","walletType":1}
                res = self.help.fetch_url(url='https://app.open.name/api/v1/auth/login', type='post', payload=payload, headers=self.get_headers())
                return res['data']
            except:
                time.sleep(1*i)
        return None

    def request_data(self, name, auth, chain=59144):
        for i in range(5):
            try:
                payload = {"chainId":chain,"gToken":"","inviteCode":"","couponIds":[],"names":[{"name":name,"periodType":0,"num":1}]}
                res = self.help.fetch_url(url='https://app.open.name/api/v1/domain/sign', type='post', payload=payload, headers=self.get_headers(auth))

                return res['data']
            except:
                time.sleep(1*i)
        return None

    def domain(self, private_key, attempt = 0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        name = generate_name(min_length=7).lower()

        auth = self.get_auth(account)
        if not auth:
            return self.domain(private_key=private_key, attempt = attempt + 1)
        prefix = random.choice(self.prefixes)
        data = self.request_data(f"{name}.{prefix}", auth['access_token'])
        if not data:
            return self.domain(private_key=private_key, attempt = attempt + 1)
        pay_value = int(data['payValue'])
        sign_func = self.contract.functions.sign(data['signature'], data['contents'], data['commissions'])
        sign_data = encode_abi(new_w3, sign_func.abi, [data['signature'], data['contents'], data['commissions']])

        data = f"0xd4380353{sign_data[2:]}"

        self.logger.log(f'{self.project} | Регистрирую имя {name}.{prefix} за {round(pay_value/(10**18), 6)} ETH', wallet=account.address)

        tx = make_tx(new_w3, account, value=pay_value, data=data, to=lns_data[self.project]['contract'])
        if tx == "low_native" or not tx:
            return self.domain(private_key=private_key, attempt = attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.domain(private_key=private_key, attempt=attempt+1)
        self.logger.log_success(f'{self.project} | Успешно зарегистрировал имя {name}.{prefix} за {round(pay_value/(10**18), 6)} ETH', wallet=account.address)
        return new_w3.to_hex(hash)


def initialize_name_services(classes_to_init, w3, logger, settings, helper):
    available_swaps = {
        "Openname": Openname,
        'Lineans': Lineans,
        'Lin': Lin,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, logger, settings, helper)

    return initialized_objects

