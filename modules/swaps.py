from helpers.utils import *
from helpers.data import tokens_data_, NULL_ADDRESS
from eth_abi import *
import json

#NO
class Odos():
    def __init__(self, w3, max_slip, helper):
        self.project = 'ODOS'
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
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from, token_to, account):
        for i in range(5):
            payload = {
                        'chainId': 59144,
                        'inputTokens': [
                            {
                                'tokenAddress': "0x0000000000000000000000000000000000000000" if token_from == "ETH" else self.available_tokens[token_from]['address'],
                                'amount': str(int(amount*10**18)) if token_from == "ETH" else str(int(amount*10**int(self.available_tokens[token_from]['decimal']))),
                            },
                        ],
                        'outputTokens': [
                            {
                                'tokenAddress': "0x0000000000000000000000000000000000000000" if token_to == "ETH" else self.available_tokens[token_to]['address'],
                                'proportion': 1,
                            },
                        ],
                        'gasPrice': 0.25,
                        'userAddr': account.address,
                        'slippageLimitPercent': 1,
                        'sourceBlacklist': [],
                        'pathViz': True,
                        'referralCode': 3069696969,
                        'compact': True,
                        'likeAsset': False,
                    }
            try:
                result = self.help.fetch_url(url='https://api.odos.xyz/sor/quote/v2', type='post', payload=payload, headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return {}

    def swap_requsets(self, path_id, account):
        for i in range(5):
            try:
                payload = {"userAddr":account.address,"pathId":path_id,"simulate":True}
                result = self.help.fetch_url(url='https://api.odos.xyz/sor/assemble', type='post', payload=payload, headers=self.headers)
                if result['simulation']['isSuccess']:
                    return result
                time.sleep(i * 1)
            except:
                time.sleep(i * 1)
        return {}

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        if attempt != 0:
            time.sleep(1)
        if attempt > 10:
            return "error"

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, tokens_data_[token_from]['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, tokens_data_[token_from]['address'], swaps_data[self.project]['contract'])

        quote = self.quote(amount, token_from, token_to, account)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        swap_data = self.swap_requsets(quote['pathId'], account)
        if not swap_data or swap_data.get('detail', 'none').lower() == 'Input token not available'.lower():
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        try:
            out_amount = int(swap_data['inputTokens'][0]['amount'])
            in_amount = int(swap_data['outputTokens'][0]['amount'])
        except:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, out_amount, in_amount)
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        tx = make_tx(new_w3, account, value=int(swap_data['transaction']['value']), to=swap_data['transaction']['to'], data=swap_data['transaction']['data'])

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key)

        return new_w3.to_hex(hash)

#NO
class Inch():
    def __init__(self, w3, max_slip, helper):
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
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from, token_to, account):
        for i in range(5):
            try:
                token_from = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from
                token_to = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to
                url = f"https://api-symbiosis.1inch.io/v5.0/59144/swap?fromTokenAddress={token_from}&toTokenAddress={token_to}&amount={amount}&fromAddress={account.address}&destReceiver={account.address}&slippage={int(self.max_slip)}&disableEstimate=true&allowPartialFill=false" #&protocols=ZKSYNC_MUTE%2CZKSYNC_ONE_INCH_LIMIT_ORDER_V3%2CZKSYNC_PMMX%2CZKSYNC_SPACEFI%2CZKSYNC_SYNCSWAP%2CZKSYNC_GEM%2CZKSYNC_MAVERICK_V1%2CZKSYNC_WOOFI_V2&usePatching=false
                # url2 = f'https://api-symbiosis.1inch.io/v5.0/324/quote?fromTokenAddress={token_from}&toTokenAddress={token_to}&amount={amount}&gasPrice=250000000&protocolWhiteList=ZKSYNC_MUTE,ZKSYNC_ONE_INCH_LIMIT_ORDER_V3,ZKSYNC_PMMX,ZKSYNC_SPACEFI,ZKSYNC_SYNCSWAP,ZKSYNC_GEM,ZKSYNC_MAVERICK_V1,ZKSYNC_WOOFI_V2&walletAddress={self.account.address}&preset=maxReturnResult'
                result = self.help.fetch_url(url=url, type='get', headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if attempt != 0:
            time.sleep(1)
        if attempt > 10:
            return "error"

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        try:
            _amount = int(amount * 10 ** int(token_from_data['decimals']))
        except:
            _amount = int(amount * 10 ** int(token_from_data['decimal']))

        if token_from != 'ETH':
            _amount = int(amount * 10 ** token_from_data['decimal'])
            _amount = min(_amount, get_balance(new_w3, account, token_from_data['address']))
            amount = float(_amount / (10 ** token_from_data['decimal']) * 0.999)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])

        quote = self.quote(str(_amount), token_from_data['address'], token_to_data['address'], account)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        if quote.get('description', 'none').lower() == 'insufficient liquidity':
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        elif quote.get('error', False):
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, int(quote['fromTokenAmount']), int(quote['toTokenAmount']))
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        tx = make_tx(new_w3, account, value=int(quote['tx']['value']), to=new_w3.to_checksum_address(quote['tx']['to']), data=quote['tx']['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#? API ERROR
class Sushiswap():

    def __init__(self, w3, max_slip, helper):

        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'SUSHISWAP'
        self.available_tokens = tokens_data_
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
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data['SUSHISWAP']['contract']), abi=swaps_data['SUSHISWAP']['ABI'])

    def get_quote(self, token_in, token_out, amount, account, new_w3):
        from_token_id = 'ETH' if token_in.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_in
        token_in = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_in.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_in
        token_out = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_out.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_out
        url = f'https://swap.sushi.com/{"v3.2"}?chainId={str(59144)}&tokenIn={token_in}&tokenOut={token_out}&fromTokenId={from_token_id}&toTokenId={token_out}&amount={str(amount)}&maxPriceImpact={int(self.max_slip)/100}&gasPrice={new_w3.eth.gas_price}&to={account.address}&preferSushi=true'

        for i in range(3):
            try:
                result = self.helper.fetch_url(url=url, type='get', headers=self.headers, retries=5, timeout=5)
                return json.loads(result)
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, factor=1, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        quote = self.get_quote(token_from_data['address'], token_to_data['address'], int(amount * 10 ** token_from_data['decimal']), account, new_w3)
        if not quote or not quote.get('route', {}).get('status') == 'Success':
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, factor=factor, attempt=attempt+1)
        route = quote['route']
        if float(route['priceImpact']) > self.max_slip/100:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, factor=factor, attempt=attempt+2)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data['SUSHISWAP']['contract'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data['SUSHISWAP']['contract'])

        func_ = getattr(self.contract.functions, 'processRoute')
        args = quote['args']['tokenIn'], int(route['amountIn']), quote['args']['tokenOut'], int(route['amountOut']*factor), account.address, quote['args']['routeCode']

        tx = make_tx(new_w3, account, value=int(route['amountIn']) if token_from == 'ETH' else 0, func=func_, args=args)

        if tx == "low_native" or not tx or tx == 'error':
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, factor=factor, attempt=attempt+1)
        if tx == 'factor':
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, factor=factor*0.99, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, factor=factor, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Pancake():

    def __init__(self, w3, max_slip, helper):
        self.project = 'PANCAKE'
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']),abi=swaps_data[self.project]['ABI'])
        self.max_slip = max_slip
        self.pools = self.get_pools()

    def get_pools(self):
        # url = 'https://api.studio.thegraph.com/query/45376/exchange-v3-base/version/latest'
        # payload = { "query": """query MyQuery { pools( first: 20 orderBy: totalValueLockedUSD orderDirection: desc where: {totalValueLockedUSD_gte: "500"} ) { id token0 { decimals id name symbol } token1 { decimals id name symbol } volumeUSD totalValueLockedUSD sqrtPrice liquidity feeTier feeProtocol token0Price token1Price } }""",}
        for i in range(5):
            try:
                result = self.help.fetch_url(url='https://api.dexscreener.com/latest/dex/pairs/linea/0xd5539d0360438a66661148c633a9f0965e482845,0xa48e0630b7b9dcb250112143c9d0fe47d26cb1e4,0xbd3bc396c9393e63bbc935786dd120b17f58df4c,0xe817a59f8a030544ff65f47536aba272f6d63059,0x42c9e266b226bbf0b11c14416faabfce29c96b78,0x6a72f4f191720c411cd1ff6a5ea8dedec3a64771',type='get')
                return result['pairs']
                # result = self.help.fetch_url(url=url, type='post', payload=payload)
                # return result['data']['pools']
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

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

        if not self.pools:
            return 'no_route'

        try:
            token_from_data = tokens_data_[token_from]
            token_to_data = tokens_data_[token_to]
        except:
            return "no_route"

        pool = None
        for p in self.pools:
            if p['quoteToken']['address'].lower() == token_from_data['address'].lower() and p['baseToken']['address'].lower() == token_to_data['address'].lower() or p['baseToken']['address'].lower() == token_from_data['address'].lower() and p['quoteToken']['address'].lower() == token_to_data['address'].lower():
                pool = p

        self.prices = self.help.get_prices_combined()
        if pool is not None:
            contract = new_w3.eth.contract(address=new_w3.to_checksum_address(pool['pairAddress']), abi=swaps_data[self.project]['ABI_pool'])
            fee = contract.functions.fee().call()
            tokens = new_w3.to_checksum_address(token_to_data['address']), new_w3.to_checksum_address(token_from_data['address'])
            amount_in = int(amount * 10 ** token_from_data['decimal'])
            amount_out_min = int(amount * self.prices[token_from] / self.prices[token_to] * ((100-self.max_slip)/100) * 10 ** token_to_data['decimal'])
            sqrt_price_limit_x96 = 0#math.isqrt(int(pool["sqrtPrice"]) * 10 ** 12)

            recipient = account.address
            add_data = ''
            if token_from == 'ETH' or token_to == 'ETH':
                if token_to == 'ETH':
                    recipient = new_w3.to_checksum_address('0x0000000000000000000000000000000000000002')
                    add_data = self.contract.encodeABI(fn_name='unwrapWETH9', args=[0, account.address])
            else:
                add_data = ''

            args = tokens[1], tokens[0], fee, recipient, amount_in, amount_out_min, sqrt_price_limit_x96

            swap_data = [self.contract.encodeABI(fn_name='exactInputSingle', args=[args])]
            if add_data:
                swap_data.append(add_data)

            tx_args = int(time.time())+300, swap_data

        else:
            paths = []
            for p in self.pools:
                pools = []
                if p['quoteToken']['address'].lower() == token_from_data['address'].lower() or p['baseToken']['address'].lower() == token_from_data['address'].lower():
                    pools.append(p['pairAddress'])
                    intermediate_token = p['quoteToken'] if p['quoteToken']['address'].lower() != token_from_data['address'].lower() else p['baseToken']
                    for sub_p in self.pools:
                        if sub_p['quoteToken']['address'].lower() == intermediate_token['address'].lower() and sub_p['baseToken']['address'].lower() == token_to_data['address'].lower() or sub_p['baseToken']['address'].lower() == intermediate_token['address'].lower() and sub_p['quoteToken']['address'].lower() == token_to_data['address'].lower():
                            pools.append(sub_p['pairAddress'])
                            path = {"intermediate_token": intermediate_token, "pools": pools}
                            paths.append(path)
            if not paths:
                return 'no_route'

            path = random.choice(paths)
            path['fees'] = []
            for pool in path['pools']:
                contract = new_w3.eth.contract(address = new_w3.to_checksum_address(pool), abi=swaps_data[self.project]['ABI_pool'])
                fee = contract.functions.fee().call()
                path['fees'].append(fee)
            path = f"{token_from_data['address']}{'{:06X}'.format(path['fees'][0])}{path['intermediate_token']['address'][2:]}{'{:06X}'.format(path['fees'][1])}{token_to_data['address'][2:]}"
            amount_in = int(amount * 10 ** token_from_data['decimal'])
            amount_out_min = int(amount * self.prices[token_from] / self.prices[token_to] * ((100 - self.max_slip) / 100) * 10 **token_to_data['decimal'])
            if token_to == 'ETH':
                add_data = self.contract.encodeABI(fn_name='unwrapWETH9', args=[0, account.address])
            else:
                add_data = ''
            args = path, account.address, amount_in, amount_out_min

            swap_data = [self.contract.encodeABI(fn_name='exactInput', args=[args])]
            if add_data:
                swap_data.append(add_data)

            tx_args = int(time.time()) + 300, swap_data


        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, amount_in, amount_out_min)
        if (slip * 0.5) > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != "ETH":
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])

        func_ = getattr(self.contract.functions, 'multicall')

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(amount_in), func=func_, args=tx_args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+ NO MULTIROUTE
class Velocore():

    def __init__(self, w3, max_slip, helper):
        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'VELOCORE'
        self.available_tokens = tokens_data_
        self.contract_vault = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_vault']), abi=swaps_data[self.project]['ABI_vault'])
        self.contract_factory = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_factory']),abi=swaps_data[self.project]['ABI_factory'])
        self.contract_data_ = self.w3.eth.contract( address=self.w3.to_checksum_address(swaps_data[self.project]['contract_data']),abi=swaps_data[self.project]['ABI_data'])
        self.pools = self.get_pools()

    def unpack_token(self, token):
        packed_eth = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        if token == packed_eth:
            return tokens_data_['ETH']
        token_ = f"0x{token[24:].lower()}"
        _ = [data for exact_token, data in tokens_data_.items() if data['address'].lower() == token_]
        return _[-1]

    def get_pools(self):
        url = 'https://v2-api.velocore.xyz/whitelisted-pools/59144'
        for i in range(5):
            try:
                result = self.helper.fetch_url(url=url, type='get')
                pairs = []
                for res in result:
                    try:
                        pool_ = self.contract_data_.functions.queryPool(self.w3.to_checksum_address(res)).call()
                        pairs.append({"pool": pool_[0], "token0": self.unpack_token(pool_[4][0].hex()), "token1": self.unpack_token(pool_[4][1].hex())})
                    except:
                        pass
                return pairs
            except:
                time.sleep(i * 1)
        return []

    def get_route(self, token_from, token_to):
        for pool in self.pools:
            if pool['token0']['address'].lower() == token_from.lower() or pool['token1']['address'].lower() == token_from.lower():
                sub_token = pool['token0'] if pool['token0']['address'].lower() != token_from.lower() else pool['token1']
                for sub_pool in self.pools:
                    if (sub_pool['token0']['address'].lower() == token_to.lower() and sub_pool['token1']['address'].lower() == sub_token['address'].lower()) or (sub_pool['token1']['address'].lower() == token_to.lower() and sub_pool['token0']['address'].lower() == sub_token['address'].lower()):
                        return (pool['pool'], token_from, sub_token), (sub_pool['pool'], sub_token, token_to)

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return {}

    def get_packed_pool(self, address):
        operation_types = {"swap": 0}
        unused_bytes = 0
        type_packed = (operation_types['swap']).to_bytes(1, byteorder='big')
        id_packed = unused_bytes.to_bytes(11, byteorder='big')
        address_packed = bytes.fromhex(address[2:])

        return '0x' + (type_packed + id_packed + address_packed).hex()

    def get_packed_token(self, token):
        packed_eth = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        token_types = {'erc20': 0, 'erc721': 1, 'erc1155': 2}

        if token['symbol'] == 'ETH':
            return packed_eth

        id = 0
        type_packed = (token_types['erc20']).to_bytes(1, byteorder='big')
        id_packed = id.to_bytes(11, byteorder='big')
        address_packed = bytes.fromhex(token['address'][2:])

        return '0x' + (type_packed + id_packed + address_packed).hex()

    def get_packed_token_information(self, index, amount_type, normalized_amount):
        unused_bytes = 0

        index_packed = index.to_bytes(1, byteorder='big')
        amount_type_packed = amount_type.to_bytes(1, byteorder='big')
        unused_bytes_packed = unused_bytes.to_bytes(14, byteorder='big')
        normalized_amount_packed = normalized_amount.to_bytes(16, byteorder='big')

        return '0x' + (index_packed + amount_type_packed + unused_bytes_packed + normalized_amount_packed).hex()

    def get_swap_params(self, pool_address, token_from, token_to, amount, amount_out):
        amount_types = { 'exactly': 0, 'at_most': 1, 'all': 2, }

        pool_packed = self.get_packed_pool(pool_address)
        from_token_ref = self.get_packed_token(token_from)
        to_token_ref = self.get_packed_token(token_to)

        token_ref = sorted([from_token_ref, to_token_ref])

        deposit = [0] * len(token_ref)

        from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref), amount_type=amount_types['exactly'], normalized_amount=amount)
        to_token_info = self.get_packed_token_information(index=token_ref.index(to_token_ref), amount_type=amount_types['at_most'], normalized_amount=amount_out)

        token_info = sorted([from_token_info, to_token_info])

        return [token_ref, deposit, [[pool_packed, token_info, '0x']]]

    def get_multi_swap_params(self, pool_operations):
        amount_types = {'exactly': 0, 'at_most': 1, 'all': 2}

        token_refs = []
        deposits = []
        ops = []

        # Extract all token references first
        for operation in pool_operations:
            _, token_from, token_to, _, _, _ = operation
            from_token_ref = self.w3.to_bytes(hexstr=self.get_packed_token(token_from))
            to_token_ref = self.w3.to_bytes(hexstr=self.get_packed_token(token_to))
            token_refs.extend([from_token_ref, to_token_ref])

        # Get unique token references and sort them
        unique_token_refs = sorted(list(set(token_refs)))

        for operation in pool_operations:
            pool_address, token_from, token_to, amount, amount_out, op = operation

            pool_packed = self.w3.to_bytes(hexstr=self.get_packed_pool(pool_address))
            from_token_ref = self.w3.to_bytes(hexstr=self.get_packed_token(token_from))
            to_token_ref = self.w3.to_bytes(hexstr=self.get_packed_token(token_to))

            deposit = [0] * len(unique_token_refs)
            deposits.append(deposit)

            from_token_info = self.get_packed_token_information(index=unique_token_refs.index(from_token_ref),
                                                                amount_type=amount_types[op], normalized_amount=amount)
            to_token_info = self.get_packed_token_information(index=unique_token_refs.index(to_token_ref),
                                                              amount_type=amount_types['at_most'],
                                                              normalized_amount=amount_out)

            token_info = sorted([self.w3.to_bytes(hexstr=from_token_info), self.w3.to_bytes(hexstr=to_token_info)])

            ops.append([pool_packed, token_info, b'0x'])

        return [unique_token_refs, [0, 0], ops]

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        amount_ = int(amount * 10 ** token_from_data['decimal'])

        pool_address = self.contract_factory.functions.pools(self.get_packed_token(token_from_data), self.get_packed_token(token_to_data)).call()
        route = None
        if pool_address == NULL_ADDRESS:
            # route = self.get_route(token_from_data['address'], token_to_data['address'])
            # if not route:
            return 'no_route'

        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))

        # if route is None:
        args = self.get_swap_params(pool_address, token_from_data, token_to_data, amount_, min_amount)
        # else:
        #     pool_operations = [(route[0][0], token_from_data, route[0][2], amount_, 170141183460469231731687303715884105727, 'exactly'), (route[1][0], route[1][1], token_to_data, min_amount, 170141183460469231731687303715884105727, 'all')]
        #     args = self.get_multi_swap_params(pool_operations)
        #     #args = self.get_swap_params_with_hops([p['pool'] for p in route], [token_from_data, sub_token], [sub_token, token_to_data], amount_, min_amount)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract_vault'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract_vault'])

        func_ = getattr(self.contract_vault.functions, 'execute')

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else amount_, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Syncswap():

    def __init__(self, w3, max_slip, helper):
        self.project = 'SYNCSWAP'
        self.help = helper
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.factory = self.w3.eth.contract( address=self.w3.to_checksum_address(swaps_data[self.project]['contract_factory']), abi=swaps_data[self.project]['ABI_factory'])
        self.max_slip = max_slip
        self.available_tokens = tokens_data_

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.help.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return {}

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

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

        if token_to == 'ETH':
            token_to = "WETH"
        if token_from == 'ETH':
            token_from = "WETH"

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        amount_ = int(amount * 10 ** token_from_data['decimal'])
        pool_address = self.factory.functions.getPool(new_w3.to_checksum_address(token_to_data['address']),
                                                      new_w3.to_checksum_address(token_from_data['address'])).call()

        if pool_address == NULL_ADDRESS:
            return 'no_route'

        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return 'no_data'

        token_from_address = new_w3.to_checksum_address(token_from_data['address'])

        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))

        type = 0 if token_from != 'WETH' and token_to != 'WETH' else (2 if token_from == 'WETH' else 1)
        swap_data = encode(["address", "address", "uint8"], [token_from_address, account.address, type])

        steps = new_w3.to_checksum_address(pool_address), swap_data, NULL_ADDRESS, b'0x'
        path = [[steps], token_from_address if token_from != 'WETH' else NULL_ADDRESS, amount_]
        args = [path], min_amount, int(time.time() + 60 * 30)

        if token_from != 'WETH':
            approve = check_approve(self.w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(self.w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        func_ = getattr(self.contract.functions, 'swap')

        tx = make_tx(self.w3, account, value=0 if token_from != 'WETH' else amount_, func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Lynex():

    def __init__(self, w3, max_slip, helper):
        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'LYNEX'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.contract_quoter = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_quoter']), abi=swaps_data[self.project]['ABI_quoter'])
        self.pools = self.get_pools()

    def get_pools(self):
        for i in range(5):
            try:
                payload = {"query":"\n      query MyQuery { pools(first: 25, orderBy: volumeUSD, orderDirection: desc) { volumeUSD fee feeGrowthGlobal0X128 feeGrowthGlobal1X128 id liquidity token0 { decimals id name symbol } token1 { decimals id name symbol } tick tickSpacing } }"}
                result = self.helper.fetch_url(url='https://graph-query.linea.build/subgraphs/name/cryptoalgebra/analytics',type='post', payload=payload)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_route(self, token_from, token_to):

        max_liq, pool_ = 0, None
        for pool in self.pools:
            if (pool['token0']['id'].lower() == token_from and pool['token1']['id'].lower() == token_to) or (pool['token1']['id'].lower() == token_from and pool['token0']['id'].lower() == token_to):
                if float(pool['volumeUSD']) > max_liq:
                    max_liq = float(pool['volumeUSD'])
                    pool_ = pool
        if pool_:
            return [pool_]
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    if (sub_pool['token0']['id'].lower() == token_X and sub_pool['token1']['id'].lower() == token_to) or (sub_pool['token1']['id'].lower() == token_X and sub_pool['token0']['id'].lower() == token_to):
                        return [pool, sub_pool]

        good_pools = []
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    token_Y = sub_pool['token0']['id'].lower() if sub_pool['token0']['id'].lower() != token_X else sub_pool['token1']['id'].lower()
                    for sub_pool_ in self.pools:
                        if (sub_pool_['token0']['id'].lower() == token_Y and sub_pool_['token1']['id'].lower() == token_to) or (sub_pool_['token1']['id'].lower() == token_Y and sub_pool_['token0']['id'].lower() == token_to):
                            good_pools.append([pool, sub_pool, sub_pool_])
        if good_pools:
            prefered_tokens = ['0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'.lower(), '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower()]
            for p in good_pools:
                token_x = p[0]['token0']['id'] if p[0]['token0']['id'].lower() != token_from else p[0]['token1']['id']
                if token_x.lower() in prefered_tokens:
                    return p
        else:
            return []

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        route = self.get_route(token_from_data['address'].lower(), token_to_data['address'].lower())
        if not route:
            return 'no_route'

        if len(route) == 1:
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
        elif len(route) == 2:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{new_w3.to_checksum_address(token_x)[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
        elif len(route) == 3:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            token_y = route[1]['token0']['id'].lower() if token_x != route[1]['token0']['id'].lower() else route[1]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{new_w3.to_checksum_address(token_x)[2:]}{new_w3.to_checksum_address(token_y)[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"

        else:
            return 'no_route'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        bytes_path = bytes.fromhex(path[2:])

        if len(route) == 1:
            quote = self.contract_quoter.functions.quoteExactInputSingle(new_w3.to_checksum_address(token_from_data['address']),new_w3.to_checksum_address(token_to_data['address']), _amount, 0).call()
            min_amount = quote[0]
        else:
            quote = self.contract_quoter.functions.quoteExactInput(bytes_path, _amount).call()
            min_amount = quote[0]

        slip = check_slippage(self.helper.get_prices_combined(), token_from, token_to, _amount, min_amount)
        if (slip * 0.5) > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        min_amount = int(min_amount*0.995)

        if len(route) == 1:
            func = 'exactInputSingle'
            args = new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_to_data['address']), account.address, int(time.time()+60*30), _amount, min_amount, 0
        else:
            func = 'exactInput'
            args = path, account.address, int(time.time()+60*30), _amount, min_amount

        func_ = getattr(self.contract.functions, func)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Echodex():

    def __init__(self, w3, max_slip, helper):
        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'ECHODEX'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.contract_router = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_router']), abi=swaps_data[self.project]['ABI_router'])
        self.pools = self.get_pools()

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return {}

    def get_pools(self):
        for i in range(5):
            try:
                payload = {"query":"\n      query MyQuery { pools(first: 50, orderBy: totalValueLockedUSD, orderDirection: desc) { totalValueLockedUSD id feeTier volumeUSD token0 { decimals id name symbol } token1 { decimals id name symbol } } }"}
                result = self.helper.fetch_url(url='https://graph-query.linea.build/subgraphs/name/echodex/exchange-v3-2',type='post', payload=payload)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_route(self, token_from, token_to):

        max_liq, pool_ = 0, None
        for pool in self.pools:
            if (pool['token0']['id'].lower() == token_from and pool['token1']['id'].lower() == token_to) or (pool['token1']['id'].lower() == token_from and pool['token0']['id'].lower() == token_to):
                if float(pool['totalValueLockedUSD']) > max_liq:
                    max_liq = float(pool['totalValueLockedUSD'])
                    pool_ = pool
        if pool_:
            return [pool_]
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    if (sub_pool['token0']['id'].lower() == token_X and sub_pool['token1']['id'].lower() == token_to) or (sub_pool['token1']['id'].lower() == token_X and sub_pool['token0']['id'].lower() == token_to):
                        return [pool, sub_pool]

        good_pools = []
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    token_Y = sub_pool['token0']['id'].lower() if sub_pool['token0']['id'].lower() != token_X else sub_pool['token1']['id'].lower()
                    for sub_pool_ in self.pools:
                        if (sub_pool_['token0']['id'].lower() == token_Y and sub_pool_['token1']['id'].lower() == token_to) or (sub_pool_['token1']['id'].lower() == token_Y and sub_pool_['token0']['id'].lower() == token_to):
                            good_pools.append([pool, sub_pool, sub_pool_])
        if good_pools:
            prefered_tokens = ['0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'.lower(), '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower()]
            for p in good_pools:
                token_x = p[0]['token0']['id'] if p[0]['token0']['id'].lower() != token_from else p[0]['token1']['id']
                if token_x.lower() in prefered_tokens:
                    return p
        else:
            return []

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        route = self.get_route(token_from_data['address'].lower(), token_to_data['address'].lower())
        if not route:
            return 'no_route'

        if len(route) == 1:
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 2:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 3:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            token_y = route[1]['token0']['id'].lower() if token_x != route[1]['token0']['id'].lower() else route[1]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['feeTier']))[2:]}{new_w3.to_checksum_address(token_y)[2:]}{'{:08X}'.format(int(route[2]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_y), new_w3.to_checksum_address(token_to_data['address'])]

        else:
            return 'no_route'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return 'no_data'

        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))

        bytes_path = bytes.fromhex(path[2:])
        if len(route) == 1:
            data = self.contract.encodeABI(fn_name='exactInputSingle', args=[[path_origin[0], path_origin[1], int(route[0]['feeTier']), account.address if token_to != 'ETH' else '0x0000000000000000000000000000000000000002', _amount, min_amount, 0]])
        else:
            data = self.contract.encodeABI(fn_name='exactInput', args=[[bytes_path, account.address, _amount, min_amount]])

        unwrap_data = self.contract.encodeABI(fn_name='unwrapWETH9', args=[min_amount, account.address])
        all_data = [data] if token_to != 'ETH' else [data, unwrap_data]
        args = int(time.time() + 300), all_data

        func_ = getattr(self.contract.functions, 'multicall')

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Horizon():

    def __init__(self, w3, max_slip, helper):
        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'HORIZON'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        #self.contract_router = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_router']), abi=swaps_data[self.project]['ABI_router'])
        self.pools = self.get_pools()

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return {}

    def get_pools(self):
        for i in range(3):
            try:
                payload = {"query":"\n      query MyQuery { pools(first: 500, orderBy: totalValueLockedUSD, orderDirection: desc) { feeTier id volumeUSD totalValueLockedUSD token0 { decimals id name symbol } token1 { decimals id name symbol } } }"}
                result = self.helper.fetch_url(url='https://subgraph-mainnet.horizondex.io/subgraphs/name/horizondex/horizondex-mainnet-v2',type='post', payload=payload, retries=5, timeout=5)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_route(self, token_from, token_to):

        max_liq, pool_ = 0, None
        for pool in self.pools:
            if (pool['token0']['id'].lower() == token_from and pool['token1']['id'].lower() == token_to) or (pool['token1']['id'].lower() == token_from and pool['token0']['id'].lower() == token_to):
                if float(pool['volumeUSD']) > max_liq:
                    max_liq = float(pool['volumeUSD'])
                    pool_ = pool
        if pool_:
            return [pool_]
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    if (sub_pool['token0']['id'].lower() == token_X and sub_pool['token1']['id'].lower() == token_to) or (sub_pool['token1']['id'].lower() == token_X and sub_pool['token0']['id'].lower() == token_to):
                        return [pool, sub_pool]

        good_pools = []
        for pool in self.pools:
            if pool['token0']['id'].lower() == token_from or pool['token1']['id'].lower() == token_from:
                token_X = pool['token0']['id'].lower() if pool['token0']['id'].lower() != token_from else pool['token1']['id'].lower()
                for sub_pool in self.pools:
                    token_Y = sub_pool['token0']['id'].lower() if sub_pool['token0']['id'].lower() != token_X else sub_pool['token1']['id'].lower()
                    for sub_pool_ in self.pools:
                        if (sub_pool_['token0']['id'].lower() == token_Y and sub_pool_['token1']['id'].lower() == token_to) or (sub_pool_['token1']['id'].lower() == token_Y and sub_pool_['token0']['id'].lower() == token_to):
                            good_pools.append([pool, sub_pool, sub_pool_])
        if good_pools:
            prefered_tokens = ['0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'.lower(), '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower()]
            for p in good_pools:
                token_x = p[0]['token0']['id'] if p[0]['token0']['id'].lower() != token_from else p[0]['token1']['id']
                if token_x.lower() in prefered_tokens:
                    return p
        else:
            return []

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        route = self.get_route(token_from_data['address'].lower(), token_to_data['address'].lower())
        if not route:
            return 'no_route'

        if len(route) == 1:
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 2:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 3:
            token_x = route[0]['token0']['id'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['token1']['id'].lower()
            token_y = route[1]['token0']['id'].lower() if token_x != route[1]['token0']['id'].lower() else route[1]['token1']['id'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['feeTier']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['feeTier']))[2:]}{new_w3.to_checksum_address(token_y)[2:]}{'{:08X}'.format(int(route[2]['feeTier']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_y), new_w3.to_checksum_address(token_to_data['address'])]

        else:
            return 'no_route'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return 'no_data'

        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))

        bytes_path = bytes.fromhex(path[2:])
        if len(route) == 1:
            data = self.contract.encodeABI(fn_name='swapExactInputSingle', args=[[path_origin[0], path_origin[1], int(route[0]['feeTier']), account.address if token_to != 'ETH' else '0x0000000000000000000000000000000000000000', int(time.time()+300), _amount, min_amount, 0]])
        else:
            data = self.contract.encodeABI(fn_name='swapExactInput', args=[[bytes_path, account.address, int(time.time()+300), _amount, min_amount]])

        unwrap_data = self.contract.encodeABI(fn_name='unwrapWeth', args=[min_amount, account.address])
        all_data = [data] if token_to != 'ETH' else [data, unwrap_data]
        args = all_data

        func_ = getattr(self.contract.functions, 'multicall')

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)


class Vooi():

    def __init__(self, w3, max_slip, helper):
        self.w3 = w3
        self.max_slip = max_slip
        self.helper = helper
        self.project = 'VOOI'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.pools = self.get_pools()

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return {}

    def get_pools(self):
        pools = {}
        total_pools = self.contract.functions.lastIndex().call()
        for i in range(total_pools):
            try:
                pool_data = self.contract.functions.indexToAsset(i).call()
                pools[pool_data[5].lower()] = {"pool_data": pool_data, "id": i}
            except:
                pass
        return pools

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        if attempt > 10:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        try:
            token_from_pool_data = self.pools[token_from_data['address'].lower()]
            token_to_pool_data = self.pools[token_to_data['address'].lower()]
        except:
            return 'error'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return 'no_data'

        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))
        args = token_from_pool_data['id'], token_to_pool_data['id'], _amount, min_amount, account.address, int(time.time()+300)
        func_ = getattr(self.contract.functions, 'swap')

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Izumi():

    def __init__(self, w3, max_slip, helper):
        self.project = 'IZUMI'
        self.headers = {
            'authority': 'api.izumi.finance',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en;q=0.9',
            'origin': 'https://zksync.izumi.finance',
            'referer': 'https://zksync.izumi.finance/',
            'sec-ch-ua': '"Chromium";v="112", "YaBrowser";v="23", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.pools = self.get_pools()
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.max_slip = max_slip

    def get_pools(self):
        for i in range(5):
            try:
                result = self.help.fetch_url(url='https://api.izumi.finance/api/v1/izi_swap/summary_record/?page=1&page_size=300&chain_id=59144&type=0&order_by=-vol_day', type='get')
                return result['data']
            except:
                time.sleep(i * 1)
        return {}

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.help.get_prices_combined()
                return self.prices[token_from['symbol']] / self.prices[token_to['symbol']]
            except:
                time.sleep(i * 1)
        return 1

    def get_route(self, token_from, token_to):

        max_liq, pool_ = 0, None
        for pool in self.pools:
            if (pool['tokenX_address'].lower() == token_from and pool['tokenY_address'].lower() == token_to) or (pool['tokenY_address'].lower() == token_from and pool['tokenX_address'].lower() == token_to):
                if float(pool['volDay']) > max_liq:
                    max_liq = float(pool['volDay'])
                    pool_ = pool
        if pool_:
            return [pool_]
        for pool in self.pools:
            if pool['tokenX_address'].lower() == token_from or pool['tokenY_address'].lower() == token_from:
                token_X = pool['tokenX_address'].lower() if pool['tokenX_address'].lower() != token_from else pool['tokenY_address'].lower()
                for sub_pool in self.pools:
                    if (sub_pool['tokenX_address'].lower() == token_X and sub_pool['tokenY_address'].lower() == token_to) or (sub_pool['tokenY_address'].lower() == token_X and sub_pool['tokenX_address'].lower() == token_to):
                        return [pool, sub_pool]

        good_pools = []
        for pool in self.pools:
            if pool['tokenX_address'].lower() == token_from or pool['tokenY_address'].lower() == token_from:
                token_X = pool['tokenX_address'].lower() if pool['tokenX_address'].lower() != token_from else pool['tokenY_address'].lower()
                for sub_pool in self.pools:
                    token_Y = sub_pool['tokenX_address'].lower() if sub_pool['tokenX_address'].lower() != token_X else sub_pool['tokenY_address'].lower()
                    for sub_pool_ in self.pools:
                        if (sub_pool_['tokenX_address'].lower() == token_Y and sub_pool_['tokenY_address'].lower() == token_to) or (sub_pool_['tokenY_address'].lower() == token_Y and sub_pool_['tokenX_address'].lower() == token_to):
                            good_pools.append([pool, sub_pool, sub_pool_])
        if good_pools:
            prefered_tokens = ['0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'.lower(), '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower()]
            for p in good_pools:
                token_x = p[0]['tokenX_address'] if p[0]['tokenX_address'].lower() != token_from else p[0]['tokenY_address']
                if token_x.lower() in prefered_tokens:
                    return p
        else:
            return []

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

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
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        route = self.get_route(token_from_data['address'].lower(), token_to_data['address'].lower())
        if not route:
            return 'no_route'

        if len(route) == 1:
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['fee']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 2:
            token_x = route[0]['tokenX_address'].lower() if token_from_data['address'].lower() != route[0]['tokenX_address'].lower() else route[0]['tokenY_address'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['fee']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['fee']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_to_data['address'])]
        elif len(route) == 3:
            token_x = route[0]['tokenX_address'].lower() if token_from_data['address'].lower() != route[0]['token0']['id'].lower() else route[0]['tokenY_address'].lower()
            token_y = route[1]['tokenX_address'].lower() if token_x != route[1]['tokenX_address'].lower() else route[1]['tokenY_address'].lower()
            path = f"{new_w3.to_checksum_address(token_from_data['address'])}{'{:08X}'.format(int(route[0]['fee']))[2:]}{new_w3.to_checksum_address(token_x)[2:]}{'{:08X}'.format(int(route[1]['fee']))[2:]}{new_w3.to_checksum_address(token_y)[2:]}{'{:08X}'.format(int(route[2]['fee']))[2:]}{new_w3.to_checksum_address(token_to_data['address'])[2:]}"
            path_origin = [new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_x), new_w3.to_checksum_address(token_y), new_w3.to_checksum_address(token_to_data['address'])]

        else:
            return 'no_route'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        quote_data = float(self.get_quote(token_from_data, token_to_data))
        if not quote_data:
            return 'no_data'

        min_amount = int(amount * quote_data * 10 ** int(token_to_data['decimal']) * ((100 - self.max_slip) / 100))

        bytes_path = bytes.fromhex(path[2:])

        reciepent = account.address if token_to != 'ETH' else '0x0000000000000000000000000000000000000000'
        data = self.contract.encodeABI(fn_name='swapAmount', args=[[bytes_path, reciepent, _amount, min_amount, int(time.time()+600)]])

        if token_from == "ETH":
            unwrap_data = [self.contract.encodeABI(fn_name='refundETH', args=[])]
        elif token_to == 'ETH':
            unwrap_data = [self.contract.encodeABI(fn_name='unwrapWETH9', args=[0, account.address])]
        else:
            unwrap_data = None

        args = [data] if not unwrap_data else [data, unwrap_data[0]]

        func_ = getattr(self.contract.functions, 'multicall')

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)




#+ NO EXTERNAL FOR NOW
class Woofi():

    def __init__(self, w3, max_slip, helper):
        self.project = 'WOOFI'
        self.headers = {
            'authority': 'fi-api.woo.org',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://fi.woo.org',
            'referer': 'https://fi.woo.org/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.max_slip = max_slip

    def get_quote(self, token_in, token_out, amount):
        params = {
            'from_token': self.w3.to_checksum_address(token_in),
            'to_token': self.w3.to_checksum_address(token_out),
            'from_amount': str(amount),
            'network': 'linea',
        }
        for i in range(3):
            try:
                result = self.help.fetch_url(url='https://fi-api.woo.org/woofi_swap', type='get', params=params, headers=self.headers, retries=5, timeout=5)
                if result.get('status', '') == 'ok':
                    return result['data']
                else:
                    raise Exception
            except Exception:
                time.sleep(i * 1)
        return None

    def get_external_tx(self, token_in, token_out, amount):
        token_in = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_in.lower() == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'.lower() else token_in
        token_out = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_out.lower() == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'.lower() else token_out
        params = {
            'fromTokenAddress': token_in,
            'toTokenAddress': token_out,
            'amount': amount,
            'fromAddress': '0xfd505702b37Ae9b626952Eb2DD736d9045876417',
            'slippage': str(int(min(1, self.max_slip))),
            'disableEstimate': 'true',
            'allowPartialFill': 'false',
            'referrer': '0x5f67ffa4b3f77dd16c9c34a1a82cab8daea03191',
            'fee': 1
        }
        for i in range(3):
            try:
                result = self.help.fetch_url(url='https://api-kronos-woo.1inch.io/v5.2/324/swap', type='get', params=params, headers=self.headers, retries=5, timeout=5)
                return result
            except Exception:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

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
        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        _amount = int(amount * 10 ** token_from_data['decimal'])

        quote = self.get_quote(token_from_data['address'].lower(), token_to_data['address'].lower(), _amount)
        if not quote:
            # external_tx = self.get_external_tx(token_from_data['address'].lower(), token_to_data['address'].lower(), _amount)
            # if not external_tx:
            #     return 'no_route'
            # else:
            #     amount_min = int(int(external_tx['toAmount']) * 0.995)
            #     external = True

            return 'no_route'
        else:
            amount_min = int(int(quote['to_amount']) * 0.995)
            external = False

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, _amount, amount_min)
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key,attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, token_from_data['address'], new_w3.to_checksum_address('0x39d361e66798155813b907a70d6c2e3fdafb0877') if external else swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, token_from_data['address'], new_w3.to_checksum_address('0x39d361e66798155813b907a70d6c2e3fdafb0877') if external else swaps_data[self.project]['contract'])

        token_from_data['address'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from_data['symbol'] == 'ETH' else token_from_data['address']
        token_to_data['address'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to_data['symbol'] == 'ETH' else token_to_data['address']

        if external:
            args = new_w3.to_checksum_address('0x39d361e66798155813b907a70d6c2e3fdafb0877'), new_w3.to_checksum_address("0x39d361e66798155813b907a70d6c2e3fdafb0877"), new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address( token_to_data['address']), _amount, amount_min, account.address, external_tx['tx']['data']
            func_ = getattr(self.contract.functions, 'externalSwap')
        else:
            args = new_w3.to_checksum_address(token_from_data['address']), new_w3.to_checksum_address(token_to_data['address']), _amount, amount_min, account.address, account.address
            func_ = getattr(self.contract.functions, 'swap')

        tx = make_tx(new_w3, account, value=0 if token_from != 'ETH' else int(_amount), func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)


class Spaceswap():
    def __init__(self, w3, max_slip, helper):
        self.project = 'SPACESWAP'
        self.help = helper
        self.headers = {
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'x-lifi-integrator': 'jumper.exchange',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'x-lifi-sdk': '2.4.1',
            'Referer': 'https://jumper.exchange/',
            'x-lifi-widget': '2.5.0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def get_routes(self, amount, account, from_token_data, to_token_data):
        from_token = "0x0000000000000000000000000000000000000000" if from_token_data['symbol'] == "ETH" else from_token_data['address']
        to_token = "0x0000000000000000000000000000000000000000" if to_token_data['symbol'] == "ETH" else to_token_data['address']
        payload = {"fromChainId":59144,"fromAmount":str(amount),"fromTokenAddress":from_token,"toChainId":59144,"toTokenAddress":to_token,"fromAddress":account.address,"toAddress":account.address,"options":{"slippage":max(0.005, self.max_slip/100),"maxPriceImpact":max(1, self.max_slip),"allowSwitchChain":True,"bridges":{"deny":[]},"exchanges":{"deny":[]},"order":"RECOMMENDED","insurance":False, 'referrer': '0x5f67ffa4b3f77DD16C9C34A1A82CaB8dAea03191', 'fee': 0.01, "integrator":"ch.dao"}}
        url = 'https://li.quest/v1/advanced/routes'
        for i in range(7):
            try:
                res = self.help.fetch_url(url=url, type='post', payload=payload, headers=self.headers)
                if len(res['routes']) == 0:
                    return None
                return res['routes'][0]['steps'][0]
            except:
                time.sleep((1*i)+i)
        return None

    def get_tx(self, payload):
        url = 'https://li.quest/v1/advanced/stepTransaction'
        for i in range(7):
            try:
                res = self.help.fetch_url(url=url, type='post', payload=payload, headers=self.headers)
                return res['transactionRequest']
            except:
                time.sleep((1 * i) + i)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        if attempt != 0:
            time.sleep(1)
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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        amount_ = int(amount * 10 ** token_from_data['decimal'])

        route = self.get_routes(amount_, account, token_from_data, token_to_data)
        if not route:
            if attempt > 5:
                return 'no_data'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key,  attempt=attempt + 1)

        tx_ = self.get_tx(route)
        if not tx_:
            if attempt > 5:
                return 'no_data'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key,attempt=attempt + 1)

        slip = (1-float(route['estimate']['toAmountUSD'])/float(route['estimate']['fromAmountUSD']))*100
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], tx_['to'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], tx_['to'])

        tx = make_tx(new_w3, account, value=int(tx_['value'], 16), to=new_w3.to_checksum_address(tx_['to']), data=tx_['data'], minus_fee=False)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Dodoex():
    def __init__(self, w3, max_slip, helper):
        self.project = 'DODOEX'
        self.headers = {
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://swapbox.nabox.io/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from_data, token_to_data, account):
        for i in range(5):
            try:
                token_from = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from_data['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from_data['address']
                token_to = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to_data['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to_data['address']
                url = f"https://api.dodoex.io/route-service/fee-route-widget/getdodoroute?chainId=59144&apikey=8477c6932c9df6c5b8&deadLine={int(time.time())+600}&fromAmount={amount}&fromTokenAddress={token_from}&fromTokenDecimals={token_from_data['decimal']}&toTokenAddress={token_to}&slippage={max(1, int(self.max_slip))}&userAddr={account.address}&rebateTo=0x5f67ffa4b3f77DD16C9C34A1A82CaB8dAea03191&fee=10000000000000000&rpc=https:%2F%2Frpc.linea.build%2F"
                result = self.help.fetch_url(url=url, type='get', headers=self.headers)
                return result['data']
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        if attempt != 0:
            time.sleep(1)
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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        quote = self.quote(str(int(amount * 10 ** token_from_data['decimal'])), token_from_data, token_to_data, account)
        if not quote:
            if attempt > 5:
                return 'no_data'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = float(quote['priceImpact'])
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['targetApproveAddr'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['targetApproveAddr'])

        tx = make_tx(new_w3, account, value=int(quote['value']), to=new_w3.to_checksum_address(quote['to']), data=quote['data'])

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Wowmax():
    def __init__(self, w3, max_slip, helper):
        self.project = 'WOWMAX'
        self.headers = {
            'authority': 'api-gateway.wowmax.exchange',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://app.wowmax.exchange',
            'referer': 'https://app.wowmax.exchange/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from_data, token_to_data, account):
        for i in range(5):
            try:
                token_from = '0x0000000000000000000000000000000000000000' if token_from_data['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from_data['address'].lower()
                token_to = '0x0000000000000000000000000000000000000000' if token_to_data['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to_data['address'].lower()
                url = f"https://api-gateway.wowmax.exchange/chains/59144/swap?amount={amount}&from={token_from}&to={token_to}&gasPrice={self.w3.eth.gas_price}&slippage={round(max(1, self.max_slip), 2)}"
                result = self.help.fetch_url(url=url, type='get', headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        if attempt != 0:
            time.sleep(1)
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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        quote = self.quote(str(amount), token_from_data, token_to_data, account)
        if not quote:
            if attempt > 5:
                return 'no_data'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        try:
            if quote.get('statusCode', 0) in [500, '500']:
                return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        except:
            pass

        slip = float(quote['priceImpact']) * 100
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['contract'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['contract'])

        try:
            value = int(quote['value'])
        except:
            value = 0

        tx = make_tx(new_w3, account, value=value, to=new_w3.to_checksum_address(quote['contract']), data=quote['data'], gas=int(quote['gasUnitsConsumed']))

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Openocean():
    def __init__(self, w3, max_slip, helper):
        self.project = 'OPENOCEAN'
        self.headers = {
            'authority': 'ethapi.openocean.finance',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://app.openocean.finance',
            'referer': 'https://app.openocean.finance/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'token': '',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from, token_to, account):
        for i in range(5):
            try:
                base_url = 'https://ethapi.openocean.finance/v2/59144/swap?'
                token_from['address'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from['address']
                token_to['address'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to['address'].lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to['address']
                payload = f"inTokenSymbol={token_from['symbol']}&inTokenAddress={token_from['address']}&outTokenSymbol={token_to['symbol']}&outTokenAddress={token_to['address']}&amount={amount}&gasPrice=661105768&disabledDexIds=&slippage={self.max_slip}&account={account.address}&referrer=0x5f67ffa4b3f77DD16C9C34A1A82CaB8dAea03191&flags=0&referrerFee=100"
                url = f"{base_url}{payload}"
                result = self.help.fetch_url(url=url, type='get', headers=self.headers)
                return result
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        if attempt != 0:
            time.sleep(1)
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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        quote = self.quote(str(int(amount * 10 ** token_from_data['decimal'])), token_from_data, token_to_data, account)
        if not quote:
            if attempt > 5:
                return 'no_data'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, int(quote['inAmount']), int(quote['outAmount']))
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract'])

        tx = make_tx(new_w3, account, value=int(quote['value']), to=new_w3.to_checksum_address(quote['to']), data=quote['data'])

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Okx():

    def __init__(self, w3, max_slip, helper):

        self.project = 'OKXSWAP'
        self.headers = {
            'authority': 'www.okx.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-sec-fetch-site': 'same-origin',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def get_quote(self, token_from, token_to, amount):
        token_from = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_from.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from
        token_to = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_to.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to
        payload = {"amount":str(amount),"chainId":59144,"toChainId":59144,"toTokenAddress":token_to,"fromTokenAddress":token_from,"slippage":self.max_slip,"slippageType":1,"pmm":"1","gasDropType":0}
        for i in range(5):
            try:
                url = f"https://www.okx.com/priapi/v1/dx/trade/multi/v2/quote?t={int(time.time())}"
                result = self.help.fetch_url(url=url, type='post', headers=self.headers, payload=payload)
                if int(result['code']) == 0:
                    return result['data']
            except:
                time.sleep(i * 1)
        return None

    def get_tx(self, quote, account):
        payload = {
            "autoSlippageInfo": {
                "autoSlippage": quote['autoSlippageInfo']['autoSlippage']
            },
            "chainId": 59144,
            "defiPlatformId": quote['defiPlatformInfo']['id'],
            "dexRouterList": quote['dexRouterList'],
            "estimateGasFee": quote['estimateGasFee'],
            "fromAmount": quote['fromTokenAmount'],
            "fromTokenAddress": quote['fromToken']['tokenContractAddress'],
            "fromTokenDecimal": quote['fromToken']['decimals'],
            "gasDropType": 0,
            "gasPrice": '0.25',
            "minimumReceived": quote['minimumReceived'],
            "originDexRouterList": quote['originDexRouterList'],
            'pmm':"1",
            'priorityFee':"0.0001",
            'quoteType':quote['quoteType'],
            'slippage':quote['realSlippage'],
            'toAmount':quote['receiveAmount'],
            'toTokenAddress':quote['toToken']['tokenContractAddress'],
            'toTokenDecimal':quote['toToken']['decimals'],
            'userWalletAddress':account.address,
        }

        for i in range(5):
            try:
                url = f"https://www.okx.com/priapi/v1/dx/trade/multi/v2/saveOrder?t={int(time.time())}"
                result = self.help.fetch_url(url=url, type='post', headers=self.headers, payload=payload)
                if int(result['code']) == 0:
                    return result['data']
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        if token_from != 'ETH':
            _amount = int(amount * 10 ** token_from_data['decimal'])
            _amount = min(_amount, get_balance(new_w3, account, token_from_data['address']))
            amount = float(_amount / (10 ** token_from_data['decimal']) * 0.999)

        quote = self.get_quote(token_from_data['address'], token_to_data['address'], amount)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        tx_ = self.get_tx(quote, account)
        if not tx_:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, float(quote['fromTokenAmount'])*10**token_from_data['decimal'], float(quote['receiveAmount'])*10**token_to_data['decimal'])
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract_approve'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract_approve'])

        value = tx_['callData'].get('value', 0)
        tx = make_tx(new_w3, account, value=int(value), to=new_w3.to_checksum_address(tx_['callData']['to']), data=tx_['callData']['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            if attempt > 5:
                return 'error'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)

#+
class Kyberswap():

    def __init__(self, w3, max_slip, helper):

        self.project = 'KYBERSWAP'
        self.headers = {
            'authority': 'meta-aggregator-api.kyberswap.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-sec-fetch-site': 'same-origin',
        }
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def get_quote(self, token_from, token_to, amount):
        token_from = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_from.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from
        token_to = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' if token_to.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to
        params = {"amountIn":str(amount),"saveGas":False,"gasInclude":True,"tokenIn":token_from,"tokenOut":token_to, "feeReceiver": '0x5f67ffa4b3f77dd16c9c34a1a82cab8daea03191', "feeAmount": 100, "chargeFeeBy": 'currency_in', 'isInBps': True}
        for i in range(5):
            try:
                url = f"https://meta-aggregator-api.kyberswap.com/linea/api/v1/routes"
                result = self.help.fetch_url(url=url, type='get', headers=self.headers, params=params)
                if int(result['code']) == 0:
                    return result['data']
            except:
                time.sleep(i * 1)
        return None

    def get_tx(self, quote, account):
        payload = {
            "deadline": int(time.time()) + 60 * 20,
            "recipient": account.address,
            "routeSummary": quote['routeSummary'],
            "sender": account.address,
            "skipSimulateTx": False,
            "slippageTolerance": int(self.max_slip * 100),
            "source": 'kyberswap'
        }

        for i in range(5):
            try:
                url = f"https://meta-aggregator-api.kyberswap.com/linea/api/v1/route/build"
                result = self.help.fetch_url(url=url, type='post', headers=self.headers, payload=payload)
                if int(result['code']) == 0:
                    return result['data']
            except:
                time.sleep(i * 1)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt = 0):

        if attempt > 0:
            time.sleep(1)
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

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'no_route'

        _amount = int(amount * 10 ** token_from_data['decimal'])
        if token_from != 'ETH':
            _amount = int(amount * 10 ** token_from_data['decimal'])
            _amount = min(_amount, get_balance(new_w3, account, token_from_data['address']))
            amount = float(_amount / (10 ** token_from_data['decimal']) * 0.999)

        quote = self.get_quote(token_from_data['address'], token_to_data['address'], _amount)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        tx_ = self.get_tx(quote, account)
        if not tx_:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        slip = (1-float(tx_['amountInUsd'])/float(tx_['amountOutUsd']))*100
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], tx_['routerAddress'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], tx_['routerAddress'])

        value = int(tx_['amountIn']) if token_from == 'ETH' else 0
        tx = make_tx(new_w3, account, value=value, to=new_w3.to_checksum_address(tx_['routerAddress']), data=tx_['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            if attempt > 5:
                return 'error'
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt+1)
        return new_w3.to_hex(hash)


class Xyfinance():

    def __init__(self, w3, max_slip, helper):
        self.project = 'XY.FINANCE'
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from, token_to, account):
        for i in range(3):
            try:
                token_from = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from
                token_to = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to
                params = {
                    'src_chain_id': '59144',
                    'src_quote_token_address': token_from,
                    'src_quote_token_amount': str(amount),
                    'dst_chain_id': '59144',
                    'dst_quote_token_address': token_to,
                    'slippage': str(int(max(1, self.max_slip))),
                    'receiver': account.address,
                    'affiliate': '0x5f67ffa4b3f77DD16C9C34A1A82CaB8dAea03191',
                    'commission_rate': 10000,
                    'src_swap_provider': 'OpenOcean V3 DexAggregator',
                }
                res = self.help.fetch_url(url='https://router-api.xy.finance/xy_router/build_tx', params=params, type='get')
                if res.get('success', False) is True:
                    return res
                elif res.get('error_code', '') == 40002:
                    return None
                time.sleep((1 * i) + i)
            except:
                time.sleep((1 * i) + i)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if attempt != 0:
            time.sleep(1)
        if attempt > 5:
            return "error"

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        try:
            _amount = int(amount * 10 ** int(token_from_data['decimals']))
        except:
            _amount = int(amount * 10 ** int(token_from_data['decimal']))

        quote = self.quote(str(_amount), token_from_data['address'], token_to_data['address'], account)
        if not quote and quote.get('success', False) is True:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, int(quote['route']['src_quote_token_amount']), int(quote['route']['dst_quote_token_amount']))
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['tx']['to'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['tx']['to'])

        tx = make_tx(new_w3, account, value=int(quote['tx']['value'], 16), to=new_w3.to_checksum_address(quote['tx']['to']), data=quote['tx']['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Metamask():

    def __init__(self, w3, max_slip, helper):
        self.project = 'METAMASK SWAP'
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip

    def quote(self, amount, token_from, token_to, account):
        for i in range(3):
            try:
                token_from = '0x0000000000000000000000000000000000000000' if token_from.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_from
                token_to = '0x0000000000000000000000000000000000000000' if token_to.lower() == '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f'.lower() else token_to
                url = f"https://swap.metaswap.codefi.network/networks/59144/trades?sourceAmount={amount}&sourceToken={token_from}&destinationToken={token_to}&slippage={str(int(max(1, self.max_slip)))}&walletAddress={account.address.lower()}&timeout=10000&enableDirectWrapping=true&includeRoute=true"
                res = self.help.fetch_url(url=url, type='get')
                if res:
                    good_results = [r for r in res if r['trade'] is not None]
                    if good_results:
                        return random.choice(good_results)
                else:
                    raise Exception
            except Exception:
                time.sleep((1 * i) + i)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if attempt != 0:
            time.sleep(1)
        if attempt > 5:
            return "error"

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        try:
            _amount = int(amount * 10 ** int(token_from_data['decimals']))
        except:
            _amount = int(amount * 10 ** int(token_from_data['decimal']))

        quote = self.quote(str(_amount), token_from_data['address'], token_to_data['address'], account)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, int(quote['sourceAmount']), int(quote['destinationAmount']))
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['trade']['to'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], quote['trade']['to'])

        tx = make_tx(new_w3, account, value=int(quote['trade']['value']), to=new_w3.to_checksum_address(quote['trade']['to']), data=quote['trade']['data'])

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

#+
class Symbiosis():

    def __init__(self, w3, max_slip, helper):
        self.project = 'SYMBIOSIS'
        self.help = helper
        self.available_tokens = tokens_data_
        self.w3 = w3
        self.max_slip = max_slip
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']),abi=swaps_data[self.project]['ABI'])

    def quote(self, token_from_data, token_to_data, amount, account):
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json',
        }

        token_from = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_from_data['symbol'] == 'ETH' else token_from_data['address']
        token_to = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' if token_to_data['symbol'] == 'ETH' else token_to_data['address']

        url = f"https://open-api.openocean.finance/v3/linea/swap_quote?inTokenAddress={token_from}&outTokenAddress={token_to}&amount={round(amount, 6)}&gasPrice=5&slippage={max(1, self.max_slip)}&account={account.address}&referrer=0x5f67ffa4b3f77DD16C9C34A1A82CaB8dAea03191"

        for i in range(7):
            try:
                res = self.help.fetch_url(url=url, type='get', headers=headers)
                if int(res['code']) == 200:
                    return res['data']
                time.sleep((1*i)+i)
            except:
                time.sleep((1*i)+i)
        return None

    def swap(self, amount, token_from, token_to, private_key, attempt=0):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if attempt != 0:
            time.sleep(1)
        if attempt > 5:
            return "error"

        try:
            token_from_data = self.available_tokens[token_from]
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        quote = self.quote(token_from_data, token_to_data, amount, account)
        if not quote:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        slip = check_slippage(self.help.get_prices_combined(), token_from, token_to, int(quote['inAmount']), int(quote['outAmount']))
        if slip > self.max_slip:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        if token_from != 'ETH':
            approve = check_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract_approve'])
            if not approve:
                make_approve(new_w3, account, self.available_tokens[token_from]['address'], swaps_data[self.project]['contract_approve'])

        func_ = getattr(self.contract.functions, 'onswap')
        token_from_address = new_w3.to_checksum_address(token_from_data['address']) if token_from_data['symbol'] != 'ETH' else '0x0000000000000000000000000000000000000000'
        args = token_from_address, int(quote['inAmount']), quote['to'], quote['to'], quote['data']

        value = int(quote['value']) + 300000000000000

        tx = make_tx(new_w3, account, value=value, func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx
        if tx == 'attempt':
            time.sleep(3)
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.swap(amount=amount, token_from=token_from, token_to=token_to, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

def initialize_swaps(classes_to_init, w3, max_slippage, helper):
    available_swaps = {
        "Syncswap": Syncswap,                                        # SYNCSWAP   |
        "Lynex": Lynex,                                              # LYNEX      |
        "Echodex": Echodex,                                          # ECHODEX    |
        "Horizon": Horizon,                                          # HORIZON    |
        "Vooi": Vooi,                                                # VOOI       |
        "Izumi": Izumi,                                              # IZUMI      |
        "Pancake": Pancake,                                          # PANCAKE    | pancakeswap.finance
        "Velocore": Velocore,                                        # VELOCORE   |
        'Sushiswap': Sushiswap,                                      # SUSHISWAP  |
        'Symbiosis': Symbiosis,                                      # SYMBIOSIS  |
        "Woofi": Woofi,                                              # WOOFI      |
        "Spaceswap": Spaceswap,                                      # SPACESWAP  |
        "Dodoex": Dodoex,                                            # DODOEX     |
        "Wowmax": Wowmax,                                            # WOWMAX     |
        "Openocean": Openocean,                                      # OPENOCEAN  | openocean.finance
        "Okx": Okx,                                                  # OKX        | okx.com/web3/dex
        "Kyberswap": Kyberswap,                                      # KYBERSWAP  | kyberswap.com
        "Xyfinance": Xyfinance,                                      # XYFINANCE  |
        "Metamask": Metamask,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, max_slippage, helper)

    return initialized_objects


