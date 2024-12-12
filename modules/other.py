from requests_toolbelt import MultipartEncoder
from helpers.data import other_data, NULL_ADDRESS, tokens_data_
from helpers.utils import *
from web3._utils.contracts import encode_abi
import random, string, uuid, base64, hmac, hashlib
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware

def generate_collection_name():
    prefixes = ['Crypto', 'NFT', 'Digital', 'Art', 'Linea', 'Virtual', 'Collectible', 'Magic', 'Space', 'Galactic', 'Pixel', 'Dream',
                'Quantum', 'Rainbow', 'Kryptonite', 'Time', 'Cyber', 'Unicorn', 'Blockchain', 'Token', 'Ether', 'Decentralized', 'Tech', 'Smart', 'Solid',
                'Meta', 'Web', 'Mystic', 'Star', 'Future', 'Cyberpunk', 'Neo', 'Cosmic', 'Satoshi', 'Moon', 'HODL', 'FOMO', 'DeFi', 'Yield', 'NFTY',
                'Crystal', 'Dream', 'Future', 'Eon', 'Infinity', 'Fusion', 'Cosmos', 'Linea', 'Layer2', 'L2', 'Chain', 'Plasma', 'Stellar', 'Solaris']

    suffixes = ['Hub', 'Network', 'Platform', 'World', 'Base', 'Zone', 'Galaxy', 'Vortex', 'Dreams', 'Realm', 'Universe', 'Space', 'Void',
                'Vault', 'Wave', 'Port', 'Path', 'Forge', 'Protocol', 'Studio', 'Collective', 'Protocol', 'Labs', 'Craft', 'Works', 'Gems', 'Genesis',
                'Tech', 'Chain', 'Nexus', 'Digital', 'Sphere', 'Linea', 'Layer', 'Star', 'Solaris', 'Plasma', 'Stellar', 'Nebula', 'Horizon', 'Pulse', 'Orbit', 'Cosmos', 'Synchrony']

    names = ['Alpha', 'Omega', 'NFT', 'Genesis', 'Digital', 'Art', 'Mystic', 'Space', 'Cosmic', 'Galactic', 'Pixel', 'Quantum', 'Rainbow', 'Kryptonite', 'Cyber', 'Magic', 'Unicorn', 'Meta', 'Ether', 'Satoshi', 'Moon', 'HODL', 'FOMO', 'DeFi', 'Yield', 'NFTY',
            'Crystal', 'Dream', 'Future', 'Eon', 'Infinity', 'Fusion', 'Cosmos', 'Linea', 'Layer2', 'L2', 'Chain', 'Plasma', 'Stellar', 'Solaris', 'Horizon', 'Synchrony', 'Nova', 'Aurora', 'Aegis', 'Celestial', 'Nebula', 'Pulse', 'Orbit', 'Nexus']

    name = random.choice(prefixes) + ' ' + random.choice(names) + ' ' + random.choice(suffixes)
    return name

def generate_collection_symbol(name):
    symbol = name.replace(' ', '').upper()[:random.randint(3, 5)]
    return symbol

def generate_collection_description(name):
    descriptions = [name + ' Token', name + ' NFT', 'The ' + name + ' Collection', 'Explore the ' + name,
                    'Discover ' + name, name + ' Universe', name + ' Artwork', 'The Essence of ' + name,
                    name + ' Wonders', 'Journey through ' + name, name + ' Treasures', 'Unlock the power of ' + name,
                    'A world of ' + name, 'The magic of ' + name, 'Experience ' + name, 'Delve into ' + name,
                    name + ' Marvels', 'Adventures in ' + name, 'The Enchantment of ' + name, name + ' Dreams',
                    'Visions of ' + name, 'Echoes of ' + name, name + ' Fantasia', 'The Enigma of ' + name,
                    name + ' Chronicles', 'Whispers of ' + name, name + ' Odyssey', 'Tales from ' + name,
                    'The Legacy of ' + name, name + ' Legends', 'Myths of ' + name, name + ' Saga',
                    'In the realm of ' + name, 'A world beyond ' + name, name + ' Elegance', 'Infinite ' + name,
                    'The heart of ' + name, 'Celestial ' + name, 'Epic ' + name, name + ' Phenomenon',
                    'Legends of ' + name, name + ' Chronicle', 'Sculptures of ' + name, 'Symphony of ' + name,
                    'Rise of ' + name, 'Mysteries of ' + name, 'Whispers from ' + name, 'The Odyssey of ' + name,
                    'Realm of ' + name, 'Astral ' + name, 'Chronicles of ' + name, 'Sagas from ' + name,
                    'Tales of ' + name, 'Adventures of ' + name, 'Wonders of ' + name, 'Legends from ' + name,
                    'The Enchanted ' + name, 'Artistry of ' + name, name + ' Visions', 'Curiosities of ' + name,
                    'Symphonies from ' + name, 'The Myths of ' + name, 'Epic ' + name + ' Adventures',
                    'Whispers of ' + name + ' Tales', name + ' Fantasies', 'Odyssey through ' + name,
                    'Chronicles of ' + name + ' Lore', 'The Legacy ' + name + ' Holds',
                    'Myths and ' + name + ' Legends', name + ' Sagas of Wonder', 'Tales of ' + name + ' Chronicles',
                    'Adventures in ' + name + ' Realm', 'Exploring ' + name + ' Dreams',
                    'Unlocking ' + name + ' Mysteries', 'Discover the ' + name + ' Odyssey',
                    name + ' Chronicles of Destiny', 'Echoes from ' + name + ' Visions', name + ' Odyssey into Fantasy',
                    'The ' + name + ' Artistic Journey', 'Mystical ' + name + ' Quest',
                    'Wonders of ' + name + ' Realms', 'Enchanted ' + name + ' Tales', name + ' Dreams and Legends',
                    'Exploring the ' + name + ' Universe', 'Embark on a ' + name + ' Adventure',
                    name + ' Odyssey Beyond Imagination', 'Legends and Myths of ' + name,
                    'A ' + name + ' Fantasy Adventure', 'Chronicles of ' + name + ' Legends',
                    'The ' + name + ' Legacy Unveiled', 'Mythical ' + name + ' Odyssey', name + ' Journeys of Wonder',
                    'Uncover ' + name + ' Chronicles', 'Enter the World of ' + name,
                    'Tales from the ' + name + ' Realm', name + ' Chronicles of Imagination',
                    'The ' + name + ' Saga Begins', 'A ' + name + ' Fantasy Realm', 'Legendary ' + name + ' Odyssey',
                    'Mysteries of ' + name + ' Legends', 'Venture into ' + name + ' Realms',
                    'Adventures in ' + name + ' Lore', 'Discover ' + name + ' Visions',
                    name + ' Odyssey of Enchantment', 'Epic ' + name + ' Chronicles', 'Whispers of ' + name + ' Myths',
                    'Journey through ' + name + ' Fantasy', name + ' Chronicles of Magic',
                    'Unlocking ' + name + ' Wonders', 'Embark on a ' + name + ' Quest', name + ' Odyssey into Legends',
                    'Realm of ' + name + ' Fantasy', 'The ' + name + ' Enchanted Journey',
                    'Explore the ' + name + ' Chronicles', name + ' Odyssey Beyond Dreams',
                    'Legends and Myths of ' + name + ' Realm', 'A ' + name + ' Adventure Awaits',
                    'Chronicles of ' + name + ' Destiny', 'The ' + name + ' Legacy Revealed',
                    'Mythical ' + name + ' Adventures', name + ' Journeys into Fantasy',
                    'Unveiling ' + name + ' Chronicles', 'Discover ' + name + ' Realms',
                    'Tales from the ' + name + ' Odyssey', name + ' Chronicles of Wonder',
                    'The ' + name + ' Saga Continues', 'A ' + name + ' Fantasy Adventure Beckons',
                    'Legendary ' + name + ' Chronicles', 'Mysteries of ' + name + ' Visions',
                    'Venture into ' + name + ' Lore', 'Adventures in ' + name + ' Imagination',
                    name + ' Odyssey of Magic', 'Epic ' + name + ' Myths', 'Whispers of ' + name + ' Legends',
                    'Journey through ' + name + ' Enchantment']
    description = random.choice(descriptions)
    return description

#0.00069 ETH NFT
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

    def get_collections(self, chain=59144):

        for i in range(5):
            try:
                payload = {
                    'operationName': 'projectCollection',
                    'variables': {
                        'projectAddress': '0xe60aC07Be8bD7f7f33d446e1399c329928Ba8114',
                        'limit': 10000,
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

    def main(self, private_key, attempt = 0):

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

        collections = self.get_collections()
        if not collections:
            return self.main(private_key=private_key, attempt=attempt+1)
        collection = random.choice(collections)

        contract = collection['writingNFT']['proxyAddress']

        col_contract = new_w3.eth.contract(address=new_w3.to_checksum_address(contract), abi=other_data[self.project]['ABI'])
        price = col_contract.functions.price().call()

        if price != 0 and collection['_id'] != 'XcOD365fDtWqqCAOLvlw6K0dlqxfonyiMwh7S2qec4U':
            return self.main(private_key=private_key, attempt=attempt + 1)
        if collection['_id'] == 'XcOD365fDtWqqCAOLvlw6K0dlqxfonyiMwh7S2qec4U':
            add_price = 0.0002
        else:
            add_price = 0

        func_ = getattr(col_contract.functions, 'purchase')

        tx = make_tx(new_w3, account, value=int((0.00069+add_price) * 10 ** 18), func=func_, args=(account.address, ""), args_positioning=True)
        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, attempt = attempt + 2)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, attempt = attempt + 1)

        self.logger.log_success(f"{self.project} | Успешно заминтил статью {collection['writingNFT']['title']} за 0.00069 ETH",account.address)
        return new_w3.to_hex(hash)
#FREE NFT
class Bilinear():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'BILINEAR'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])
        self.collection_categories = ['art', 'music', 'gaming', 'membership', 'photography', 'pfp']
        self.collection_types = [[2, 'ERC1155']] #[[1, 'ERC721'], [2, 'ERC1155']]

    def get_headers(self, multipart=None):
        headers = {
            'authority': 'api.bilinear.io',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://www.bilinear.io',
            'referer': 'https://www.bilinear.io/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        if multipart:
            headers['content-type'] = multipart.content_type
        return headers

    def generate_random_filename(self):
        random_uuid = uuid.uuid4()

        random_filename = str(random_uuid).replace("-", "")

        return random_filename

    def get_image_hash(self, nft=False, col_address=None):
        for i in range(5):
            try:
                image_size = random.choice([i for i in range(500, 1001, 100)])
                image = self.helper.fetch_url(url=f'https://picsum.photos/{image_size}', type='get', content=True)
                if not image:
                    continue
                col_name = generate_collection_name()
                col_desc = generate_collection_description(col_name)
                random_file_name = self.generate_random_filename()
                fields = {
                    'image': (str(random_file_name), image, 'image/jpeg'),
                    'name': col_name if not nft else nft,
                    'description': col_desc if not nft else f"{nft} Token",
                }
                if nft:
                    fields['media_type'] = 'image/jpeg'
                    fields['external_url'] = ''
                    fields['attributes'] = []
                    fields['collection_address'] = col_address
                    fields['chain'] = 'linea'

                boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
                multipart = MultipartEncoder(fields=fields, boundary=boundary)
                return multipart, col_name, col_desc
            except:
                time.sleep((i+1)*i)
        return None

    def process_nft_creation(self, account, private_key, new_w3, col_address, name):
        multipart, _, __ = self.get_image_hash()
        url = f'https://api.bilinear.io/collection-ipfs'
        result = self.helper.fetch_url(url=url, type='post', headers=self.get_headers(multipart=multipart), data=multipart)

        contract = new_w3.eth.contract(address=new_w3.to_checksum_address(col_address), abi=other_data[self.project]['ABI_ERC1155'])
        NFT_count = random.randint(1, 10)
        args = NFT_count, result['metadata_uri']

        func_ = getattr(contract.functions, 'mint')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно заминтил {NFT_count} NFT в коллекции "{name}"!', wallet=account.address)
        return new_w3.to_hex(hash)

    def process_collection_creation(self, account, private_key, new_w3):

        multipart, name, desc = self.get_image_hash()

        url = f'https://api.bilinear.io/collection-ipfs'
        result = self.helper.fetch_url(url=url, type='post', headers=self.get_headers(multipart=multipart), data=multipart)

        category = random.choice(self.collection_categories)
        type = random.choice(self.collection_types)
        royaly = int(random.randint(0, 10) * 100)
        supply = random.choice([int(random.randint(10, 1000) * random.randint(1, 10)), 6969, int(random.randint(1, 10) * 1000)])
        symbol = generate_collection_symbol(name)

        args = name, symbol, result['metadata_uri'], supply, royaly, account.address, type[0]

        func_ = getattr(self.contract.functions, 'createCollection')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        tx_receipt = new_w3.eth.get_transaction_receipt(hash)

        url = f'https://api.bilinear.io/collection-db'
        json_data = {
            'chain': 'linea',
            'address': tx_receipt.logs[1]['address'],
            'token_standard': type[1],
            'tx_hash': new_w3.to_hex(hash),
            'total_supply': '0',
            'media_type': 'image/jpeg',
            'media_uri': result['image_uri'],
            'external_link': '',
            'name': name,
            'description': desc,
            'metadata_uri': result['metadata_uri'],
            'image_uri': result['image_uri'],
            'blacklisted': False,
            'max_supply': str(supply),
            'royalties_basis_points': royaly,
            'symbol': symbol,
            'category': category,
        }

        result = self.helper.fetch_url(url=url, type='post', headers=self.get_headers(), payload=json_data)

        self.logger.log_success(f'{self.project} | Успешно сделал коллекцию "{name}"!', wallet=account.address)
        return self.process_nft_creation(account, private_key, new_w3, tx_receipt.logs[1]['address'], name)

    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        return self.process_collection_creation(account, private_key, new_w3)
#FREE NFT
class Nfts2me():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'NFTS2ME'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])

    def process_collection_creation(self, account, private_key, new_w3):

        name = generate_collection_name()
        symbol = generate_collection_symbol(name)

        supply = random.randint(1, 10)

        args = name, symbol, [account.address for i in range(supply)], new_w3.eth.account.create().key.hex(), [], '0x0000000000000000000000000000000000000000', 750, False, new_w3.eth.account.create().key.hex(), '0x3732310000000000000000000000000000000000000000000000000000000000'

        func_ = getattr(self.contract.functions, 'createAndMintCollection')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)

        self.logger.log_success(f'{self.project} | Успешно сделал коллекцию "{name}" и заминтил {supply} NFT!', wallet=account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        return self.process_collection_creation(account, private_key, new_w3)
#FREE NFT
class Omnisea():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'OMNISEA'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])

    def get_headers(self, multipart=None):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Origin': 'https://omnisea.org',
            'Referer': 'https://omnisea.org/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'authorization': 'Basic MjdwTVA4SEFtckp3TXVHemJGdXBlN0dPY0FBOmU0OTA0N2I2YmM4MmExZjYwY2VkMDUwY2I5MjVkNzYy',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        if multipart:
            headers['content-type'] = multipart.content_type
        return headers

    def generate_random_filename(self):
        random_uuid = uuid.uuid4()

        random_filename = str(random_uuid).replace("-", "")

        return random_filename

    def get_image_hash(self):
        for i in range(5):
            try:
                image_size = random.choice([i for i in range(500, 1001, 100)])
                image = self.helper.fetch_url(url=f'https://picsum.photos/{image_size}', type='get', content=True)
                if not image:
                    continue
                col_name = generate_collection_name()
                col_desc = generate_collection_description(col_name)
                fields = {
                    'file': ('', image, 'image/jpeg'),
                }

                boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
                multipart = MultipartEncoder(fields=fields, boundary=boundary)
                return multipart, col_name, col_desc
            except:
                time.sleep((i+1)*i)
        return None

    def process_collection_creation(self, account, private_key, new_w3):

        multipart, name, desc = self.get_image_hash()

        url = f'https://ipfs.infura.io:5001/api/v0/add?stream-channels=true&progress=false'
        result = self.helper.fetch_url(url=url, type='post', headers=self.get_headers(multipart=multipart), data=multipart)
        hash = result['Hash']

        name = generate_collection_name()
        symbol = generate_collection_symbol(name)
        end_time = int(time.time() + random.randint(30*24*60*60, 30*24*60*60*12))
        royaly = int(random.randint(0, 10) * 100)
        supply = random.choice([int(random.randint(10, 1000) * random.randint(1, 10)), 6969, int(random.randint(1, 10) * 1000)])
        args = name, symbol, hash, '', supply, True, royaly, end_time

        func_ = getattr(self.contract.functions, 'create')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=False)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно создал коллекцию "{name}"!', wallet=account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        return self.process_collection_creation(account, private_key, new_w3)
#CHEAP TX
class Dmail():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'DMAIL'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])

    def process_send_mail(self, account, private_key, new_w3):

        to = f'{new_w3.eth.account.create().address}@dmail.ai'
        subject = random.choice(['gm', 'hello', 'hi', 'welcome', 'Gm', 'Hello', 'Hi', 'Welcome']) + ' ' + to
        args = to, subject

        func_ = getattr(self.contract.functions, 'send_mail')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно отправил письмо!', wallet=account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        return self.process_send_mail(account, private_key, new_w3)

class Backer_nft():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'BACKER NFT'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])

    def get_headers(self, auth=None):
        headers = {
            'authority': 'event.aspecta.id',
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://aspecta.id',
            'referer': 'https://aspecta.id/',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        if auth:
            headers['authorization'] = f'Bearer {auth}'
        return headers

    def get_auth(self, account):
        nonce, raw_nonce = None, None
        for i in range(3):
            try:
                nonce_data = self.helper.fetch_url(f"https://passport.aspecta.id/api/metamask/nonce/{account.address}/", type='get', headers=self.get_headers())
                nonce = nonce_data['nonce']
                raw_nonce = nonce_data['raw_nonce']
                break
            except:
                time.sleep(1)

        if not nonce:
            return None, None
        message = nonce.encode()
        message_to_sign = encode_defunct(primitive=message)
        signed_message = self.w3.eth.account.sign_message(message_to_sign, private_key=account._private_key.hex())
        sig = signed_message.signature.hex()

        for i in range(3):
            try:
                payload = {
                    "nonce": base64.b64encode(nonce.encode('utf-8')).decode('utf-8'),
                    "signature": sig,
                    "raw_nonce": raw_nonce,
                }
                multipart_data = MultipartEncoder(fields=payload)
                headers = self.get_headers()
                headers['content-type'] = multipart_data.content_type
                auth_data = self.helper.fetch_url(f"https://passport.aspecta.id/api/metamask/login/", type='post', headers=headers, data=multipart_data .to_string())
                auth = auth_data['token']
                return auth, auth_data['username']
            except:
                time.sleep(1)
        return None, None

    def process_likes(self, auth):
        users = None
        for i in range(3):
            try:
                params = {
                    'page': '1',
                    'page_size': '20',
                }
                users = self.helper.fetch_url(url='https://event.aspecta.id/api/events-published/01e97f75-0b1c-407f-8b64-939e731f925e/users/', type='get', headers=self.get_headers(auth=auth), params=params)
                break
            except:
                time.sleep(1)
        if not users:
            return
        for user in users['data']:
            try:
                self.helper.fetch_url(url=f'https://event.aspecta.id/api/events/29/users/{user["user_id"]}/likers/like/', type='post', headers=self.get_headers(auth=auth), payload={'event_id': 29,'user_id': int(user['user_id'])}, retries=1)
            except:
                pass
        return True

    def process_getintouch(self, auth, username):
        for i in range(3):
            try:
                services = random.choice([3, 1, 6, 7])
                appeals = random.choice([2, 8])
                payload = {
                    'services': [
                        services
                    ],
                    'appeals': [
                        appeals
                    ],
                    'services_custom': [],
                    'appeals_custom': [],
                }
                getintouch = self.helper.fetch_url(url=f'https://profile.aspecta.id/new/api/users/{username}/get-in-touch-with/',type='patch', headers=self.get_headers(auth=auth), payload=payload)
                if getintouch.get('services_formatted'):
                    return True
            except:
                time.sleep(1)
        return

    def process_label(self, auth):
        for i in range(3):
            try:
                label = random.choice(['ai','creative','front_end_developer','gamer','nft','nature_lover','team_player','smart_contract','independent_developer','poker','traveler',])
                payload = {
                    'custom_labels': [
                        label
                    ],
                }
                label = self.helper.fetch_url(url='https://profile.aspecta.id/new/api/users/labels/',type='patch', headers=self.get_headers(auth=auth), payload=payload)
                if label.get('custom_labels'):
                    return True
            except:
                time.sleep(1)
        return

    def process_intro(self, auth, username):
        for i in range(3):
            try:
                intro = generate_collection_name()
                payload = {
                    'short_intro': intro
                }
                multipart_data = MultipartEncoder(fields=payload)
                headers = self.get_headers(auth=auth)
                headers['content-type'] = multipart_data.content_type
                intro = self.helper.fetch_url(url='https://profile.aspecta.id/new/api/home/auth/user/',type='patch', headers=headers, data=multipart_data.to_string())
                if intro['username'] == username:
                    return True
            except:
                time.sleep(1)
        return

    def process_twitter_stuff(self, auth):
        for i in range(3):
            try:
                payload = {
                    'page_url': 'https://aspecta.id/u/user7591Z',
                    'action': 'open_link',
                    'action_target': 'follow_aspecta',
                }
                follow1 = self.helper.fetch_url(url='https://mission.aspecta.id/api/user-action-logs',type='post', headers=self.get_headers(auth=auth), payload=payload)
                if follow1:
                    break
            except:
                time.sleep(1)

        for i in range(3):
            try:
                payload = {
                    'page_url': 'https://aspecta.id/u/user7591Z',
                    'action': 'share_twitter',
                    'action_target': 'share_campaign',
                }
                follow2 = self.helper.fetch_url(url='https://mission.aspecta.id/api/user-action-logs', type='post', headers=self.get_headers(auth=auth), payload=payload)
                if follow2:
                    return True
            except:
                time.sleep(1)
        return

    def post_data(self, auth):
        for i in range(3):
            try:
                payload = {"campaign_id":2,"mission":4}
                data = self.helper.fetch_url(url='https://mission.aspecta.id/api/benefits/acquirement',type='post', headers=self.get_headers(auth=auth), payload=payload)
                if data:
                    return True
            except:
                time.sleep(1)

    def get_claim_data(self, auth):
        for i in range(3):
            try:
                payload = {"network_id":13,"by_gas_free":False,"is_attestation":True}
                data = self.helper.fetch_url(url='https://campaign.aspecta.id/api/campaigns/2/claim-nfts/12/',type='post', headers=self.get_headers(auth=auth), payload=payload)
                if data['nft_sign_info']:
                    return data
            except:
                time.sleep(1)

    def process_all(self, account, private_key, new_w3, attempt = 0, auth=None):

        if attempt > 10:
            return 'error'

        auth, username = self.get_auth(account)
        if not auth:
            return self.process_all(account, private_key, new_w3, attempt=attempt+1)

        users = self.process_likes(auth)
        if not users:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        label = self.process_label(auth)
        if not label:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        twitter = self.process_twitter_stuff(auth)
        if not twitter:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        get_in_touch = self.process_getintouch(auth, username)
        if not get_in_touch:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        intro = self.process_intro(auth, username)
        if not intro:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        data_post = self.post_data(auth)
        if not data_post:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        claim_data = self.get_claim_data(auth)
        if not claim_data:
            return self.process_all(account, private_key, new_w3, attempt=attempt + 1, auth=auth)

        func_ = getattr(self.contract.functions, 'attest')

        args = claim_data['nft_sign_info']['params']

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно заминтил BACKER NFT!', wallet=account.address)
        return new_w3.to_hex(hash)


    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        return self.process_all(account, private_key, new_w3)

#SMART TX
class Gnosis():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'GNOSIS SAFE'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])

    def get_safes(self, account):
        for i in range(3):
            try:
                result = self.helper.fetch_url(url=f'https://gateway.safe.linea.build/v1/chains/59144/owners/{account.address}/safes', type='get')
                return result['safes']
            except:
                time.sleep(1)
        return []

    def process_safe_creation(self, account, private_key, new_w3):

        data = self.contract.encodeABI(fn_name="setup", args=[[account.address], 1, NULL_ADDRESS, "0x", new_w3.to_checksum_address("0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4"), NULL_ADDRESS, 0, NULL_ADDRESS])
        args = new_w3.to_checksum_address('0x3E5c63644E683549055b9Be8653de26E0B4CD36E'), data, int(time.time()+600)

        func_ = getattr(self.contract.functions, 'createProxyWithNonce')

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        #tx_receipt = new_w3.eth.get_transaction_receipt(hash)
        #print(tx_receipt.logs[0]['address'])
        self.logger.log_success(f'{self.project} | Успешно создал Gnosis Safe!', wallet=account.address)
        return new_w3.to_hex(hash)

    def process_safe_deposit(self, account, private_key, new_w3, safe, token_data):
        prices = self.helper.get_prices_combined()
        prefered_value = random.uniform(0.05, 0.25) / prices[token_data['symbol'].upper()]
        if prefered_value > token_data['amount']:
            prefered_value = token_data['amount']
        prefered_amount = int(prefered_value * 10 ** token_data['decimals'])
        if token_data['symbol'] == 'ETH':
            tx = make_tx(new_w3, account, value=prefered_amount, to=new_w3.to_checksum_address(safe))
        else:
            contract = new_w3.eth.contract(address=new_w3.to_checksum_address(token_data['address']), abi=TOKEN_ABI)
            func_ = getattr(contract.functions, 'transfer')
            tx = make_tx(new_w3, account, value=0, func=func_, args=[new_w3.to_checksum_address(safe), prefered_amount], args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)

        self.logger.log_success(f'{self.project} | Успешно задепозитил {round(prefered_value, 6)} {token_data["symbol"]} в Gnosis Safe!', wallet=account.address)
        return new_w3.to_hex(hash)

    def process_safe_withdraw(self, account, private_key, new_w3, safe, token_data):
        contract = new_w3.eth.contract(address=new_w3.to_checksum_address(safe), abi=other_data[self.project]['SAFE_ABI'])

        signature = f'0x000000000000000000000000{account.address.lower()[2:]}000000000000000000000000000000000000000000000000000000000000000001'
        func_ = getattr(contract.functions, 'execTransaction')
        to = account.address if token_data['symbol'] == 'ETH' else token_data['address']
        value = token_data['balance'] if token_data['symbol'] == 'ETH' else 0
        if token_data['symbol'] == 'ETH':
            data = '0x'
        else:
            t_contract = new_w3.eth.contract(address=new_w3.to_checksum_address(token_data['address']), abi=TOKEN_ABI)
            transfer_func = t_contract.functions.transfer(account.address, token_data['balance'])
            transfer_data = encode_abi(self.w3, transfer_func.abi, [account.address, token_data['balance']])
            data = f"0xa9059cbb{transfer_data[2:]}"
        args = to, value, data, 0, 0, 0, 0, NULL_ADDRESS, NULL_ADDRESS, signature
        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)

        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)

        self.logger.log_success(f'{self.project} | Успешно вывел {round(token_data["amount"], 6)} {token_data["symbol"]} из Gnosis Safe!', wallet=account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key):

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        safes = self.get_safes(account)
        if len(safes) == 0:
            return self.process_safe_creation(account, private_key, new_w3)
        else:
            choosed_safe = safes[0]
            safe_balance = self.helper.get_user_tokens_reserved(choosed_safe)
            user_balance = self.helper.get_user_tokens_reserved(account.address)
            have_balance = True if len([b for b in safe_balance.values() if b['balance'] != 0]) != 0 else False
            dep = lambda:self.process_safe_deposit(account, private_key, new_w3, choosed_safe, random.choice([b for b in user_balance.values() if b['balance'] != 0]))
            wd = lambda:self.process_safe_withdraw(account, private_key, new_w3, choosed_safe, random.choice([b for b in safe_balance.values() if b['balance'] != 0]))
            action = random.choice([dep, wd]) if have_balance else dep

            return action()

#FREE NFTS
class AlienMint():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'ALIEN MINT'

    def get_current_mintings(self):
        for i in range(3):
            try:
                res = self.helper.fetch_tls(url='https://alienswap.xyz/alien-api/api/v1/public/activity/l2mint/collections/minting?network=linea', type='get', session=self.helper.get_tls_session())
                cols = []
                for col in res['data']['collections']:
                    if int(col['mint_end_time']) > int(time.time()) and float(col['mint_price']) == 0:
                        cols.append(col['contract'])
                return cols
            except:
                time.sleep(1)
        return []

    def get_random_mint_tx(self, col):
        for i in range(3):
            try:
                res = self.helper.fetch_tls(url=f'https://alienswap.xyz/api/market/linea/collections/activity/v6?collection={col}&types=mint&limit=30&sortBy=eventTimestamp&includeMetadata=true', type='get', session=self.helper.get_tls_session())
                hash_occurrences = {}
                for tx in res['activities'][1:-1]:
                    tx_hash = tx['txHash']
                    if tx_hash in hash_occurrences:
                        hash_occurrences[tx_hash] += 1
                    else:
                        hash_occurrences[tx_hash] = 1
                for tx in res['activities'][1:-1]:
                    if hash_occurrences[tx['txHash']] == 1:
                        return tx['txHash'], tx['collection']['collectionName']
            except:
                time.sleep(1)
        return None, None

    def main(self, private_key, attemp=0):

        if attemp > 5:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        current_mintings = self.get_current_mintings()
        if len(current_mintings) == 0:
            self.logger.log_warning(f"{self.project} | Сейчас нет никаких бесплатных минтов, пропускаю!", wallet=account.address)
            return

        col = random.choice(current_mintings)
        hash, col_name = self.get_random_mint_tx(col)
        if not hash:
            return self.main(private_key=private_key, attemp=attemp+1)

        receipt = new_w3.eth.get_transaction(hash)

        tx = make_tx(new_w3, account, value=0, to=receipt['to'], data=receipt['input'])
        if tx == "low_native" or not tx:
            return tx

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key)
        self.logger.log_success(f'{self.project} | Успешно заминтил NFT ({col_name}) за 0 ETH!', wallet=account.address)
        return new_w3.to_hex(hash)

#FREE NFTS
class ElementMint():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'ALIEN MINT'

    def generate_xapi_signature(self, api_key='zQbYj7RhC1VHIBdWU63ki5AJKXloamDT', secret='UqCMpfGn3VyQEdsjLkzJv9tNlgbKFD7O'):
        random_number = random.randint(1000, 9999)
        timestamp = int(time.time())
        message = f"{api_key}{random_number}{timestamp}"
        signature = hmac.new(bytes(secret, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
        return f"{signature}.{random_number}.{timestamp}"

    def get_headers(self):
        headers = {
            'x-api-key': 'zQbYj7RhC1VHIBdWU63ki5AJKXloamDT',
            'x-api-sign': str(self.generate_xapi_signature()),
        }
        return headers

    def get_current_mintings(self):
        for i in range(3):
            try:
                payload = {"operationName":"CollectionMintRanking","variables":{"first":100,"statsLevel":"L1H","sortBy":"Trades","blockChain":{"chain":"linea","chainId":"0xE708"},"isAsc":False},"query":"query CollectionMintRanking($before: String, $after: String, $first: Int, $last: Int, $blockChain: BlockChainInput!, $statsLevel: String!, $sortBy: String!, $isAsc: Boolean) {\n  collectionMintRanking(\n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    blockChain: $blockChain\n    statsLevel: $statsLevel\n    sortBy: $sortBy\n    isAsc: $isAsc\n  ) {\n    edges {\n      cursor\n      node {\n        collectionId\n        level\n        mintCount\n        mintCountRatio\n        mintPrice\n        usdMintPrice\n        floorPrice\n        usdFloorPrice\n        uniqueMinter\n        totalSupply\n        assetCount\n        whales\n        contractAddress\n        mintFunc {\n          selector\n          defaultAmount\n          maxDefaultAmount\n          avgMintPrice\n          mintPrice\n          support\n        }\n        collection {\n          name\n          imageUrl\n          isVerified\n          slug\n          ifNew\n          createdDate\n          rewards {\n            rewardTrade {\n              score\n            }\n            rewardListing {\n              score\n              flag\n            }\n          }\n          stats {\n            coin {\n              icon\n              symbol\n              chain\n              chainId\n            }\n          }\n        }\n      }\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      startCursor\n      endCursor\n    }\n  }\n}\n"}
                res = self.helper.fetch_tls(url='https://api.element.market/graphql?args=CollectionMintRanking', type='post', headers=self.get_headers(), payload=payload, session=self.helper.get_tls_session())
                cols = []
                for col in res['data']['collectionMintRanking']['edges']:
                    col = col['node']
                    if float(col['mintPrice']) == 0 and col['mintFunc']['selector']:
                        cols.append(col)
                return cols
            except:
                time.sleep(1)
        return []

    def get_random_mint_tx(self, col):
        for i in range(3):
            try:
                res = self.helper.fetch_tls(url=f'https://alienswap.xyz/api/market/linea/collections/activity/v6?collection={col}&types=mint&limit=30&sortBy=eventTimestamp&includeMetadata=true', type='get', session=self.helper.get_tls_session())
                hash_occurrences = {}
                for tx in res['activities'][1:-1]:
                    tx_hash = tx['txHash']
                    if tx_hash in hash_occurrences:
                        hash_occurrences[tx_hash] += 1
                    else:
                        hash_occurrences[tx_hash] = 1
                for tx in res['activities'][1:-1]:
                    if hash_occurrences[tx['txHash']] == 1:
                        return tx['txHash'], tx['collection']['collectionName']
            except:
                time.sleep(1)
        return None, None

    def main(self, private_key, attemp=0):

        if attemp > 20:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        current_mintings = self.get_current_mintings()
        if len(current_mintings) == 0:
            self.logger.log_warning(f"{self.project} | Сейчас нет никаких бесплатных минтов, пропускаю!", wallet=account.address)
            return

        col = random.choice(current_mintings)
        tx = make_tx(new_w3, account, value=0, to=new_w3.to_checksum_address(col['contractAddress']), data=col['mintFunc']['selector'])
        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, attemp=attemp+1)

        try:
            sign = account.sign_transaction(tx)
            hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        except:
            return self.main(private_key=private_key, attemp=attemp + 1)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, attemp=attemp+1)
        self.logger.log_success(f'{self.project} | Успешно заминтил NFT ({col["collection"]["name"]}) за 0 ETH!', wallet=account.address)
        return new_w3.to_hex(hash)

#FREE NFTS
class Tatarot():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'TATAROT'
        self.contract = self.w3.eth.contract(address=self.w3.to_checksum_address(other_data[self.project]['contract']), abi=other_data[self.project]['ABI'])
        self.headers = {
            'authority': 'api.tatarot.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://tatarot.ai',
            'referer': 'https://tatarot.ai/',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

    def generate_i_wonder_phrases(self):
        categories = ['love', 'career', 'health', 'travel', 'personal growth', 'finance', 'education', 'hobbies',
                      'friendships', 'technology']
        subjects = ['relationship', 'job', 'adventure', 'learning', 'project', 'investment', 'course', 'skill',
                    'meeting', 'innovation']
        descriptors = ['unexpected', 'exciting', 'challenging', 'rewarding', 'new', 'surprising', 'intense', 'relaxing',
                       'demanding', 'innovative']
        actions = ['awaits', 'brings', 'leads to', 'changes', 'enhances', 'disrupts', 'transforms', 'influences',
                   'affects', 'determines']
        times = ['soon', 'this year', 'next month', 'in the future', 'tomorrow', 'in a decade', 'before long',
                 'eventually', 'one day', 'in my lifetime']
        emotions = ['joy', 'curiosity', 'fear', 'hope', 'anxiety', 'excitement', 'dread', 'optimism', 'apprehension',
                    'eagerness']
        places = ['at work', 'in my city', 'abroad', 'at home', 'online', 'in nature', 'in space', 'in my country',
                  'in a virtual world', 'in the unknown']

        templates = ["how {descriptor} my {category} can be {time}", "what {descriptor} {subject} {action} me {time}",
                     "if {category} involves {descriptor} {subject} {place}",
                     "when encountering a {descriptor} {subject} that {action} {emotion}",
                     "{descriptor} {emotion} with {subject} {place}",
                     "possibilities of {descriptor} {subject} in {category}",
                     "{time} for a {descriptor} change in {category}",
                     "the {emotion} of {descriptor} {subject} {action} me",
                     "{category} {action} by {descriptor} {subject} {place}",
                     "{subject} that {action} {emotion} {time}",
                     "exploring {descriptor} {category} possibilities {place}",
                     "why {category} often {action} {descriptor} {emotion} {time}",
                     "imagining a {time} when {subject} becomes {descriptor}",
                     "{emotion} felt during {descriptor} {subject} {action}",
                     "chances of {descriptor} {subject} impacting {category} {place}",
                     "navigating {descriptor} {subject} in a world of {category}",
                     "{time} for {emotion} to guide {descriptor} {subject}",
                     "what if {category} {action} {emotion} through {subject}",
                     "the role of {descriptor} {subject} in shaping {category} {time}",
                     "envisioning {place} with {descriptor} {subject} {action} {category}"]

        template = random.choice(templates)
        phrase = template.format(
            category=random.choice(categories),
            subject=random.choice(subjects),
            descriptor=random.choice(descriptors),
            action=random.choice(actions),
            time=random.choice(times),
            emotion=random.choice(emotions),
            place=random.choice(places)
        )
        return phrase

    def get_nft_id(self):
        for i in range(3):
            try:
                payload = { 'question': self.generate_i_wonder_phrases() }
                res = self.helper.fetch_url(url='https://fcqxmxchcrw2zp73fbjeo5plka0fkwlj.lambda-url.us-east-1.on.aws/', type='post', payload=payload, headers=self.headers)
                return int(res['scryId'])
            except:
                time.sleep(1)
        return None

    def get_sig(self, nft_id, account):
        for i in range(3):
            try:
                payload = {"address": account.address, "scryId": nft_id}
                res = self.helper.fetch_url(url='https://api.tatarot.ai/production/api/v1/signature-mint', type='post', payload=payload, headers=self.headers)
                return res['signature'], int(res['value']['validityEndTimestamp']), int(res['value']['validityStartTimestamp'])
            except:
                time.sleep(1)
        return None, None, None

    def main(self, private_key, attempt=0):

        if attempt > 20:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        nft_id = self.get_nft_id()
        if not nft_id:
            return self.main(private_key=private_key, attempt=attempt+1)

        sig, time1, time2 = self.get_sig(nft_id, account)
        if not sig:
            return self.main(private_key=private_key, attempt=attempt+1)

        func_ = getattr(self.contract.functions, 'mintWithSignature')

        tx = make_tx(new_w3, account, value=0, func=func_, args=((account.address, nft_id, time2, time1), new_w3.to_bytes(hexstr=sig)), args_positioning=True)
        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, attempt=attempt + 1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, attempt=attempt + 1)

        self.logger.log_success(f"{self.project} | Успешно заминтил NFT за 0 ETH", account.address)
        return new_w3.to_hex(hash)

#JUNK TX
class RandomTransfer():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'RANDOM TRANSFER'

    def get_random_human_address(self, new_w3):
        new_w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        for i in range(3):
            try:
                block = w3.eth.get_block(block_identifier='latest', full_transactions=True)
                from_ = random.choice(block['transactions'])['from']
                return from_
            except:
                pass
        return None

    def process_transfer(self, recipient_address, address_type, token_data, account, private_key, new_w3, attempt):

        prices = self.helper.get_prices_combined()

        prefered_value = random.uniform(0.005, 0.05) / prices[token_data['symbol'].upper()]
        if prefered_value > token_data['amount']:
            prefered_value = token_data['amount']
        prefered_amount = int(prefered_value * 10 ** token_data['decimals'])

        if token_data['symbol'] == 'ETH':
            tx = make_tx(new_w3, account, value=prefered_amount, to=new_w3.to_checksum_address(recipient_address))
        else:
            contract = new_w3.eth.contract(address=new_w3.to_checksum_address(token_data['address']), abi=TOKEN_ABI)
            func_ = getattr(contract.functions, 'transfer')
            tx = make_tx(new_w3, account, value=0, func=func_, args=[new_w3.to_checksum_address(recipient_address), prefered_amount], args_positioning=True)

        if tx == "low_native" or not tx:
            return self.main(private_key, attempt=attempt+1)

        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key, attempt=attempt+1)

        self.logger.log_success(f'{self.project} | Успешно сделал TRANSFER {round(prefered_value, 6)} {token_data["symbol"]} в на адрес ({address_type})!', wallet=account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key, attempt=0):

        if attempt>3:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        recipient_ways = {
            "RANDOM HUMAN" : self.get_random_human_address(new_w3),
            "RANDOM GENERATED": new_w3.eth.account.create().address,
            "SELF": account.address,
        }
        recipient_type = random.choice(list(recipient_ways.keys()))
        recipient_address = recipient_ways[recipient_type]

        user_balance = self.helper.get_user_tokens_reserved(account.address)
        tokens = [b for b in user_balance.values() if b['balance'] != 0]
        token_to_transfer = random.choice(tokens)

        return self.process_transfer(recipient_address, recipient_type, token_to_transfer, account, private_key, new_w3, attempt)

#JUNK TX
class RandomApprove():

    def __init__(self, w3, logger, helper):

        self.w3 = w3
        self.logger = logger
        self.helper = helper
        self.project = 'RANDOM APPROVE'

    def process_approve(self, dapp_address, dapp_name, token_to_approve, account, private_key, new_w3, attempt):

        contract = new_w3.eth.contract(address=new_w3.to_checksum_address(token_to_approve['address']), abi=TOKEN_ABI)
        func_ = getattr(contract.functions, 'approve')
        args = new_w3.to_checksum_address(dapp_address), random.randint(10000000000000000000000000000000, 115792089237316195423570985008687907853269984665640564039457584007913129)

        tx = make_tx(new_w3, account, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return self.main(private_key, attempt=attempt+1)
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)

        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key, attempt=attempt+1)
        self.logger.log_success(f"{self.project} | Успешно сделал APPROVE токена {token_to_approve['symbol']} для {dapp_name}", account.address)
        return new_w3.to_hex(hash)

    def main(self, private_key, attempt=0):

        if attempt>3:
            return 'error'

        try:
            if private_key.get('proxy', None):
                new_w3 = self.helper.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        token_to_approve_name = random.choice(list(tokens_data_.keys()))
        token_to_approve = tokens_data_[token_to_approve_name]

        dapps_list = {
            'Symbiosis' : '0x0f91052dc5B4baE53d0FeA5DAe561A117268f5d2',
            'SushiSwap' : '0x0BE808376Ecb75a5CF9bB6D237d16cd37893d904',
            'Izumi' : '0x032b241de86a8660f1ae0691a4760b426ea246d7',
            'Kyberswap' : '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5',
            'OpenOcean' : '0x6352a56caadc4f1e25cd6c75970fa768a3304e64',
            'DodoEx' : '0x03e89fc55a5ad0531576e5a502c4ca52c8bf391b',
        }

        dapp_name = random.choice(list(dapps_list.keys()))
        dapp_address = dapps_list[dapp_name]

        return self.process_approve(dapp_address, dapp_name, token_to_approve, account, private_key, new_w3, attempt)


def initialize_misc(classes_to_init, w3, logger, helper):
    available_swaps = {
        "Bilinear": Bilinear,
        "Nfts2me": Nfts2me,
        "Mirror": Mirror,
        "Omnisea": Omnisea,
        "Dmail": Dmail,
        "Backer_nft": Backer_nft,
        "Gnosis": Gnosis,
        "AlienMint": AlienMint,
        "ElementMint": ElementMint,
        "Tatarot": Tatarot,
        "RandomTransfer": RandomTransfer,
        "RandomApprove": RandomApprove,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, logger, helper)

    return initialized_objects
