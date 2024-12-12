import random
from eth_abi import *
from helpers.utils import *
from helpers.data import tokens_data_, NULL_ADDRESS
from helpers.data import DATA_ABI, CONTRACT_DATA

#+ maybe small bugs
class Syncswap_liq():

    def __init__(self, w3, helper):
        self.project = 'SYNCSWAP'
        self.help = helper
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.factory = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_factory']), abi=swaps_data[self.project]['ABI_factory'])
        self.available_tokens = tokens_data_
        self.pools = self.get_pools()

    def get_pools(self, account=False):
        for i in range(5):
            try:
                result = self.help.fetch_url(url=f'https://api.syncswap.xyz/api/fetchers/fetchAllPools?network=lineaMainnet&quote=next', type='get')
                return result['pools']
            except:
                time.sleep(i*1)
        return {}

    def add_liq(self, amount, token_from, private_key, attempt=0):

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

        if token_from == "ETH":
            token_from = 'WETH'

        try:
            token_from_data = self.available_tokens[token_from]
        except:
            return 'error'

        if token_from != 'WETH':
            approve = check_approve(self.w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
            if not approve:
                make_approve(self.w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        pools = []
        for pool in self.pools:
            if token_from == pool['token1']['symbol'] and pool['token0']['symbol'] in list(self.available_tokens.keys()) or token_from == pool['token0']['symbol'] and pool['token1']['symbol'] in list(self.available_tokens.keys()):
                pools.append(pool)

        if not pools:
            return 'no_route'
        choosed_pool = random.choice(pools)

        if token_from == choosed_pool['token0']['symbol']:
            token_to = choosed_pool['token1']['symbol']
        else:
            token_to = choosed_pool['token0']['symbol']

        try:
            token_to_data = self.available_tokens[token_to]
        except:
            return 'error'

        amount_decimals = amount * 10 ** int(token_from_data['decimal'])
        if token_from not in ['WETH', 'ETH']:
            amount_decimals = min(amount_decimals, get_balance(self.w3, account, token_from_data['address']))

        args = [self.w3.to_checksum_address(choosed_pool['pool']),
                [[
                    token_from_data['address'] if token_from != 'WETH' else NULL_ADDRESS, int(amount_decimals)
                ],
                [
                    token_to_data['address'] if token_to != 'WETH' else NULL_ADDRESS, 0
                ]],
                f'0x000000000000000000000000{account.address[2:]}',
                0,
                NULL_ADDRESS,
                bytes.fromhex('')]

        func_ = getattr(self.contract.functions, 'addLiquidity2')

        tx = make_tx(self.w3, account, value=0 if token_from != 'WETH' else int(amount_decimals), func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

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

        good_pools = [p for p in self.pools if get_balance(self.w3, account, p['pool']) > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        approve = check_approve(self.w3, account, choosed_pool['pool'], swaps_data[self.project]['contract'])
        if not approve:
            make_approve(self.w3, account, choosed_pool['pool'], swaps_data[self.project]['contract'])

        pool_balance = get_balance(self.w3, account, choosed_pool['pool'])

        args = self.w3.to_checksum_address(choosed_pool['pool']), int(pool_balance), \
            f'0x000000000000000000000000{account.address[2:]}0000000000000000000000000000000000000000000000000000000000000001', \
            [int(0), int(0)], '0x0000000000000000000000000000000000000000', b''

        func_ = getattr(self.contract.functions, 'burnLiquidity')

        tx = make_tx(self.w3, account, value=0, func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+
class Vooi_liq():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'VOOI'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.pools = self.get_pools()

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

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
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
            token_from_pool_data = self.pools[token_from_data['address'].lower()]
        except:
            return 'error'
        _amount = int(amount * 10 ** token_from_data['decimal'])

        approve = check_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])
        if not approve:
            make_approve(new_w3, account, token_from_data['address'], swaps_data[self.project]['contract'])

        args = token_from_pool_data['id'], _amount, 0, account.address, int(time.time()+600)
        func_ = getattr(self.contract.functions, 'deposit')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        good_pools = [p for p in list(self.pools.values()) if self.contract.functions.balanceOf(account.address, p['id']).call() > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        balance = self.contract.functions.balanceOf(account.address, choosed_pool['id']).call()

        args = choosed_pool['id'], balance, 0, account.address, int(time.time()+600)
        func_ = getattr(self.contract.functions, 'withdraw')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+
class Echodex_liq():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'ECHODEX'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_liq']), abi=swaps_data[self.project]['ABI_liq'])
        self.contract_data = self.w3.eth.contract(address=self.w3.to_checksum_address(CONTRACT_DATA), abi=DATA_ABI)
        self.pools = self.get_pools()

    def get_pools(self):
        for i in range(5):
            try:
                payload = {"query":"\n      query MyQuery { pools(orderDirection: desc, orderBy: totalValueLockedUSD) { tick id token0 { id decimals name symbol totalValueLocked poolCount } token1 { id decimals name symbol poolCount totalValueLocked } feeTier liquidity sqrtPrice } }"}
                result = self.helper.fetch_url(url='https://graph-query.linea.build/subgraphs/name/echodex/exchange-v3-2',type='post', payload=payload)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol'].upper()] / self.prices[token_to['symbol'].upper()]
            except:
                time.sleep(i * 1)
        return 0

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_from_data = self.available_tokens[token_from]
        _amount = int(amount * 10 ** token_from_data['decimal'])

        user_tokens = {}
        user_tokens_ = self.contract_data.functions.getBalances(account.address).call()
        for t in user_tokens_:
            user_tokens[t[0].lower()] = {"address": t[0], "symbol": t[1], "decimal": t[2], 'balance': t[3], "amount": float(t[3] / (10 ** t[2]))}

        good_pools = []
        for p in self.pools:
            token_to = p['token0']['id'] if p['token0']['id'].lower() != token_from_data['address'].lower() else p['token1']['id']
            if p['token0']['id'].lower() == token_from_data['address'].lower() or p['token1']['id'].lower() == token_from_data['address'].lower():
                try:
                    token_to_data = user_tokens[token_to.lower()]
                    if token_to_data['balance'] > 0:
                        qoute = float(p['token0']['totalValueLocked']) / float(p['token1']['totalValueLocked']) if p['token0']['id'].lower() != token_from_data['address'].lower() else float(p['token1']['totalValueLocked']) / float(p['token0']['totalValueLocked'])
                        if int(p['tick']) == 0:
                            continue
                        good_pools.append({'pair': p['id'],'tokenA': new_w3.to_checksum_address(token_from_data['address']),"tokenB": new_w3.to_checksum_address(token_to), "amountA": _amount, "amountB": token_to_data['balance'], "fee": int(p['feeTier']), 'tick': int(p['tick']), "quote": qoute, "token_to": token_to_data})
                except:
                    pass

        if not good_pools:
            return 'no_route'
        choosed_pool = random.choice(good_pools)
        for token in ['tokenA', 'tokenB']:
            if choosed_pool[token].lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower():
                continue
            approve = check_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq'])
            if not approve:
                make_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq'])

        pair = new_w3.eth.contract(address=self.w3.to_checksum_address(choosed_pool['pair']), abi=swaps_data[self.project]['ABI_pool'])
        tick_spacing = pair.functions.tickSpacing().call()
        tick_normal = int(int(choosed_pool['tick'] / 10) * 10)
        multiplier = 0.005 if (token_from in ['USDC', 'BUSD', 'AXLUSDC', 'DAI', 'USD+', 'USDT'] and choosed_pool['token_to']['symbol'] in ['USDC', 'BUSD', 'AXLUSDC', 'DAI', 'USD+', 'USDT']) else 0.1
        tick1 = int(tick_normal - abs(tick_normal * multiplier))
        tick2 = int(tick_normal + abs(tick_normal * multiplier))
        tick1, tick2 = int(int(tick1 / tick_spacing) * tick_spacing), int(int(tick2 / tick_spacing) * tick_spacing)

        token0 = pair.functions.token0().call()
        if token0.lower() != choosed_pool['tokenA'].lower():
            amountA = choosed_pool['amountB']
            choosed_pool['amountB'] = choosed_pool['amountA']
            choosed_pool['amountA'] = amountA
            tokenA = choosed_pool['tokenB']
            choosed_pool['tokenB'] = choosed_pool['tokenA']
            choosed_pool['tokenA'] = tokenA

        quote_data = float(self.get_quote(token_from_data, choosed_pool['token_to']))
        if not quote_data:
            return 'no_data'

        amountB = int(amount * quote_data * 10 ** int(choosed_pool['token_to']['decimal']))
        if amountB < choosed_pool['amountB']:
            amountA = int(amountB / (10 ** choosed_pool['token_to']['decimal']) / quote_data * 10 ** int(token_from_data['decimal']))
            choosed_pool['amountA'] = amountA
            choosed_pool['amountB'] = amountB
        if amountB > choosed_pool['amountB']:
            amountA = int(amountB / (10 ** choosed_pool['token_to']['decimal']) / quote_data * 10 ** int(token_from_data['decimal']))
            choosed_pool['amountA'] = amountA
            amountB = int(choosed_pool['amountA'] / (10 ** token_from_data['decimal']) * quote_data * 10 ** int(choosed_pool['token_to']['decimal']))
            choosed_pool['amountB'] = amountB

        args = choosed_pool['tokenA'], choosed_pool['tokenB'], choosed_pool['fee'], tick1, tick2, choosed_pool['amountA'], choosed_pool['amountB'], 0, 0, account.address, int(time.time())

        data = []
        data.append(self.contract.encodeABI(fn_name='mint', args=[args]))
        if '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() in [choosed_pool['tokenA'].lower(), choosed_pool['tokenB'].lower()]:
            data.append(self.contract.encodeABI(fn_name='refundETH', args=[]))
            eth_value = choosed_pool['amountA'] if choosed_pool[ 'tokenA'].lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() else  choosed_pool['amountB']
        else:
            eth_value = 0

        func_ = getattr(self.contract.functions, 'multicall')

        tx = make_tx(new_w3, account, value=eth_value, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        positions_count = self.contract.functions.balanceOf(account.address).call()
        positions = [self.contract.functions.tokenOfOwnerByIndex(account.address, id).call() for id in range(positions_count)]
        good_pools = [pos for pos in positions if self.contract.functions.positions(pos).call()[7] > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        pos = self.contract.functions.positions(choosed_pool).call()
        tokens = [pos[2], pos[3]]

        data = []
        data.append(self.contract.encodeABI(fn_name='decreaseLiquidity', args=[[choosed_pool, pos[7], 0, 0, int(time.time()+600)]]))
        data.append(self.contract.encodeABI(fn_name='collect', args=[[choosed_pool, account.address, 340282366920938463463374607431768211455, 340282366920938463463374607431768211455]]))
        for token in tokens:
            if token.lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower():
                data.append(self.contract.encodeABI(fn_name='unwrapWETH9', args=[0, account.address]))
            else:
                data.append(self.contract.encodeABI(fn_name='sweepToken', args=[token, 0, account.address]))

        func_ = getattr(self.contract.functions, 'multicall')

        tx = make_tx(new_w3, account, value=0, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+-
class Horizon_liq():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'HORIZON'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_liq']), abi=swaps_data[self.project]['ABI_liq'])
        self.contract_data = self.w3.eth.contract(address=self.w3.to_checksum_address(CONTRACT_DATA), abi=DATA_ABI)
        self.pools = self.get_pools()

    def get_pools(self):
        for i in range(3):
            try:
                payload = {
                    "query": "\n      query MyQuery { pools(orderDirection: desc, orderBy: totalValueLockedUSD) { tick id token0 { id decimals name symbol totalValueLocked poolCount } token1 { id decimals name symbol poolCount totalValueLocked } feeTier liquidity sqrtPrice } }"}
                result = self.helper.fetch_url(url='https://subgraph-mainnet.horizondex.io/subgraphs/name/horizondex/horizondex-mainnet-v2', type='post', payload=payload, retries=5, timeout=5)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol'].upper()] / self.prices[token_to['symbol'].upper()]
            except:
                time.sleep(i * 1)
        return 0

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_from_data = self.available_tokens[token_from]
        _amount = int(amount * 10 ** token_from_data['decimal'])

        # if token_from == 'ETH':
        #     if get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f') < _amount:
        #         wrap = eth_wrapper(amount, 'WETH', new_w3, private_key['private_key'])

        user_tokens = {}
        user_tokens_ = self.contract_data.functions.getBalances(account.address).call()
        for t in user_tokens_:
            user_tokens[t[0].lower()] = {"address": t[0], "symbol": t[1], "decimal": t[2], 'balance': t[3], "amount": float(t[3] / (10 ** t[2]))}

        good_pools = []
        for p in self.pools:
            token_to = p['token0']['id'] if p['token0']['id'].lower() != token_from_data['address'].lower() else p['token1']['id']
            if p['token0']['id'].lower() == token_from_data['address'].lower() or p['token1']['id'].lower() == token_from_data['address'].lower():
                try:
                    token_to_data = user_tokens[token_to.lower()]
                    if token_to_data['balance'] > 0:
                        #token_to_data_amount = token_to_data['balance'] / (10 ** token_to_data['decimal'])
                        qoute = float(p['token0']['totalValueLocked']) / float(p['token1']['totalValueLocked']) if p['token0']['id'].lower() != token_from_data['address'].lower() else float(p['token1']['totalValueLocked']) / float(p['token0']['totalValueLocked'])
                        good_pools.append({'pair': p['id'],'tokenA': new_w3.to_checksum_address(token_from_data['address']),"tokenB": new_w3.to_checksum_address(token_to), "amountA": _amount, "amountB": token_to_data['balance'], "fee": int(p['feeTier']), 'tick': int(p['tick']), "quote": qoute, "token_to": token_to_data})
                except:
                    pass

        if not good_pools:
            return 'no_route'
        choosed_pool = random.choice(good_pools)
        for token in ['tokenA', 'tokenB']:
            approve = check_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq'])
            if not approve:
                make_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq'])

        pair = new_w3.eth.contract(address=self.w3.to_checksum_address(choosed_pool['pair']), abi=swaps_data[self.project]['ABI_pool'])
        current_tick = pair.functions.getPoolState().call()[2]
        tick1, tick2 = pair.functions.initializedTicks(current_tick).call()

        quote_data = float(self.get_quote(token_from_data, choosed_pool['token_to']))
        if not quote_data:
            return 'no_data'

        amountB = int(amount * quote_data * 10 ** int(choosed_pool['token_to']['decimal']) * ((100 - 10) / 100))
        if amountB < choosed_pool['amountB']:
            amountA = int(amountB / (10 ** choosed_pool['token_to']['decimal']) / quote_data * 10 ** int(token_from_data['decimal']) * ((100 - 10) / 100))
            choosed_pool['amountA'] = amountA
            choosed_pool['amountB'] = amountB

        args = choosed_pool['tokenA'], choosed_pool['tokenB'], choosed_pool['fee'], tick1, tick2, [tick1, tick2], choosed_pool['amountA'], choosed_pool['amountB'], 0, 0, account.address, int(time.time()+300)
        data = []
        data.append(self.contract.encodeABI(fn_name='mint', args=[args]))
        if '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() in [choosed_pool['tokenA'].lower(), choosed_pool['tokenB'].lower()]:
            data.append(self.contract.encodeABI(fn_name='refundEth', args=[]))
            eth_value = choosed_pool['amountA'] if choosed_pool['tokenA'].lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() else choosed_pool['amountB']
        else:
            eth_value = 0

        func_ = getattr(self.contract.functions, 'multicall')

        tx = make_tx(new_w3, account, value=eth_value, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx
        if tx == 'order':
            args = choosed_pool['tokenB'], choosed_pool['tokenA'], choosed_pool['fee'], tick1, tick2, [tick1, tick2], choosed_pool['amountB'], choosed_pool['amountA'], 0, 0, account.address, int(time.time() + 300)
            data = []
            data.append(self.contract.encodeABI(fn_name='mint', args=[args]))
            if '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() in [choosed_pool['tokenA'].lower(), choosed_pool['tokenB'].lower()]:
                data.append(self.contract.encodeABI(fn_name='refundEth', args=[]))
                eth_value = choosed_pool['amountA'] if choosed_pool['tokenA'].lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() else choosed_pool['amountB']
            else:
                eth_value = 0
            tx = make_tx(new_w3, account, value=eth_value, func=func_, args=data, args_positioning=False)
            if tx == "low_native" or not tx:
                return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        positions_count = self.contract.functions.balanceOf(account.address).call()
        positions = [self.contract.functions.tokenOfOwnerByIndex(account.address, id).call() for id in range(positions_count)]
        good_pools = [pos for pos in positions if self.contract.functions.positions(pos).call()[0][5] > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        pos = self.contract.functions.positions(choosed_pool).call()

        tokens = [pos[1][0], pos[1][2]]

        data = []
        data.append(self.contract.encodeABI(fn_name='removeLiquidity', args=[[choosed_pool, pos[0][5], 0, 0, int(time.time()+300)]]))
        for token in tokens:
            if token.lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower():
                data.append(self.contract.encodeABI(fn_name='unwrapWeth', args=[0, account.address]))
            else:
                data.append(self.contract.encodeABI(fn_name='transferAllTokens', args=[token, 0, account.address]))

        func_ = getattr(self.contract.functions, 'multicall')

        tx = make_tx(new_w3, account, value=0, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+
class Lynex_liq():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'LYNEX'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_liq']), abi=swaps_data[self.project]['ABI_liq'])
        self.contract_liq = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_liq2']), abi=swaps_data[self.project]['ABI_liq2'])
        self.contract_data = self.w3.eth.contract(address=self.w3.to_checksum_address(CONTRACT_DATA), abi=DATA_ABI)
        self.pools = self.get_pools()
        self.gammas = {'0x3cb104f044db23d6513f2a6100a1997fa5e3f587': '0x0b15a5e3ca0d4b492c3b476d0f807535f9b72079',
                       '0x8611456f845293edd3f5788277f00f7c05ccc291': '0xf3b1125c8505f038503e002e61a78253610d4f60',
                       '0xd4d4d99b26e7c96c70f32b417870aad2d51374a5': '0xd6cc4a33da7557a629e819c68fb805ddb225f517',
                       '0x8e80016b025c89a6a270b399f5ebfb734be58ada': '0x8a9570ec97534277ade6e46d100939fbce4968f0',
                       '0x1203688929f72c459007508b1da79a5eb20a6165': '0x8421c6102ee8a147facc01977df3b159f7921d54',
                       '0x704c442bfef3b6b31559085fc67083ca64e30b5c': '0x32e27ff479454e32868ff67ee9f06bafdc1e908f',
                       "0xc4deb765f13f47c6bb1279a7326696b67786c15a": '0x6e9d701fb6478ed5972a37886c2ba6c82a4cbb4c'}

    def get_pools(self):
        for i in range(5):
            try:
                payload = {"query":"\n      query MyQuery { pools(first: 25, orderBy: volumeUSD, orderDirection: desc) { volumeUSD fee feeGrowthGlobal0X128 feeGrowthGlobal1X128 id liquidity token0 { decimals id name symbol } token1 { decimals id name symbol } tick tickSpacing } }"}
                result = self.helper.fetch_url(url='https://graph-query.linea.build/subgraphs/name/cryptoalgebra/analytics',type='post', payload=payload)
                return result['data']['pools']
            except:
                time.sleep(i * 1)
        return []

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol'].upper()] / self.prices[token_to['symbol'].upper()]
            except:
                time.sleep(i * 1)
        return 0

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_from_data = self.available_tokens[token_from]
        _amount = int(amount * 10 ** token_from_data['decimal'])

        # if token_from == 'ETH':
        #     if get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f') < _amount:
        #         wrap = eth_wrapper(amount, 'WETH', new_w3, private_key['private_key'])

        user_tokens = {}
        user_tokens_ = self.contract_data.functions.getBalances(account.address).call()
        for t in user_tokens_:
            user_tokens[t[0].lower()] = {"address": t[0], "symbol": t[1], "decimal": t[2], 'balance': t[3], "amount": float(t[3] / (10 ** t[2]))}

        good_pools = []
        for p in self.pools:
            token_to = p['token0']['id'] if p['token0']['id'].lower() != token_from_data['address'].lower() else p['token1']['id']
            if p['token0']['id'].lower() == token_from_data['address'].lower() or p['token1']['id'].lower() == token_from_data['address'].lower():
                try:
                    token_to_data = user_tokens[token_to.lower()]
                    if token_to_data['balance'] > 0:
                        gamma_pool = None#self.gammas[p['id'].lower()]
                        good_pools.append({'gamma': gamma_pool, 'pair': p['id'],'tokenA': new_w3.to_checksum_address(token_from_data['address']),"tokenB": new_w3.to_checksum_address(token_to), "amountA": _amount, "amountB": token_to_data['balance'], 'token_to': token_to_data, 'tick': int(p['tick'])})
                except:
                    pass

        if not good_pools:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        quote_data = float(self.get_quote(token_from_data, choosed_pool['token_to']))
        if not quote_data:
            return 'no_data'

        for token in ['tokenA', 'tokenB']:
            approve = check_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq2'])
            if not approve:
                make_approve(new_w3, account, choosed_pool[token], swaps_data[self.project]['contract_liq2'])

        amountB = int(amount * quote_data * 10 ** int(choosed_pool['token_to']['decimal']))
        if amountB < choosed_pool['amountB']:
            amountA = int(amountB / (10 ** choosed_pool['token_to']['decimal']) / quote_data * 10 ** int(token_from_data['decimal']))
            choosed_pool['amountA'] = amountA
            choosed_pool['amountB'] = amountB
        if amountB > choosed_pool['amountB']:
            amountA = int(amountB / (10 ** choosed_pool['token_to']['decimal']) / quote_data * 10 ** int(token_from_data['decimal']))
            choosed_pool['amountA'] = amountA
            amountB = int(choosed_pool['amountA'] / (10 ** token_from_data['decimal']) * quote_data * 10 ** int(choosed_pool['token_to']['decimal']))
            choosed_pool['amountB'] = amountB

        pair = new_w3.eth.contract(address=self.w3.to_checksum_address(choosed_pool['pair']), abi=swaps_data[self.project]['ABI_pool'])
        tick_spacing = pair.functions.tickSpacing().call()
        tick_normal = int(int(choosed_pool['tick'] / 10) * 10)
        multiplier = 0.005 if (token_from in ['USDC', 'BUSD', 'AXLUSDC', 'DAI', 'USD+', 'USDT'] and choosed_pool['token_to']['symbol'] in ['USDC', 'BUSD', 'AXLUSDC', 'DAI', 'USD+', 'USDT']) else 0.1
        tick1 = int(tick_normal - abs(tick_normal * multiplier))
        tick2 = int(tick_normal + abs(tick_normal * multiplier))
        tick1, tick2 = int(int(tick1 / tick_spacing) * tick_spacing), int(int(tick2 / tick_spacing) * tick_spacing)

        token0 = pair.functions.token0().call()
        if token0.lower() != choosed_pool['tokenA'].lower():
            amountA = choosed_pool['amountB']
            choosed_pool['amountB'] = choosed_pool['amountA']
            choosed_pool['amountA'] = amountA
            tokenA = choosed_pool['tokenB']
            choosed_pool['tokenB'] = choosed_pool['tokenA']
            choosed_pool['tokenA'] = tokenA

        args = choosed_pool['tokenA'], choosed_pool['tokenB'], tick1, tick2, choosed_pool['amountA'], choosed_pool['amountB'], 0, 0, account.address, int(time.time()+600)
        data = []
        data.append(self.contract_liq.encodeABI(fn_name='mint', args=[args]))
        if '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() in [choosed_pool['tokenA'].lower(), choosed_pool['tokenB'].lower()]:
            data.append(self.contract_liq.encodeABI(fn_name='refundNativeToken', args=[]))
            eth_value = choosed_pool['amountA'] if choosed_pool['tokenA'].lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower() else choosed_pool['amountB']
        else:
            eth_value = 0

        func_ = getattr(self.contract_liq.functions, 'multicall')

        tx = make_tx(new_w3, account, value=eth_value, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        positions_count = self.contract_liq.functions.balanceOf(account.address).call()
        positions = [self.contract_liq.functions.tokenOfOwnerByIndex(account.address, id).call() for id in  range(positions_count)]
        good_pools = [pos for pos in positions if self.contract_liq.functions.positions(pos).call()[6] > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        pos = self.contract_liq.functions.positions(choosed_pool).call()
        tokens = [pos[2], pos[3]]

        data = []
        data.append(self.contract_liq.encodeABI(fn_name='decreaseLiquidity', args=[[choosed_pool, pos[6], 0, 0, int(time.time() + 600)]]))
        data.append(self.contract_liq.encodeABI(fn_name='collect', args=[[choosed_pool, account.address, 340282366920938463463374607431768211455, 340282366920938463463374607431768211455]]))
        for token in tokens:
            if token.lower() == '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'.lower():
                data.append(self.contract_liq.encodeABI(fn_name='unwrapWNativeToken', args=[0, account.address]))
            else:
                data.append(self.contract_liq.encodeABI(fn_name='sweepToken', args=[token, 0, account.address]))

        func_ = getattr(self.contract_liq.functions, 'multicall')

        tx = make_tx(new_w3, account, value=0, func=func_, args=data, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+-
class Velocore_liq():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'VELOCORE'
        self.available_tokens = tokens_data_
        self.contract_vault = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_vault']),abi=swaps_data[self.project]['ABI_vault'])
        self.contract_factory = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_factory']),abi=swaps_data[self.project]['ABI_factory'])
        self.contract_data = self.w3.eth.contract(address=self.w3.to_checksum_address(CONTRACT_DATA), abi=DATA_ABI)
        self.contract_data_ = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_data']), abi=swaps_data[self.project]['ABI_data'])
        self.max_value = 170141183460469231731687303715884105727

    def get_pools(self, account):
        for i in range(5):
            try:
                pools = {}
                pool_len = self.contract_data_.functions.canonicalPoolLength().call()
                pools_ = self.contract_data_.functions.canonicalPools(account.address, 0, pool_len-1).call()
                for pool in pools_:
                    try:
                        pools[pool[0]] = pool[1]
                    except:
                        pass
                return pools
            except:
                time.sleep(1)
        return {}

    def get_quote(self, token_from, token_to):
        for i in range(5):
            try:
                self.prices = self.helper.get_prices_combined()
                return self.prices[token_from['symbol'].upper()] / self.prices[token_to['symbol'].upper()]
            except:
                time.sleep(i * 1)
        return 0

    def get_packed_pool(self, address):
        operation_types = {"swap": 0, "stake": 1}
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

    def get_tx_params(self, pool_address, token_from, token_to, amount, amount_out, single=False, packed=False):
        amount_types = {'exactly': 0, 'at_most': 1, 'all': 2, }

        pool_packed = self.get_packed_pool(pool_address)
        if not packed:
            from_token_ref = self.get_packed_token(token_from)
            to_token_ref = self.get_packed_token(token_to)
        else:
            from_token_ref = token_from
            to_token_ref = token_to

        token_ref = sorted([from_token_ref, pool_packed]) if single else sorted([from_token_ref, to_token_ref, pool_packed])
        if packed:
            token_ref = sorted([from_token_ref, pool_packed])

        deposit = [0] * len(token_ref)

        if single:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref), amount_type=amount_types['exactly'],normalized_amount=amount)
            to_token_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['at_most'], normalized_amount=0 if single else amount_out)
            pool_info = None
        elif not single and not packed:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref),amount_type=amount_types['exactly'],normalized_amount=amount)
            to_token_info = self.get_packed_token_information(index=token_ref.index(to_token_ref),amount_type=amount_types['exactly'],normalized_amount=amount_out)
            pool_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['at_most'], normalized_amount=0)
        else:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref), amount_type=amount_types['at_most'], normalized_amount=0)
            pool_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['exactly'], normalized_amount=amount_out)

        if not packed:
            token_info = sorted([from_token_info, to_token_info]) if single else sorted([from_token_info, to_token_info, pool_info])
        else:
            token_info = sorted([from_token_info, pool_info])

        return [token_ref, deposit, [[pool_packed, token_info, '0x']]]

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_from_data = self.available_tokens[token_from]
        _amount = int(amount * 10 ** token_from_data['decimal'])

        user_tokens = {}
        user_tokens_ = self.contract_data.functions.getBalances(account.address).call()
        for t in user_tokens_:
            user_tokens[t[0].lower()] = {"address": t[0], "symbol": t[1], "decimal": t[2], 'balance': t[3], "amount": float(t[3] / (10 ** t[2]))}

        good_pools = []
        for token_ in user_tokens.values():
            if token_['symbol'].lower() == token_from_data['symbol'].lower() or (token_['symbol'] == 'WETH' and token_from == 'ETH'):
                continue
            try:
                pool_address = self.contract_factory.functions.pools(self.get_packed_token(token_from_data), self.get_packed_token(token_)).call()
                if (pool_address != NULL_ADDRESS) and (token_['symbol'] in [token['symbol'] for token in tokens_data_.values() if token['liq']]):
                    good_pools.append({"pool": pool_address, "token_from": token_from_data, "token_to": token_})
            except:
                pass

        if not good_pools:
            return 'no_route'

        choosed_pool = random.choice(good_pools)

        quote_data = float(self.get_quote(token_from_data, choosed_pool['token_to']))
        if not quote_data:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        min_amount = int(amount * quote_data * 10 ** int(choosed_pool['token_to']['decimal']))
        min_amount = min(choosed_pool['token_to']['balance'], min_amount)

        for token in ['token_to', 'token_from']:
            if choosed_pool[token]['address'].lower() in ['0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'.lower(), '0x0000000000000000000000000000000000000000']:
                continue
            approve = check_approve(new_w3, account, choosed_pool[token]['address'], swaps_data[self.project]['contract_vault'])
            if not approve:
                make_approve(new_w3, account, choosed_pool[token]['address'], swaps_data[self.project]['contract_vault'])

        args = self.get_tx_params(choosed_pool['pool'], token_from_data, choosed_pool['token_to'], _amount, min_amount)

        func_ = getattr(self.contract_vault.functions, 'execute')

        if token_from == 'ETH':
            eth_value = _amount
        elif choosed_pool['token_to']['symbol'] in ['ETH', 'WETH']:
            eth_value = min_amount
        else:
            eth_value = 0

        tx = make_tx(new_w3, account, value=eth_value, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        pools = self.get_pools(account)
        good_pools = [data for p, data in pools.items() if get_balance(new_w3, account, new_w3.to_checksum_address(p), ignore_exception=True) > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        approve = check_approve(new_w3, account, choosed_pool[0], swaps_data[self.project]['contract_vault'])
        if not approve:
            make_approve(new_w3, account, choosed_pool[0], swaps_data[self.project]['contract_vault'])

        token_from = f"0x{choosed_pool[4][0].hex()}"
        token_to = f"0x{choosed_pool[4][1].hex()}"
        balance = get_balance(new_w3, account, new_w3.to_checksum_address(choosed_pool[0]))

        args = self.get_tx_params(choosed_pool[0], token_to if 'eeeeeee' in token_to else token_from, token_from if 'eeeeee' in token_to else token_to, 0, balance, packed=True)
        func_ = getattr(self.contract_vault.functions, 'execute')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)

#+
class Xyfinance_liq_VOAYGE():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'XYFINANCE'
        self.available_tokens = tokens_data_
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract']), abi=swaps_data[self.project]['ABI'])
        self.liq_token = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['liq_token']), abi=TOKEN_ABI)
        self.agr_cont = self.w3.eth.contract(address=self.w3.to_checksum_address('0xcA11bde05977b3631167028862bE2a173976CA11'), abi='[{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"aggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes[]","name":"returnData","type":"bytes[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"allowFailure","type":"bool"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call3[]","name":"calls","type":"tuple[]"}],"name":"aggregate3","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"allowFailure","type":"bool"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call3Value[]","name":"calls","type":"tuple[]"}],"name":"aggregate3Value","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"blockAndAggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes32","name":"blockHash","type":"bytes32"},{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"getBasefee","outputs":[{"internalType":"uint256","name":"basefee","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getBlockHash","outputs":[{"internalType":"bytes32","name":"blockHash","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getBlockNumber","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getChainId","outputs":[{"internalType":"uint256","name":"chainid","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockCoinbase","outputs":[{"internalType":"address","name":"coinbase","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockDifficulty","outputs":[{"internalType":"uint256","name":"difficulty","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockGasLimit","outputs":[{"internalType":"uint256","name":"gaslimit","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockTimestamp","outputs":[{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"getEthBalance","outputs":[{"internalType":"uint256","name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getLastBlockHash","outputs":[{"internalType":"bytes32","name":"blockHash","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bool","name":"requireSuccess","type":"bool"},{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"tryAggregate","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bool","name":"requireSuccess","type":"bool"},{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"tryBlockAndAggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes32","name":"blockHash","type":"bytes32"},{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"}]')

    def wait_for_balance_change(self, account, prev_balance):
        while True:
            try:
                new_balance = self.liq_token.functions.balanceOf(account.address).call()
                if new_balance > prev_balance:
                    return new_balance
                else:
                    time.sleep(random.uniform(150, 180))
            except:
                time.sleep(random.uniform(30, 60))

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if token_from != 'ETH':
            return 'error'

        _amount = int(amount * 10 ** 18)

        prev_balance = get_balance(new_w3, account, swaps_data[self.project]['liq_token'])
        if _amount * 0.9 < prev_balance:
            return True

        args = _amount
        func_ = getattr(self.contract.functions, 'deposit')

        dep_gas_lim = self.contract.functions.completeDepositGasLimit().call()
        current_gas = new_w3.eth.gas_price
        add_fee = int(round(current_gas / 1000000000) * 1000000000 * dep_gas_lim)

        tx = make_tx(new_w3, account, value=int(_amount + add_fee), func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)

        self.wait_for_balance_change(account, prev_balance)

        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_balance = get_balance(new_w3, account, swaps_data[self.project]['liq_token'])
        eth_balance_before = new_w3.eth.get_balance(account.address)

        if token_balance == 0:
            return 'error'

        approve = check_approve(new_w3, account, swaps_data[self.project]['liq_token'],swaps_data[self.project]['contract'])
        if not approve:
            make_approve(new_w3, account, swaps_data[self.project]['liq_token'], swaps_data[self.project]['contract'])

        args = token_balance
        func_ = getattr(self.contract.functions, 'withdraw')

        wd_gas_lim = self.contract.functions.completeWithdrawGasLimit().call()
        current_gas = new_w3.eth.gas_price
        add_fee = int(round(current_gas / 1000000000) * 1000000000 * wd_gas_lim)

        tx = make_tx(new_w3, account, value=add_fee, func=func_, args=args, args_positioning=False)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)

        eth_balance_after = wait_for_balance_change(new_w3, account.address, eth_balance_before)

        return new_w3.to_hex(hash)

#+-
class Velocore_liq_VOAYGE():

    def __init__(self, w3, helper):
        self.w3 = w3
        self.helper = helper
        self.project = 'VELOCORE'
        self.available_tokens = tokens_data_
        self.contract_vault = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_vault']),abi=swaps_data[self.project]['ABI_vault'])
        self.contract_factory = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_factory']),abi=swaps_data[self.project]['ABI_factory'])
        self.contract_data = self.w3.eth.contract(address=self.w3.to_checksum_address(CONTRACT_DATA), abi=DATA_ABI)
        self.contract_data_ = self.w3.eth.contract(address=self.w3.to_checksum_address(swaps_data[self.project]['contract_data']), abi=swaps_data[self.project]['ABI_data'])
        self.max_value = 170141183460469231731687303715884105727

    def get_pools(self, account):
        for i in range(5):
            try:
                pools = {}
                pool_len = self.contract_data_.functions.canonicalPoolLength().call()
                pools_ = self.contract_data_.functions.canonicalPools(account.address, 0, pool_len-1).call()
                for pool in pools_:
                    try:
                        pools[pool[0]] = pool[1]
                    except:
                        pass
                return pools
            except:
                time.sleep(1)
        return {}

    def get_packed_pool(self, address):
        operation_types = {"swap": 0, "stake": 1}
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

    def get_tx_params(self, pool_address, token_from, token_to, amount, amount_out, single=False, packed=False):
        amount_types = {'exactly': 0, 'at_most': 1, 'all': 2, }

        pool_packed = self.get_packed_pool(pool_address)
        if not packed:
            from_token_ref = self.get_packed_token(token_from)
            to_token_ref = self.get_packed_token(token_to)
        else:
            from_token_ref = token_from
            to_token_ref = token_to

        token_ref = sorted([from_token_ref, pool_packed]) if single else sorted([from_token_ref, to_token_ref, pool_packed])
        if packed:
            token_ref = sorted([from_token_ref, pool_packed])

        deposit = [0] * len(token_ref)

        if single:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref), amount_type=amount_types['exactly'],normalized_amount=amount)
            to_token_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['at_most'], normalized_amount=0 if single else amount_out)
            pool_info = None
        elif not single and not packed:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref),amount_type=amount_types['exactly'],normalized_amount=amount)
            to_token_info = self.get_packed_token_information(index=token_ref.index(to_token_ref),amount_type=amount_types['exactly'],normalized_amount=amount_out)
            pool_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['at_most'], normalized_amount=0)
        else:
            from_token_info = self.get_packed_token_information(index=token_ref.index(from_token_ref), amount_type=amount_types['at_most'], normalized_amount=0)
            pool_info = self.get_packed_token_information(index=token_ref.index(pool_packed), amount_type=amount_types['exactly'], normalized_amount=amount_out)


        if not packed:
            token_info = sorted([from_token_info, to_token_info]) if single else sorted([from_token_info, to_token_info, pool_info])
        else:
            token_info = sorted([from_token_info, pool_info])

        return [token_ref, deposit, [[pool_packed, token_info, '0x']]]

    def add_liq(self, amount, token_from, private_key, attempt=0):

        if attempt > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_from_data = self.available_tokens[token_from]
        _amount = int(amount * 10 ** token_from_data['decimal'])

        user_tokens = {}
        user_tokens_ = self.contract_data.functions.getBalances(account.address).call()
        for t in user_tokens_:
            user_tokens[t[0].lower()] = {"address": t[0], "symbol": t[1], "decimal": t[2], 'balance': t[3], "amount": float(t[3] / (10 ** t[2]))}

        good_pools = []
        for token_ in user_tokens.values():
            if token_['symbol'].lower() == token_from_data['symbol'].lower() or (token_['symbol'] == 'WETH' and token_from == 'ETH'):
                continue
            if token_['symbol'] not in ['USDT', 'USDC']:
                continue
            try:
                pool_address = self.contract_factory.functions.pools(self.get_packed_token(token_from_data), self.get_packed_token(token_)).call()
                if (pool_address != NULL_ADDRESS) and (token_['symbol'] in [token['symbol'] for token in tokens_data_.values() if token['liq']]):
                    good_pools.append({"pool": pool_address, "token_from": token_from_data, "token_to": token_})
            except:
                pass

        if not good_pools:
            return 'no_route'

        choosed_pool = random.choice(good_pools)

        min_amount = 0

        args = self.get_tx_params(choosed_pool['pool'], token_from_data, choosed_pool['token_to'], _amount, min_amount, single=True)

        func_ = getattr(self.contract_vault.functions, 'execute')

        if token_from == 'ETH':
            eth_value = _amount
        elif choosed_pool['token_to']['symbol'] in ['ETH', 'WETH']:
            eth_value = min_amount
        else:
            eth_value = 0

        tx = make_tx(new_w3, account, value=eth_value, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.add_liq(amount=amount, token_from=token_from, private_key=private_key, attempt=attempt + 1)
        return new_w3.to_hex(hash)

    def rem_liq(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        pools = self.get_pools(account)
        good_pools = [data for p, data in pools.items() if get_balance(new_w3, account, new_w3.to_checksum_address(p), ignore_exception=True) > 0]
        if len(good_pools) == 0:
            return 'no_route'
        choosed_pool = random.choice(good_pools)

        approve = check_approve(new_w3, account, choosed_pool[0], swaps_data[self.project]['contract_vault'])
        if not approve:
            make_approve(new_w3, account, choosed_pool[0], swaps_data[self.project]['contract_vault'])

        token_from = f"0x{choosed_pool[4][0].hex()}"
        token_to = f"0x{choosed_pool[4][1].hex()}"
        balance = get_balance(new_w3, account, new_w3.to_checksum_address(choosed_pool[0]))

        args = self.get_tx_params(choosed_pool[0], token_to if 'eeeeeee' in token_to else token_from, token_from if 'eeeeee' in token_to else token_to, 0, balance, packed=True)
        func_ = getattr(self.contract_vault.functions, 'execute')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.rem_liq(private_key=private_key)
        return new_w3.to_hex(hash)


def initialize_liquidity(classes_to_init, w3, helper):
    available_swaps = {
        "Velocore_liq": Velocore_liq,
        "Lynex_liq": Lynex_liq,
        "Horizon_liq": Horizon_liq,
        "Echodex_liq": Echodex_liq,
        "Vooi_liq": Vooi_liq,
        "Syncswap_liq": Syncswap_liq,
        "XyfinanceVoayge": Xyfinance_liq_VOAYGE,
        "VelocoreVoayge": Velocore_liq_VOAYGE,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, helper)

    return initialized_objects

