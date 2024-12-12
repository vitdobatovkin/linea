import hmac
import json
import hashlib
import random
from helpers.utils import *
from helpers.data import markets_data, NULL_ADDRESS
from eth_account.messages import encode_defunct, encode_structured_data
from eth_account import Account
from datetime import datetime, timedelta

class Element():

    def __init__(self, w3, logger, helper):
        self.help = helper
        self.session = self.help.get_tls_session()
        self.w3 = w3
        self.project = 'ELEMENT'
        self.logger = logger
        self.contract = w3.eth.contract(address=w3.to_checksum_address(markets_data[self.project]['contract']), abi=markets_data[self.project]['ABI'])

    def generate_xapi_signature(self, api_key='zQbYj7RhC1VHIBdWU63ki5AJKXloamDT', secret='UqCMpfGn3VyQEdsjLkzJv9tNlgbKFD7O'):
        random_number = random.randint(1000, 9999)
        timestamp = int(time.time())
        message = f"{api_key}{random_number}{timestamp}"
        signature = hmac.new(bytes(secret, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
        return f"{signature}.{random_number}.{timestamp}"

    def get_headers(self, auth=False):
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
            'x-viewer-chainmid': '901',
        }
        if auth:
            headers['auth'] = auth
        return headers

    def get_nonce(self, account):
        for i in range(3):
            try:
                payload = {"query":"\n    query GetNonce($address: Address!, $chain: Chain!, $chainId: ChainId!) {\n        user(identity: { address: $address, blockChain: { chain: $chain, chainId: $chainId } }) {\n            nonce\n        }\n    }\n","variables":{"address":f"{account.address}","chain":"linea","chainId":"0xE708"}}
                result = self.help.fetch_tls(session = self.help.get_tls_session(), url='https://api.element.market/graphql', type='post', payload=payload, headers=self.get_headers())
                return result['data']['user']['nonce']
            except:
                time.sleep((i + 1) * i)
        return None

    def get_auth(self, nonce, account):
        for i in range(3):
            message_ = f'Welcome to Element!\n   \nClick "Sign" to sign in. No password needed!\n   \nI accept the Element Terms of Service: \n https://element.market/tos\n   \nWallet address:\n{account.address.lower()}\n   \nNonce:\n{str(nonce)}'
            message = message_.encode()
            message_to_sign = encode_defunct(primitive=message)
            signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
            sig = signed_message.signature.hex()
            json_data = {
                'query': '\n    mutation LoginAuth($identity: IdentityInput!, $message: String!, $signature: String!) {\n        auth {\n            login(input: { identity: $identity, message: $message, signature: $signature }) {\n                token\n            }\n        }\n    }\n',
                'variables': {
                    'identity': {
                        'address': account.address.lower(),
                        'blockChain': {
                            'chain': 'eth',
                            'chainId': '0x1',
                        },
                    },
                    'message': f'Welcome to Element!\n   \nClick "Sign" to sign in. No password needed!\n   \nI accept the Element Terms of Service: \n https://element.market/tos\n   \nWallet address:\n{account.address.lower()}\n   \nNonce:\n{str(nonce)}',
                    'signature': sig,
                },
            }
            result = self.help.fetch_tls(session = self.session, url='https://api.element.market/graphql', type='post', payload=json_data, headers=self.get_headers())
            return result['data']['auth']['login']['token']

        return None

    def get_collection(self, auth):
        for i in range(3):
            try:
                json_data = {"operationName":"SearchCollectionListAll",
                             "variables":
                                 {"first":50,
                                  "verified":True,
                                  "sortBy":"SevenDayAmount",
                                  "blockChains":
                                      [{"chain":"linea","chainId":"0xE708"}]},
                             "query":"query SearchCollectionListAll($before: String, $after: String, $first: Int, $last: Int, $querystring: String, $categorySlugs: [String!], $sortBy: CollectionSearchSortBy, $blockChains: [BlockChainInput!], $verified: Boolean) {\n  collectionSearch(\n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    input: {querystring: $querystring, sortBy: $sortBy, categorySlugs: $categorySlugs, verified: $verified, blockChains: $blockChains}\n  ) {\n    edges {\n      cursor\n      node {\n        name\n        imageUrl\n        slug\n        isVerified\n        featuredImageUrl\n        bannerImageUrl\n        stats(realtime: true) {\n          stats1D {\n            saleCount\n            floorPrice\n            floorPriceRatio\n            volume\n            coin {\n              name\n              address\n              icon\n            }\n          }\n        }\n      }\n    }\n    pageInfo {\n      startCursor\n      endCursor\n      hasPreviousPage\n      hasNextPage\n    }\n  }\n}\n"}
                result = self.help.fetch_tls(session = self.session, url = 'https://api.element.market/graphql?args=SearchCollectionListAll', type='post', headers=self.get_headers(auth), payload=json_data)
                eligeble_collections = []
                for y in result['data']['collectionSearch']['edges']:
                    try:
                        if int(y["node"]['stats']['stats1D']['saleCount']) > 0 and float(y["node"]['stats']['stats1D']['floorPrice']) <= self.max_price:
                            eligeble_collections.append(y['node'])
                    except:
                        pass
                return random.choice(eligeble_collections)
            except:
                time.sleep((i+1)*i)
        return None

    def get_item(self, slug, auth):
        for i in range(5):
            try:
                headers = self.get_headers(auth=auth)
                params = {
                    'args': 'AssetsListForCollectionV2',
                }
                json_data = {
                    'operationName': 'AssetsListForCollectionV2',
                    'variables': {
                        'realtime': False,
                        'thirdStandards': [],
                        'collectionSlugs': [
                            slug,
                        ],
                        'sortAscending': False,
                        'sortBy': 'PriceLowToHigh',
                        'toggles': [
                            'BUY_NOW',
                        ],
                        'first': 36,
                        'isPendingTx': True,
                        'isTraits': False,
                    },
                    'query': 'query AssetsListForCollectionV2($before: String, $after: String, $first: Int, $last: Int, $querystring: String, $categorySlugs: [String!], $collectionSlugs: [String!], $sortBy: SearchSortBy, $sortAscending: Boolean, $toggles: [SearchToggle!], $ownerAddress: Address, $creatorAddress: Address, $blockChains: [BlockChainInput!], $paymentTokens: [String!], $priceFilter: PriceFilterInput, $traitFilters: [AssetTraitFilterInput!], $contractAliases: [String!], $thirdStandards: [String!], $uiFlag: SearchUIFlag, $markets: [String!], $isTraits: Boolean!, $isPendingTx: Boolean!, $noPending: Boolean) {\n  search: searchV2(\n    \n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    search: {querystring: $querystring, categorySlugs: $categorySlugs, collectionSlugs: $collectionSlugs, sortBy: $sortBy, sortAscending: $sortAscending, toggles: $toggles, ownerAddress: $ownerAddress, creatorAddress: $creatorAddress, blockChains: $blockChains, paymentTokens: $paymentTokens, priceFilter: $priceFilter, traitFilters: $traitFilters, contractAliases: $contractAliases, uiFlag: $uiFlag, markets: $markets, noPending: $noPending}\n  ) {\n    totalCount\n    edges {\n      cursor\n      node {\n        asset {\n          chain\n          chainId\n          contractAddress\n          tokenId\n          tokenType\n          name\n          imagePreviewUrl\n          animationUrl\n          rarityRank\n          assetOwners(first: 1) {\n            ...AssetOwnersEdges\n          }\n          orderData(standards: $thirdStandards) {\n            bestAsk {\n              ...BasicOrder\n            }\n            bestBid {\n              ...BasicOrder\n            }\n          }\n          assetEventData {\n            lastSale {\n              lastSalePrice\n              lastSalePriceUSD\n              lastSaleTokenContract {\n                name\n                address\n                icon\n                decimal\n                accuracy\n              }\n            }\n          }\n          pendingTx @include(if: $isPendingTx) {\n            time\n            hash\n            gasFeeMax\n            gasFeePrio\n            txFrom\n            txTo\n            market\n          }\n          traits @include(if: $isTraits) {\n            trait\n            numValue\n          }\n          collection {\n            slug\n            rarityEnable\n            categories {\n              slug\n            }\n          }\n          suspiciousStatus\n          uri\n        }\n      }\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      startCursor\n      endCursor\n    }\n  }\n}\n\nfragment BasicOrder on OrderV3Type {\n  __typename\n  chain\n  chainId\n  chainMId\n  expirationTime\n  listingTime\n  maker\n  taker\n  side\n  saleKind\n  paymentToken\n  quantity\n  priceBase\n  priceUSD\n  price\n  standard\n  contractAddress\n  tokenId\n  schema\n  extra\n  paymentTokenCoin {\n    name\n    address\n    icon\n    chain\n    chainId\n    decimal\n    accuracy\n  }\n}\n\nfragment AssetOwnersEdges on AssetOwnershipTypeConnection {\n  __typename\n  edges {\n    cursor\n    node {\n      chain\n      chainId\n      owner\n      balance\n      account {\n        identity {\n          address\n          blockChain {\n            chain\n            chainId\n          }\n        }\n        user {\n          id\n          address\n          profileImageUrl\n          userName\n        }\n        info {\n          profileImageUrl\n          userName\n        }\n      }\n    }\n  }\n}\n',
                }
                result = self.help.fetch_tls(session = self.session, url = 'https://api.element.market/graphql', type='post', headers=headers, params=params, payload=json_data)
                for i in result['data']['search']['edges']:
                    return i['node']['asset']
            except:
                time.sleep((i + 1) * i)
        return None

    def get_buy_data(self, contract, token_id, type, auth, account):
        for i in range(5):
            try:
                type = 'buyERC721Ex' if type == 'ERC721' else 'buyERC1155Ex'
                headers = self.get_headers()
                json_data = {
                    'chainMId': 901,
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
                result = self.help.fetch_tls(session=self.help.get_tls_session(), url='https://api.element.market/v3/orders/exSwapTradeDataByItem', type='post', headers=headers, payload=json_data)
                return result['data']['commonData'][0]
            except:
                time.sleep((i + 1) * i)
        return None

    def buy_nft(self, private_key, max_price, attempt=0, auth=None):

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
        self.max_price = max_price

        nonce = self.get_nonce(account)
        if not nonce:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)
        auth = self.get_auth(nonce, account)
        if not auth:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        collection = self.get_collection(auth)
        if not collection:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        item = self.get_item(collection['slug'], auth)
        if not item:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        if item['tokenType'] != "ERC721":
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        order_data = self.get_buy_data(item['contractAddress'], item["tokenId"], item['tokenType'], auth, account)
        if not order_data:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        def to_collections_bytes(order, nonces):
            bytes_str = '0x'
            value = 0
            filled_nonce_set = set()
            royalty_fee_stat = {}

            collection_start_nonce = int(order['startNonce'])
            index = 0

            if order['basicCollections']:
                for basic_collection in order['basicCollections']:
                    items_count = len(basic_collection['items'])
                    start_nonce = collection_start_nonce
                    end_nonce = start_nonce + items_count
                    collection_start_nonce = end_nonce

                    filled_index_list = []

                    i = 0
                    while index < len(nonces) and nonces[index] >= start_nonce and nonces[index] < end_nonce:
                        if i < 16:
                            filled_nonce_set.add(nonces[index])
                            filled_index_list.append(nonces[index] - start_nonce)
                            value += int(basic_collection['items'][filled_index_list[i]]['erc20TokenAmount'])
                        index += 1
                        i += 1

                    filled_index_list_part1 = '0'
                    filled_index_list_part2 = '0'
                    if filled_index_list:
                        if basic_collection['royaltyFeeRecipient'] != NULL_ADDRESS:
                            key = basic_collection['royaltyFeeRecipient'].lower()
                            current_value = royalty_fee_stat[key]
                            royalty_fee_stat[key] = current_value + 1 if key in royalty_fee_stat else 1

                        filled_index_list_hex = ''.join(f'{filled_index:02x}' for filled_index in filled_index_list)
                        filled_index_list_hex = filled_index_list_hex.ljust(32, '0')

                        filled_index_list_part1 = '0x' + filled_index_list_hex[:24]
                        filled_index_list_part2 = '0x' + filled_index_list_hex[24:]

                    head1 = encode_bits([
                        [filled_index_list_part1, 96],
                        [basic_collection['nftAddress'], 160]
                    ])

                    head2 = encode_bits([
                        [0, 8],
                        [items_count, 8],
                        [len(filled_index_list), 8],
                        [0, 8],
                        [filled_index_list_part2, 32],
                        [basic_collection['platformFee'], 16],
                        [basic_collection['royaltyFee'], 16],
                        [basic_collection['royaltyFeeRecipient'], 160]
                    ])

                    items_bytes = '0x'
                    for item in basic_collection['items']:
                        item_bytes = encode_bits([[int(item['erc20TokenAmount']), 96], [int(item['nftId']), 160]])
                        items_bytes += item_bytes[2:]

                    bytes_str += head1[2:] + head2[2:] + items_bytes[2:]

            if order['collections']:
                for collection in order['collections']:
                    items_count = len(collection['items'])
                    start_nonce = collection_start_nonce
                    end_nonce = start_nonce + items_count
                    collection_start_nonce = end_nonce

                    filled_index_list = []

                    i = 0
                    while index < len(nonces) and nonces[index] >= start_nonce and nonces[index] < end_nonce:
                        if i < 16:
                            filled_nonce_set.add(nonces[index])
                            filled_index_list.append(nonces[index] - start_nonce)
                            value += int(collection['items'][filled_index_list[i]]['erc20TokenAmount'])
                        index += 1
                        i += 1

                    filled_index_list_part1 = '0'
                    filled_index_list_part2 = '0'
                    if filled_index_list:
                        if collection['royaltyFeeRecipient'] != NULL_ADDRESS:
                            key = collection['royaltyFeeRecipient'].lower()
                            current_value = royalty_fee_stat[key]
                            royalty_fee_stat[key] = current_value + 1 if key in royalty_fee_stat else 1

                        filled_index_list_hex = ''.join(f'{filled_index:02x}' for filled_index in filled_index_list)
                        filled_index_list_hex = filled_index_list_hex.ljust(32, '0')

                        filled_index_list_part1 = '0x' + filled_index_list_hex[:24]
                        filled_index_list_part2 = '0x' + filled_index_list_hex[24:]

                    head1 = encode_bits([
                        [filled_index_list_part1, 96],
                        [collection['nftAddress'], 160]
                    ])

                    head2 = encode_bits([
                        [1, 8],
                        [items_count, 8],
                        [len(filled_index_list), 8],
                        [0, 8],
                        [filled_index_list_part2, 32],
                        [collection['platformFee'], 16],
                        [collection['royaltyFee'], 16],
                        [collection['royaltyFeeRecipient'], 160]
                    ])

                    items_bytes = '0x'
                    for item in collection['items']:
                        item_bytes = encode_bits([[item['erc20TokenAmount'], 256]]) + encode_bits([[item['nftId'], 256]])[2:]
                        items_bytes += item_bytes[2:]

                    bytes_str += head1[2:] + head2[2:] + items_bytes[2:]

            return value, royalty_fee_stat, bytes_str, filled_nonce_set

        def to_collections_bytes_list(order, nonce_list):
            if nonce_list is None or len(nonce_list) == 0:
                return None

            nonce_set = set(nonce_list)
            nonces = sorted(list(nonce_set))

            nonce_limit = int(order['startNonce']) + len(order['basicCollections'][0]['items'])
            if nonces[-1] >= nonce_limit:
                raise Exception

            value = 0
            royalty_fee_stat = {}
            bytes_list = []

            filled_nonce_set = set()
            while len(filled_nonce_set) < len(nonces):
                unfilled_nonce_list = [nonce for nonce in nonces if nonce not in filled_nonce_set]

                value, royalty_fee_stat, bytes, filled_nonce_set = to_collections_bytes(order, unfilled_nonce_list)
                value += value
                for key, val in royalty_fee_stat.items():
                    royalty_fee_stat[key] += val
                bytes_list.append(bytes)

                filled_nonce_set.update(filled_nonce_set)

            return value, royalty_fee_stat, bytes_list

        def encode_bits(args):
            data = '0x'
            for arg in args:
                if isinstance(arg[0], str) and arg[0].startswith('0x'):
                    arg_val = int(arg[0][2:], 16)
                else:
                    arg_val = int(arg[0])
                data += to_hex_bytes(hex(arg_val).lower(), arg[1])
            data = data.ljust(64, '0')
            return data

        def to_hex_bytes(hex_str, bit_count):
            count = bit_count // 4
            str_hex = hex_str[2:] if hex_str.lower().startswith('0x') else hex_str.lower()
            if len(str_hex) > count:
                return str_hex[-count:]
            return str_hex.rjust(count, '0')

        MASK_96 = 0xffffffffffffffffffffffff
        taker_part1 = new_w3.to_hex(int(account.address, 16) >> 96)
        taker_part2 = new_w3.to_hex(int(account.address, 16) & MASK_96)
        try:
            exchange_data = json.loads(order_data['exchangeData'])
        except:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        try:
            data3 = encode_bits([[taker_part2, 96], [int(exchange_data['platformFeeRecipient'], 16), 160]])
            data2 = encode_bits([[taker_part1, 64], [int(exchange_data['expirationTime']), 32], [0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 160]])
            data1 = encode_bits([[int(exchange_data['startNonce']), 26], [int(exchange_data['v']), 8], [int(exchange_data['listingTime']), 32], [int(exchange_data['maker'], 16), 160]])

            collection_ = to_collections_bytes_list(exchange_data, [int(exchange_data['nonce'])])

            args = [int(data1[0:-6], 16), int(data2, 16), int(data3, 16), exchange_data['r'], exchange_data['s']], collection_[2][0]
        except:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1)

        func_ = getattr(self.contract.functions, 'fillBatchSignedERC721Order')
        tx = make_tx(new_w3, account, value=int(order_data['value']), func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt+1)

        try:
            nft = f"{collection['name']} #{item['tokenId']}"
        except:
            nft = 'UNKNOWN'

        self.logger.log_success(f"{self.project} | Успешно купил NFT ({nft}) за {round(int(order_data['value']) / 10 ** 18, 6)} ETH",wallet=account.address)
        return new_w3.to_hex(hash)

    def get_maker_nonce(self, auth, account):
        for i in range(3):
            try:
                payload = {"exchange":"0x0caB6977a9c70E04458b740476B498B214019641","maker": account.address.lower(),"chain":"linea","schema":"erc721","count":1}
                res = self.help.fetch_tls(session = self.session, url= 'https://api.element.market/v3/orders/getMakerNonce', type='post', payload=payload, headers=self.get_headers(auth=auth))
                return res['data']
            except:
                time.sleep((i+1)*i)
        return None

    def get_fees(self, contract, auth, token_id='0'):
        for i in range(3):
            try:
                payload = {"chainMid": 901, "standard": ["element-ex-v3"], "contracts": [{"contractAddress": contract, "tokenId": token_id}]}
                res = self.help.fetch_tls(session = self.session, url='https://api.element.market/bridge/v1/royalty', type='post', payload=payload, headers=self.get_headers(auth=auth))
                return res['data']
            except:
                time.sleep((i + 1) * i)
        return None

    def get_platform_fees(self, fees):
        platformFeeRecipient = None
        if 'protocolFeePoints' in fees:
            protocolFeeAddress = fees['protocolFeeAddress'].lower() if 'protocolFeeAddress' in fees else NULL_ADDRESS
            if platformFeeRecipient:
                pass
            else:
                platformFeeRecipient = protocolFeeAddress
        return platformFeeRecipient if platformFeeRecipient else NULL_ADDRESS

    def get_nft(self, auth, account):
        for i in range(3):
            try:
                payload = {"operationName": "AssetsListFromUser",
                           "variables": {"realtime": True, "thirdStandards": ["element-ex-v3"], "sortAscending": False,
                                         "sortBy": "RecentlyTransferred", "toggles": ["NOT_ON_SALE"],
                                         "ownerAddress": account.address, "first": 50, "uiFlag": "COLLECTED",
                                         "blockChains": [{"chain": "linea", "chainId": "0xE708"}],
                                         "account": {"address": "0x5f67ffa4b3f77dd16c9c34a1a82cab8daea03191",
                                                     "blockChain": {"chain": "linea", "chainId": "0xE708"}},
                                         "constantWhenERC721": 1},
                           "query": "query AssetsListFromUser($before: String, $after: String, $first: Int, $last: Int, $querystring: String, $categorySlugs: [String!], $collectionSlugs: [String!], $sortBy: SearchSortBy, $sortAscending: Boolean, $toggles: [SearchToggle!], $ownerAddress: Address, $creatorAddress: Address, $blockChains: [BlockChainInput!], $paymentTokens: [String!], $priceFilter: PriceFilterInput, $stringTraits: [StringTraitInput!], $contractAliases: [String!], $thirdStandards: [String!], $uiFlag: SearchUIFlag, $account: IdentityInput, $constantWhenERC721: Int) {\n  search(\n    \n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    search: {querystring: $querystring, categorySlugs: $categorySlugs, collectionSlugs: $collectionSlugs, sortBy: $sortBy, sortAscending: $sortAscending, toggles: $toggles, ownerAddress: $ownerAddress, creatorAddress: $creatorAddress, blockChains: $blockChains, paymentTokens: $paymentTokens, priceFilter: $priceFilter, stringTraits: $stringTraits, contractAliases: $contractAliases, uiFlag: $uiFlag}\n  ) {\n    totalCount\n    edges {\n      cursor\n      node {\n        asset {\n          chain\n          chainId\n          contractAddress\n          tokenId\n          tokenType\n          name\n          imagePreviewUrl\n          animationUrl\n          rarityRank\n          isFavorite\n          ownedQuantity(viewer: $account, constantWhenERC721: $constantWhenERC721)\n          orderData(standards: $thirdStandards) {\n            bestAsk {\n              ...BasicOrder\n            }\n            bestBid {\n              ...BasicOrder\n            }\n          }\n          assetEventData {\n            lastSale {\n              lastSaleDate\n              lastSalePrice\n              lastSalePriceUSD\n              lastSaleTokenContract {\n                name\n                address\n                icon\n                decimal\n                accuracy\n              }\n            }\n          }\n          marketStandards(account: $account) {\n            count\n            standard\n            floorPrice\n          }\n          collection {\n            name\n            isVerified\n            slug\n            imageUrl\n            royaltyFeeEnforced\n            contracts {\n              blockChain {\n                chain\n                chainId\n              }\n            }\n          }\n          suspiciousStatus\n          uri\n        }\n      }\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      startCursor\n      endCursor\n    }\n  }\n}\n\nfragment BasicOrder on OrderV3Type {\n  __typename\n  chain\n  chainId\n  chainMId\n  expirationTime\n  listingTime\n  maker\n  taker\n  side\n  saleKind\n  paymentToken\n  quantity\n  priceBase\n  priceUSD\n  price\n  standard\n  contractAddress\n  tokenId\n  schema\n  extra\n  paymentTokenCoin {\n    name\n    address\n    icon\n    chain\n    chainId\n    decimal\n    accuracy\n  }\n}\n"}

                res = self.help.fetch_tls(session=self.session, url='https://api.element.market/graphql?args=AssetsListFromUser', type='post', payload=payload, headers=self.get_headers(auth=auth))
                items = []
                edges = res["data"]["search"]["edges"]
                for item in edges:
                    items.append(item['node']['asset'])
                return random.choice(items)
            except:
                time.sleep((i + 1) * i)
        return None

    def list_nft(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        nonce = self.get_nonce(account)
        if not nonce:
            return 'no_auth'
        auth = self.get_auth(nonce, account)
        if not auth:
            return 'no_auth'

        def to_standard_basic_collections(order):
            basic_collections = []
            if order.get('basicCollections') is not None:
                for collection in order['basicCollections']:
                    items = []
                    if collection.get('items'):
                        for item in collection['items']:
                            items.append(encode_bits([
                                [item['paymentTokenAmount'], 96],
                                [item['erc721TokenId'], 160]
                            ]))
                    fee = [
                        [0, 64],
                        [collection['platformFee'], 16],
                        [collection['royaltyFee'], 16],
                        [collection['royaltyFeeRecipient'], 160]
                    ]
                    basic_collections.append({
                        'nftAddress': collection['nftAddress'],
                        'fee': encode_bits(fee),
                        'items': items
                    })
            try:
                basic_collections[0]['fee'] = bytes.fromhex(basic_collections[0]['fee'][2:])
                basic_collections[0]['items'] = [bytes.fromhex(basic_collections[0]['items'][0][2:])]
            except:
                pass
            return basic_collections

        def to_standard_collections(order):
            collections = []
            if order.get('collections') is not None:
                for collection in order['collections']:
                    items = []
                    if collection.get('items'):
                        items.extend(collection['items'])
                    collections.append({
                        'nftAddress': collection['nftAddress'],
                        'fee': encode_bits([
                            [0, 64],
                            [collection['platformFee'], 16],
                            [collection['royaltyFee'], 16],
                            [collection['royaltyFeeRecipient'], 160]
                        ]),
                        'items': items
                    })
            try:
                collections[0]['fee'] = bytes.fromhex(collections[0]['fee'][2:])
                collections[0]['items'] = [bytes.fromhex(collections[0]['items'][0][2:])]
            except:
                pass
            return collections

        def encode_bits(args):
            data = '0x'
            for arg in args:
                if isinstance(arg[0], str) and arg[0].startswith('0x'):
                    arg_val = int(arg[0][2:], 16)
                else:
                    arg_val = int(arg[0])
                data += to_hex_bytes(hex(arg_val).lower(), arg[1])
            data = data.ljust(64, '0')
            return data

        def to_hex_bytes(hex_str, bit_count):
            count = bit_count // 4
            str_hex = hex_str[2:] if hex_str.lower().startswith('0x') else hex_str.lower()
            if len(str_hex) > count:
                return str_hex[-count:]
            return str_hex.rjust(count, '0')

        def to_standart_erc20_token(erc20Token):
            if erc20Token and erc20Token.lower() != '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                return erc20Token.lower()
            return NULL_ADDRESS

        def get_order(item):
            collection = {
                'nftAddress': item['erc721TokenAddress'].lower(),
                'items': [],
                'isBasic': True
            }

            obj = {
                'erc20TokenAmount': int(item['paymentTokenAmount']),
                'nftId': int(item['erc721TokenId'])
            }
            collection['items'].append(obj)

            if collection['isBasic']:
                if 10 ** 50 < int(obj['erc20TokenAmount']) or 10 ** 18 < int(obj['nftId']):
                    collection['isBasic'] = False

            order = {
                'basicCollections': [],
                'collections': [],
                'itemCount': 0
            }

            collection_new = {
                'nftAddress': collection['nftAddress'],
                'platformFee': 0,
                'royaltyFeeRecipient': NULL_ADDRESS,
                'royaltyFee': 0,
                'items': []
            }

            if collection['isBasic']:
                order['basicCollections'].append(collection_new)
            else:
                order['collections'].append(collection_new)

            order['itemCount'] += 1

            if collection['isBasic']:
                collection_new['items'].append(item)
            else:
                collection_new['items'].append(obj)

            return order

        def set_collection_fees(collections, fee):
            for collection in collections:
                if fee:
                    if fee['protocolFeeAddress'] and fee['protocolFeeAddress'].lower() != NULL_ADDRESS:
                        collection['platformFee'] = fee.get('protocolFeePoints', 0)
                    if fee['royaltyFeeInfos'][0]['royaltyFeeAddress'] and fee['royaltyFeeInfos'][0][
                        'royaltyFeeAddress'].lower() != NULL_ADDRESS:
                        collection['royaltyFee'] = int(fee['royaltyFeeInfos'][0]['royaltyFeePoints'])
                        collection['royaltyFeeRecipient'] = fee['royaltyFeeInfos'][0]['royaltyFeeAddress'].lower()

        def create_order(params, account, counter=None):
            fees = self.get_fees(account.address, params['erc721TokenAddress'], params['erc721TokenId'])[0]
            platformFeeRecipient = self.get_platform_fees(fees)
            maker = account.address
            paymentToken = to_standart_erc20_token(params['paymentToken'])
            listingTime, expirationTime = int(time.time() - 60), int(time.time() + 60 * 60 * 24 * 30)

            #hashNonce = counter if counter is not None else self.contract.functions.getHashNonce(self.w3.to_checksum_address(maker)).call()
            order = get_order(params)
            nonce = self.get_maker_nonce(auth, account)
            set_collection_fees(order['basicCollections'], fees)
            set_collection_fees(order['collections'], fees)
            order_ = {
                'exchange': self.contract.address,
                'maker': maker,
                'listingTime': listingTime,
                'expirationTime': expirationTime,
                'startNonce': nonce,
                'paymentToken': paymentToken,
                'platformFeeRecipient': platformFeeRecipient,
                'basicCollections': order['basicCollections'],
                'collections': order['collections'],
                'hashNonce': str(0), #str(hashNonce)
                'chain': 59144
            }
            return order_

        def to_standard_order(order):
            return {
                "maker": order["maker"],
                "listingTime": order["listingTime"],
                "expiryTime": order["expirationTime"],
                "startNonce": int(order["startNonce"]),
                "erc20Token": '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
                "platformFeeRecipient": order["platformFeeRecipient"],
                "basicCollections": to_standard_basic_collections(order),
                "collections": to_standard_collections(order),
                "hashNonce": int(order["hashNonce"])
            }

        def post_order(order, signed_message, message, address, auth):
            basic_collection = order['basicCollections']
            collections = order['collections']
            if basic_collection:
                basic_collection[0]['items'] = [{"erc20TokenAmount": str(basic_collection[0]['items'][0]['paymentTokenAmount']),'nftId': str(basic_collection[0]['items'][0]['erc721TokenId'])}]
            if collections:
                collections[0]['items'] = [{"erc20TokenAmount": str(collections[0]['items'][0]['erc20TokenAmount']), "nftId": str(collections[0]['items'][0]['nftId'])}]
            payload = {"listingTime": message['message']['listingTime'],
                       "expirationTime": message['message']['expiryTime'],
                       "paymentToken": "0x0000000000000000000000000000000000000000",
                       "platformFeeRecipient": order['platformFeeRecipient'],
                       "basicCollections": basic_collection, "collections": collections, "chain": "linea",
                       "maker": address,
                       "exchange": "0x0cab6977a9c70e04458b740476b498b214019641", "startNonce": int(order["startNonce"]),
                       "hashNonce": order["hashNonce"], "hash": signed_message['messageHash'].hex(),
                       "v": signed_message['v'],
                       "r": self.w3.to_hex(signed_message['r']), "s": self.w3.to_hex(signed_message['s'])}
            res = self.help.fetch_tls(session=self.session, url='https://api.element.market/v3/orders/postBatch', type='post', payload=payload, headers=self.get_headers(auth=auth))
            return res

        item = self.get_nft(auth, account)
        if not item:
            return 'no_nft'

        try:
            price = float(item['assetEventData']['lastSale']['lastSalePrice'])
            price = round(price * random.uniform(2, 5), 6)
        except:
            price = round(random.uniform(1.5, 5) * 0.1, 6)
        contract = item['contractAddress']
        token_id = item['tokenId']
        type = item['tokenType']

        if type.lower() != "ERC721".lower():
            return 'no_nft'

        price = self.w3.to_wei(price, 'ether')

        params = {
            'erc721TokenAddress': contract,
            'erc721TokenId': token_id,
            'paymentTokenAmount': price,
            'paymentToken': NULL_ADDRESS,
        }

        approve = check_approve(new_w3, account, contract, markets_data[self.project]['approve_contract'], nft=True)
        if not approve:
            make_approve(new_w3, account, contract, markets_data[self.project]['approve_contract'], nft=True)

        order = create_order(params, account)
        message = {
            'types': markets_data['ELEMENT']['listing']['types'],
            'domain': markets_data['ELEMENT']['listing']['domain'],
            'primaryType': markets_data['ELEMENT']['listing']['primaryType'],
            'message': to_standard_order(order)
        }

        encoded_message = encode_structured_data(message)
        signed_message = Account.sign_message(encoded_message, account._private_key.hex())

        result = post_order(order, signed_message, message, account.address, auth)
        try:
            if result['data']['successList'] is not None:
                self.logger.log_success(f"{self.project} | Успешно залистил NFT ({item['collection']['name']} #{item['tokenId']}) за {round(price / 10 ** 18, 6)} ETH", wallet=account.address)
                return True
            elif result['data']['successList'] is None and result['data']['failList'] is None:
                return 'error'
            else:
                return 'error'
        except:
            return 'error'

class Alienswap():

    def __init__(self, w3, logger, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'ALIENSWAP'
        self.logger = logger

    def get_headers(self, auth=None):
        headers = {
            'authority': 'alienswap.xyz',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'expires': '0',
            'pragma': 'no-cache',
            'referer': 'https://alienswap.xyz',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        if auth:
            headers['authorization'] = f"Bearer {auth}"
        return headers

    def get_auth(self, account, session):
        for i in range(3):
            try:
                message_ = 'Welcome to AlienSwap!\nClick to sign in and accept the AlienSwap Terms of Service.\nThis request will not trigger a blockchain transaction or cost any gas fees.'
                message = message_.encode()
                message_to_sign = encode_defunct(primitive=message)
                signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
                sig = signed_message.signature.hex()
                json_data = {
                    'address': account.address,
                    'signature': sig,
                    'nonce': 'Welcome to AlienSwap!\nClick to sign in and accept the AlienSwap Terms of Service.\nThis request will not trigger a blockchain transaction or cost any gas fees.',
                    'src': 4,
                    'network': 'linea',
                    'inviter': 'z47xmV',
                }
                response = self.help.fetch_tls(url='https://alienswap.xyz/alien-api/api/v1/public/user/signin', type='post', headers=self.get_headers(), payload=json_data, session=session)
                return response['data']['access_token']
            except:
                time.sleep(i*1)
        return None

    def get_collections(self, auth, session):
        for i in range(3):
            try:
                response = self.help.fetch_tls(url='https://alienswap.xyz/api/statistics/ranking/collection?sort_field=market_cap&sort_direction=desc&limit=1000&chainId=59144', type='get', headers=self.get_headers(auth=auth), session=session)
                collections = []
                for col in response['data']:
                    try:
                        if float(col['floor_price']) <= self.max_price:
                            collections.append(col)
                    except:
                        pass
                return collections
            except:
                time.sleep(i*1)
        return []

    def get_nfts(self, auth, session, collection):
        for i in range(3):
            try:
                url = 'https://alienswap.xyz/api/market/linea/tokens/v6'
                params = {
                    'collection': str(collection).lower(),
                    'includeAttributes': 'true',
                    'includeLastSale': 'true',
                    'includeTopBid': 'true',
                    'includeDynamicPricing': 'true',
                    'limit': '50',
                    'flagStatus': '0',
                }
                response = self.help.fetch_tls(url=url, type='get', headers=self.get_headers(), session=self.help.get_tls_session(), params=params)
                nfts = []
                for nft in response['tokens']:
                    try:
                        if float(nft['market']['floorAsk']['price']['amount']['native']) <= self.max_price:
                            nfts.append(nft)
                    except:
                        pass
                return random.choice(nfts)
            except:
                time.sleep(i*1)
        return None

    def get_buy_data(self, auth, session, account, token):
        for i in range(3):
            try:
                payload = {"items":[{"token":f"{token['token']['contract']}:{token['token']['tokenId']}"}],"taker":account.address,"source":"alienswap.xyz"}
                response = self.help.fetch_tls(url='https://alienswap.xyz/api/market/linea/execute/buy/v7', type='post', headers=self.get_headers(auth=auth), session=session, payload=payload)
                return response['steps'][1]['items'][0]['data']
            except:
                time.sleep(i*1)
        return []

    def buy_nft(self, private_key, max_price, attempt = 0, auth=None, session=None):

        if attempt > 10:
            return 'error'
        elif attempt != 0:
            time.sleep(1)

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        self.max_price = max_price

        #if session is None:
        session = self.help.get_tls_session()

        if auth is None:
            auth = self.get_auth(account, session)
            if not auth:
                return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt+1, auth=auth, session=session)

        collections = self.get_collections(auth, session)
        if not collections:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1, auth=auth, session=session)

        collection = random.choice(collections)

        nft = self.get_nfts(auth, session, collection['contract_address'])
        if not nft:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1, auth=auth, session=session)

        buy_data = self.get_buy_data(auth, session, account, nft)

        if not buy_data:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt + 1, auth=auth, session=session)

        tx = make_tx(new_w3, account, value=int(buy_data['value'], 16), to=buy_data['to'], data=buy_data['data'])
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.buy_nft(private_key=private_key, max_price=max_price, attempt=attempt+1, auth=auth, session=session)

        self.logger.log_success( f"{self.project} | Успешно купил NFT ({nft['token']['name']}) за {nft['market']['floorAsk']['price']['amount']['native']} ETH", wallet=account.address)
        return new_w3.to_hex(hash)

    def get_user_nfts(self, auth, session, account):
        for i in range(3):
            try:
                params = {
                    'limit': '200',
                    'includeTopBid': 'true',
                    'includeLastSale': 'true',
                }
                response = self.help.fetch_tls(url=f'https://alienswap.xyz/api/market/linea/users/{account.address.lower()}/tokens/v7', type='get', headers=self.get_headers(), session=self.help.get_tls_session(), params=params)
                eligable = []
                for token in response['tokens']:
                    if int(token['ownership']['onSaleCount']) == 0:
                        eligable.append(token)
                return eligable
            except:
                time.sleep(i*1)
        return None

    def get_sell_data(self, auth, session, account, price, token):
        for i in range(3):
            try:
                payload = {"maker":account.address.lower(),"source":"alienswap.xyz","params":[{"token":f"{token['token']['contract']}:{token['token']['tokenId']}","weiPrice":str(price),"orderKind":"alienswap","orderbook":"reservoir","expirationTime":str(int(time.time())+ 60*60*24*90),"options":{"alienswap":{"useOffChainCancellation":True}},"automatedRoyalties":False}]}
                response = self.help.fetch_tls(url=f'https://alienswap.xyz/api/market/linea/execute/list/v5', type='post', headers=self.get_headers(), session=self.help.get_tls_session(), payload=payload)
                return response['steps']
            except:
                time.sleep(i*1)
        return None

    def fix_data_types(self, original_message):
        _message = original_message.copy()
        _message['domain']['chainId'] = int(_message['domain']['chainId'])
        message = _message['message']
        message['zoneHash'] = self.w3.to_bytes(hexstr=message['zoneHash'][2:])
        message['salt'] = int(message['salt'])
        message['conduitKey'] = self.w3.to_bytes(hexstr=message['conduitKey'][2:])
        message['startTime'] = int(message['startTime'])
        message['endTime'] = int(message['endTime'])
        message['orderType'] = int(message['orderType'])
        message['counter'] = int(message['counter'])
        #message['totalOriginalConsiderationItems'] = int(message['totalOriginalConsiderationItems'])

        for offer in message['offer']:
            offer['itemType'] = int(offer['itemType'])
            offer['identifierOrCriteria'] = int(offer['identifierOrCriteria'])
            offer['startAmount'] = int(offer['startAmount'])
            offer['endAmount'] = int(offer['endAmount'])

        for consideration in message['consideration']:
            consideration['itemType'] = int(consideration['itemType'])
            consideration['identifierOrCriteria'] = int(consideration['identifierOrCriteria'])
            consideration['startAmount'] = int(consideration['startAmount'])
            consideration['endAmount'] = int(consideration['endAmount'])

        return _message

    def post_order(self, auth, session, signarute, post):
        for i in range(3):
            try:
                url = f"https://alienswap.xyz/api/market/linea/order/v3?signature={signarute}"
                payload = post
                response = self.help.fetch_tls(url=url, type='post', headers=self.get_headers(auth), session=self.help.get_tls_session(), payload=payload)
                if response.get('message', 'bad') == 'Success':
                    return True
            except:
                time.sleep(i*1)
        return None

    def list_nft(self, private_key, attempt=0, auth=None, session=None):

        if attempt > 10:
            return 'error'
        elif attempt != 0:
            time.sleep(1)

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        #if session is None:
        session = self.help.get_tls_session()

        if auth is None:
            auth = self.get_auth(account, session)
            if not auth:
                return self.list_nft(private_key=private_key, attempt=attempt + 1, auth=auth, session=session)

        nfts = self.get_user_nfts(auth, session, account)
        if not nfts:
            return 'no_nft'
        nft = random.choice(nfts)

        try:
            price = int(int(nft['collection']['floorAskPrice']['amount']['raw']) * random.uniform(1.5, 5))
        except:
            price = int(random.uniform(0.1, 0.5) * 10 ** 18)

        sell_data = self.get_sell_data(auth, session, account, price, nft)
        if not sell_data:
            return self.list_nft(private_key=private_key, attempt=attempt + 1, auth=auth, session=session)

        if sell_data[0]['items'][0]['status'] != 'complete':
            res = check_approve(new_w3, account, nft['token']['contract'], markets_data[self.project]['contract'], nft=True)
            if not res:
                make_approve(new_w3, account, nft['token']['contract'], markets_data[self.project]['contract'], nft=True)

        sign_data = sell_data[1]['items'][0]['data']

        message = sign_data['sign']
        message['types']['EIP712Domain'] = [
            {
                "name": "name",
                "type": "string"
            },
            {
                "name": "version",
                "type": "string"
            },
            {
                "name": "chainId",
                "type": "uint256"
            },
            {
                "name": "verifyingContract",
                "type": "address"
            }
        ]
        message_to_sign = {
            'domain': message['domain'],
            'types': message['types'],
            'message': message['value'],
            'primaryType': message['primaryType']
        }
        message_fixed = self.fix_data_types(message_to_sign)
        encoded_message = encode_structured_data(message_fixed)
        signed_message = Account.sign_message(encoded_message, private_key['private_key'])

        post = self.post_order(auth, session, signed_message.signature.hex(), sign_data['post']['body'])
        if not post:
            return self.list_nft(private_key=private_key, attempt=attempt + 1, auth=auth, session=session)
        else:
            self.logger.log_success( f"{self.project} | Успешно залистил NFT ({nft['token']['name']} #{nft['token']['tokenId']}) за {round(price/(10**18), 6)} ETH", wallet=account.address)
            return True

class Zonic():

    def __init__(self, w3, logger, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'ZONIC'
        self.logger = logger
        self.contract = w3.eth.contract(address=w3.to_checksum_address(markets_data[self.project]['contract']), abi=markets_data[self.project]['ABI'])

    def get_collections(self):
        for i in range(3):
            try:
                payload = {"item_per_page": 250, "page": 0, "chain_id": 59144}
                collections = self.help.fetch_url(url='https://api.nftnest.io/v1/explore/get_collections', type='post', payload=payload)
                eligble_collections = []
                for col in collections['contracts']:
                    try:
                        if int(col['collection_info']['listed_count']) > 0 and int(col['floor_price'], 16) <= self.max_price * 10 ** 18:
                            eligble_collections.append(col)
                    except:
                        pass
                collection = random.choice(eligble_collections)
                return collection
            except:
                time.sleep((i+i)*1)
        return None

    def get_items(self, contract):
        for i in range(3):
            try:
                payload = {"contract_address": contract, "chain": "linea", "sort_by": "price_lowest", "page": 0, "attributes": [], "name": ""}
                items = self.help.fetch_url(url ='https://api.nftnest.io/v1/collection/get_nfts', type='post', payload=payload)
                items = items["tokens"]
                for i in items['59144']:
                    return i['contract_address'], str(int(i['token_id'], 16))
            except:
                time.sleep((i + i) * 1)
        return None, None

    def get_data(self, token_id, contract):
        for i in range(3):
            try:
                payload = {"contract_address": contract, "token_id": token_id, "chain_id": 59144}
                res = self.help.fetch_url(url ='https://api.nftnest.io/v1/marketplace/listing/get', type='post', payload=payload)
                sig_data = res['active_listing']['signature']
                sale_id = res['active_listing']['sale_id']
                list_price = int(res['active_listing']['list_price'], 16)
                listing = res['active_listing']['data']['message']
                payload = {"sale_id": sale_id, "chain_id": 59144}
                res_sig = self.help.fetch_url(url ='https://api.nftnest.io/v1/marketplace/listing/get_purchase_sig', type='post', payload=payload)
                expired_at = res_sig['expired_at']
                r = res_sig['r']
                s = res_sig['s']
                v = res_sig['v']
                return sig_data, expired_at, r, s, v, list_price, listing
            except:
                time.sleep((i + i) * 1)
        return None, None, None, None, None, None, None

    def buy_nft(self, private_key, max_price):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])
        self.max_price = max_price

        collection = self.get_collections()
        if not collection:
            return 'no_col'
        contract, token_id = self.get_items(collection['contract_address'])
        if not contract:
            return 'no_ntf'

        sig_data, expired_at, r, s, v, list_price, message = self.get_data(token_id, contract)
        if not sig_data:
            return 'no_data'

        listing = [
            new_w3.to_checksum_address(message['offerer']),
            [
                [
                    offer['itemType'],
                    new_w3.to_checksum_address(offer['token']),
                    int(offer['identifier']),
                    offer['amount']
                ] for offer in message['offers']
            ],
            [
                message['offererPayout']['itemType'],
                new_w3.to_checksum_address(message['offererPayout']['token']),
                int(message['offererPayout']['identifier']),
                new_w3.to_checksum_address(message['offererPayout']['recipient']),
                int(message['offererPayout']['amount'])
            ],
            [
                [
                    payout['itemType'],
                    new_w3.to_checksum_address(payout['token']),
                    int(payout['identifier']),
                    new_w3.to_checksum_address(payout['recipient']),
                    int(payout['amount'])
                ] for payout in message['creatorPayouts']
            ],
            message['orderType'],
            message['listedAt'],
            message['expiredAt'],
            message['saleId'],
            message['version']
        ]
        signature = sig_data
        adminSignatureV = int(v)
        adminSignatureR = r
        adminSignatureS = s
        adminSigExpiredAt = int(expired_at)

        args = listing, signature, adminSignatureV, adminSignatureR, adminSignatureS, adminSigExpiredAt
        func_ = getattr(self.contract.functions, 'fulfillBasicOrder')

        tx = make_tx(new_w3, account, value=list_price, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.buy_nft(private_key=private_key, max_price=max_price)
        self.logger.log_success(f"{self.project} | Успешно купил NFT ({collection['collection_info']['name']}) за {round(int(list_price) / 10 ** 18, 6)} ETH", wallet=account.address)

        return new_w3.to_hex(hash)

    def get_price(self, contract_address):
        payload = {"contract_address": contract_address, "chain": "linea"}
        res = self.help.fetch_url(url='https://api.nftnest.io/v1/collection/summary', type='post', payload=payload)
        try:
            price = int(res['summary']['floor_price'], 16)
        except:
            price = int(0.05 * 10 ** 18)
        return int(price * random.uniform(1.5, 5))

    def sign_and_post(self, contract_address, token_id, account, creator_payouts=["0xC353dE8af2eE32DA2eeaE58220D3c8251eE1aDcf", 250]):
        chainId = 59144
        types = { "OfferItem": [ { "name": "itemType", "type": "uint8" }, { "name": "token", "type": "address" }, { "name": "identifier", "type": "uint256" }, { "name": "amount", "type": "uint256" } ], "Payout": [ { "name": "itemType", "type": "uint8" }, { "name": "token", "type": "address" }, { "name": "identifier", "type": "uint256" }, { "name": "recipient", "type": "address" }, { "name": "amount", "type": "uint256" } ], "Listing": [ { "name": "offerer", "type": "address" }, { "name": "offers", "type": "OfferItem[]" }, { "name": "offererPayout", "type": "Payout" }, { "name": "creatorPayouts", "type": "Payout[]" }, { "name": "orderType", "type": "uint8" }, { "name": "listedAt", "type": "uint32" }, { "name": "expiredAt", "type": "uint32" }, { "name": "saleId", "type": "address" }, { "name": "version", "type": "uint8" } ], "EIP712Domain": [ { "name": "name", "type": "string" }, { "name": "version", "type": "string" }, { "name": "chainId", "type": "uint256" }, { "name": "verifyingContract", "type": "address" } ] }
        primary_type = "Listing"

        price = self.get_price(contract_address)

        def generate_message_for_listing(chain_id, connected_address, contract_address, token_id, price, creatorPayouts=None, listingInterval=60 * 60 * 24 * 30):
            wallet_address = self.w3.eth.account.create().address
            current_time = int(datetime.now().timestamp()) + int(listingInterval)

            price_decimal = ''
            for i in range(len(str(price))):
                price_decimal += str(price)[i] if i < 4 else '0'
            price_decimal = int(price_decimal)

            creator_payouts = []

            if creatorPayouts:
                creator_address, creator_fee = creatorPayouts

                if creator_fee > 10:
                    return {
                        'success': False,
                        'error': 'Creator Fee could not be more than 10%'
                    }

                creator_fee_amount = int((price_decimal * creator_fee * 100 / 10000))
                marketplace_fee_amount = int((price_decimal * 250 / 10000))
                offerer_payout_amount = int(price_decimal - (creator_fee_amount + marketplace_fee_amount))

                if offerer_payout_amount <= 0:
                    return {
                        'success': False,
                        'error': 'Unexpected Error'
                    }

                offerer_payout = {
                    'itemType': 0,
                    'token': '0x0000000000000000000000000000000000000000',
                    'identifier': 0,
                    'recipient': connected_address,
                    'amount': int(offerer_payout_amount)
                }

                creator_payouts.append({
                    'itemType': 0,
                    'token': '0x0000000000000000000000000000000000000000',
                    'identifier': 0,
                    'recipient': creator_address,
                    'amount': int(creator_fee_amount)
                })
            else:

                creator_fee_percentage = 250
                offerer_payout_amount = price_decimal - int((price_decimal * creator_fee_percentage / 10000))

                offerer_payout = {
                    'itemType': 0,
                    'token': '0x0000000000000000000000000000000000000000',
                    'identifier': 0,
                    'recipient': connected_address,
                    'amount': int(offerer_payout_amount)
                }

                creator_payouts.append({
                    'itemType': 0,
                    'token': '0x0000000000000000000000000000000000000000',
                    'identifier': 0,
                    'recipient': connected_address,
                    'amount': 0
                })

            domain = {
                'chainId': chain_id,
                'name': 'Zonic : NFT Marketplace for L2',
                'verifyingContract': '0x1a7b46c660603ebb5fbe3ae51e80ad21df00bdd1',
                'version': '1'
            }

            message = {
                'offerer': connected_address,
                'offers': [{
                    'itemType': 2,
                    'token': contract_address,
                    'identifier': token_id,
                    'amount': 1
                }],
                'offererPayout': offerer_payout,
                'creatorPayouts': creator_payouts,
                'orderType': 2,
                'listedAt': 0,
                'expiredAt': current_time,
                'saleId': wallet_address,
                'version': 1
            }

            return {
                'success': True,
                'domain': domain,
                'message': message
            }

        data = generate_message_for_listing(chainId, account.address, contract_address, token_id, price, creatorPayouts=creator_payouts)

        if not data['success']:
            return data, price

        domain = data['domain']
        message = data['message']

        structured_message = {
            'types': types,
            'primaryType': primary_type,
            'domain': domain,
            'message': message,
        }

        encoded_message = encode_structured_data(structured_message)
        signed_message = Account.sign_message(encoded_message, account._private_key.hex())
        signature = signed_message.signature.hex()

        domain = {
            "chainId": "0xe708",
            "name": "Zonic : NFT Marketplace for L2",
            "verifyingContract": "0x1A7b46C660603EBB5FBe3AE51e80AD21dF00bDd1",
            "version": "1"
        }
        message['creatorPayouts'][0]['amount'] = str(message['creatorPayouts'][0]['amount'])
        message['offererPayout']['amount'] = str(message['offererPayout']['amount'])
        message['offers'][0]['identifier'] = str(message['offers'][0]['identifier'])
        payload = {"listing_type": "basic", "chain_id": 59144, "contract_address": contract_address,
                   "token_id": str(token_id), "data": {"types": types,
                "primaryType": primary_type, "domain": domain,
                "message": message}, "signature": signature}
        res = self.help.fetch_url(url='https://api.nftnest.io/v1/marketplace/listing/create', type='post', payload=payload)
        return res, price

    def get_nfts(self, account):
        for i in range(3):
            try:
                payload = {"address": account.address, "chain": "linea", "page": 0, "sort_by": "listed_lowest_price", "contract_addresses": "", "name": ""}
                res = self.help.fetch_url(url='https://api.nftnest.io/v1/wallet/get_nfts', type='post', payload=payload)
                eligable_tokens = []
                for token in res['tokens']['59144']:
                    if not token.get('active_listing', False):
                        eligable_tokens.append(token)
                if eligable_tokens:
                    token = random.choice(eligable_tokens)
                else:
                    return False, False
                try:
                    creator_earnings = res.json()['contracts']['59144'][token["contract_address"]]['creator_earnings']
                except:
                    creator_earnings = []
                return token, creator_earnings
            except:
                time.sleep((i+1)*i)
        return None, None

    def list_nft(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token, creator_earnings = self.get_nfts(account)
        if not token:
            return 'no_ntf'

        if creator_earnings:
            creator_earnings = [creator_earnings[0]["payout_address"], int(creator_earnings[0]["percentage"])]
        else:
            creator_earnings = []


        res = check_approve(new_w3, account, token['contract_address'], markets_data[self.project]['contract'], nft=True)
        if not res:
            make_approve(new_w3, account, token['contract_address'], markets_data[self.project]['contract'], nft=True)

        result, price = self.sign_and_post(token['contract_address'], int(token['token_id'], 16), account, creator_payouts=creator_earnings)

        if result.get("success", False):
            try:
                token_name = token['token_info']['metadata']['name']
            except:
                token_name = 'UNKNOWN'
            self.logger.log_success(f"{self.project} | Успешно залистил NFT ({token_name}) за {round(int(price) / 10 ** 18, 6)} ETH", wallet=account.address)
            return True
        else:
            return


def initialize_nft_markets(classes_to_init, w3, logger, helper):
    available_swaps = {
        "Element": Element,
        "Alienswap": Alienswap,
        "Zonic": Zonic,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, logger, helper)

    return initialized_objects

