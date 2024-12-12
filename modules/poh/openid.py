from .openid_code import get_gmail_code
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from ecdsa.util import randrange_from_seed__trytryagain
from ecdsa import SigningKey, NIST256p
import os, binascii, asyncio, json
from Crypto.Hash import keccak
from helpers.utils import *

class Openid():

    def __init__(self, helper, logger, w3):

        self.project = 'OPENID'
        gmail_data = []
        with open("modules/poh/gmail_data_raw.txt", "r") as f:
            gmail_data_raw = [row.strip() for row in f]
        for data in gmail_data_raw:
            gmail_data.append({"data": data, "status": 0})
        self.gmail_data = gmail_data
        self.w3 = w3
        self.logger = logger
        self.help = helper
        self.headers = {
            'authority': 'openid3.dauth.network',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://auth.openid3.xyz',
            'referer': 'https://auth.openid3.xyz/',
            'sec-ch-ua': '"Opera";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
        }
        self.contract = self.w3.eth.contract(address='0xCe048492076b0130821866F6d05A0b621B1715C8', abi='[{"inputs":[{"internalType":"address[]","name":"modules","type":"address[]"},{"internalType":"address","name":"router","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"OnlyPortalOwner","type":"error"},{"inputs":[{"components":[{"internalType":"bytes32","name":"schemaId","type":"bytes32"},{"internalType":"uint64","name":"expirationDate","type":"uint64"},{"internalType":"bytes","name":"subject","type":"bytes"},{"internalType":"bytes","name":"attestationData","type":"bytes"}],"internalType":"struct AttestationPayload","name":"attestationPayload","type":"tuple"},{"internalType":"bytes[]","name":"validationPayloads","type":"bytes[]"}],"name":"attest","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"attestationRegistry","outputs":[{"internalType":"contract AttestationRegistry","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"bytes32","name":"schemaId","type":"bytes32"},{"internalType":"uint64","name":"expirationDate","type":"uint64"},{"internalType":"bytes","name":"subject","type":"bytes"},{"internalType":"bytes","name":"attestationData","type":"bytes"}],"internalType":"struct AttestationPayload[]","name":"attestationsPayloads","type":"tuple[]"},{"internalType":"bytes[][]","name":"validationPayloads","type":"bytes[][]"}],"name":"bulkAttest","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32[]","name":"attestationIds","type":"bytes32[]"},{"components":[{"internalType":"bytes32","name":"schemaId","type":"bytes32"},{"internalType":"uint64","name":"expirationDate","type":"uint64"},{"internalType":"bytes","name":"subject","type":"bytes"},{"internalType":"bytes","name":"attestationData","type":"bytes"}],"internalType":"struct AttestationPayload[]","name":"attestationsPayloads","type":"tuple[]"},{"internalType":"bytes[][]","name":"validationPayloads","type":"bytes[][]"}],"name":"bulkReplace","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32[]","name":"attestationIds","type":"bytes32[]"}],"name":"bulkRevoke","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getAttester","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getModules","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"moduleRegistry","outputs":[{"internalType":"contract ModuleRegistry","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"modules","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"portalRegistry","outputs":[{"internalType":"contract PortalRegistry","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"attestationId","type":"bytes32"},{"components":[{"internalType":"bytes32","name":"schemaId","type":"bytes32"},{"internalType":"uint64","name":"expirationDate","type":"uint64"},{"internalType":"bytes","name":"subject","type":"bytes"},{"internalType":"bytes","name":"attestationData","type":"bytes"}],"internalType":"struct AttestationPayload","name":"attestationPayload","type":"tuple"},{"internalType":"bytes[]","name":"validationPayloads","type":"bytes[]"}],"name":"replace","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"attestationId","type":"bytes32"}],"name":"revoke","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"router","outputs":[{"internalType":"contract IRouter","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

    def random_private_key(self):
        curve_order = NIST256p.order
        private_key = randrange_from_seed__trytryagain(os.urandom(32), curve_order)
        return private_key.to_bytes(32, 'big')

    def get_uncompressed_public_key_from_private(self, private_key_hex):
        private_key_bytes = binascii.unhexlify(private_key_hex)
        sk = SigningKey.from_string(private_key_bytes, curve=NIST256p)
        vk = sk.verifying_key
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        public_key_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        public_key_hex = binascii.hexlify(public_key_bytes).decode('utf-8')
        return public_key_hex

    def generate_keys(self):
        private_key_bytes = self.random_private_key()
        private_key_hex = binascii.hexlify(private_key_bytes).decode('utf-8')

        return {
            'localPriv': private_key_hex,
            'localPubKey': self.get_uncompressed_public_key_from_private(private_key_hex)
        }

    def hex_to_binary_string(self, hex_string):
        bytes_data = bytes.fromhex(hex_string)
        binary_string = bytes_data.decode('latin-1')
        return binary_string

    def create_cipher(self, binary_key):
        key_bytes = binary_key.encode('latin-1')
        iv = b'\x00' * 12
        cipher = Cipher(
            algorithms.AES(key_bytes),
            modes.GCM(iv),
            backend=default_backend()
        )

        return cipher, iv

    def encrypt_data(self, plaintext, key_hex):
        try:
            key = self.hex_to_binary_string(key_hex)
            cipher, iv = self.create_cipher(key)
            encryptor = cipher.encryptor()

            ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

            tag_hex = encryptor.tag.hex()
            ciphertext_hex = ciphertext.hex()

            return tag_hex + ciphertext_hex
        except Exception:
            return None

    def get_shared_secret(self, private_key_hex, public_key_hex):
        private_key_bytes = binascii.unhexlify(private_key_hex)
        private_key = ec.derive_private_key(
            int.from_bytes(private_key_bytes, byteorder='big'),
            ec.SECP256R1(),
            default_backend()
        )

        public_key_bytes = binascii.unhexlify(public_key_hex)
        public_numbers = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(),
            public_key_bytes
        )

        shared_secret = private_key.exchange(ec.ECDH(), public_numbers)

        return shared_secret

    def decrypt_aes_gcm(self, encrypted_data_hex, key_hex):
        key = binascii.unhexlify(key_hex)
        encrypted_data = binascii.unhexlify(encrypted_data_hex)

        tag = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(b'\x00' * 12, tag),
            backend=default_backend()
        ).decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')

    def encode_account_plain(self, account_plain):
        account_plain = str(account_plain)
        utf8_encoded_bytes = account_plain.encode('utf-8')
        k = keccak.new(digest_bits=256)
        k.update(utf8_encoded_bytes)
        hash_hex = k.hexdigest()

        return "0x" + hash_hex

    def get_exchange_key(self, pub_key):
        for i in range(3):
            try:
                payload = {'client_id': 'demo', 'key': pub_key}
                result = self.help.fetch_url(url='https://openid3.dauth.network/dauth/sdk/v1.1/exchange_key', type='post', headers=self.headers, payload=payload)
                return result['data']
            except Exception:
                time.sleep(1)
        return

    def get_auth_in_one(self, encrypted, account, session_id):
        for i in range(3):
            try:
                payload = {
                    'client_id': 'demo',
                    'id_type': 'google',
                    'cipher_code': encrypted,
                    'session_id': session_id,
                    'request_id': account.address.lower(),
                    'sign_mode': 'proof',
                    'account_plain': True,
                }
                result = self.help.fetch_url(url='https://openid3.dauth.network/dauth/sdk/v1.1/auth_in_one', type='post', headers=self.headers, payload=payload)
                return result['data']
            except:
                time.sleep(1)
        return

    def check_minted(self, account):
        for i in range(3):
            try:
                payload = {
                    "query": f'''
                      query MyQuery {{
                        attestations(
                          where: {{
                            portal: "0xCe048492076b0130821866F6d05A0b621B1715C8",
                            subject: "{account.address}"
                          }}
                        ) {{
                          id
                        }}
                      }}'''
                }
                result = self.help.fetch_url(url='https://graph-query.linea.build/subgraphs/name/Consensys/linea-attestation-registry', type='post',payload=payload)
                if len(result['data']['attestations']) != 0:
                    return True
                else:
                    return False
            except:
                time.sleep(1)
        return

    def main(self, private_key, attempt=0, debug=False):

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

        already_minted = self.check_minted(account)
        if already_minted:
            self.logger.log_success(f"{self.project} | Уже есть аттестация, пропускаю!", account.address)
            return True

        keys = self.generate_keys()
        if not keys:
            if debug:
                print('keys')
            return self.main(private_key=private_key, attempt=attempt+1)

        exchange_keys = self.get_exchange_key(keys['localPubKey'])
        if not exchange_keys:
            if debug:
                print('exchange_keys')
            return self.main(private_key=private_key, attempt=attempt+1)

        shared_secret = self.get_shared_secret(keys['localPriv'], "04" + exchange_keys['key'])
        if not shared_secret:
            if debug:
                print('shared_secret')
            return self.main(private_key=private_key, attempt=attempt+1)
        key_full = binascii.hexlify(shared_secret).decode()
        key_hex = key_full[len(key_full) // 2:]

        account_data = None
        for acc_data in self.gmail_data:
            if acc_data['status'] == 0:
                acc_data['status'] = 1
                account_data = acc_data['data']
                break
        if not account_data:
            self.logger.log_error('Закончились аккаунты Gmail, завершаю', account.address)
            return True
        gmail_code = asyncio.run(get_gmail_code(account_data=account_data, proxy=private_key.get('proxy', None)))
        if not gmail_code:
            if debug:
                print('gmail_code')
            return self.main(private_key=private_key, attempt=attempt+1)

        encrypted_data = self.encrypt_data(gmail_code, key_hex)
        if not encrypted_data:
            if debug:
                print('encrypted_data')
            return self.main(private_key=private_key, attempt=attempt+1)

        auth_in_one = self.get_auth_in_one(encrypted_data, account, exchange_keys['session_id'])
        if not auth_in_one:
            if debug:
                print('auth_in_one')
            return self.main(private_key=private_key, attempt=attempt + 1)

        decrypted_data = self.decrypt_aes_gcm(auth_in_one, key_hex)
        if not decrypted_data:
            if debug:
                print('decrypted_data')
            return self.main(private_key=private_key, attempt=attempt + 1)
        decrypted_data = json.loads(decrypted_data)
        hashed_account_plain = self.encode_account_plain(decrypted_data['auth']['account_plain'])

        attestation_data = new_w3.codec.encode(["bytes32", "bytes32"], ['0x8f2f90d8304f6eb382d037c47a041d8c8b4d18bdd8b082fa32828e016a584ca7', hashed_account_plain])

        args = (
            (
                new_w3.to_bytes(hexstr="0x912214269b9b891a0d7451974030ba13207d3bf78e515351609de9dd8a339686"[2:]),  # bytes32
                0,  # uint64
                account.address,
                attestation_data,  # bytes
            ),
            [new_w3.to_bytes(hexstr=decrypted_data['signature'])]  # bytes[]
        )
        # encoded = new_w3.codec.encode(["(bytes32,uint64,bytes,bytes)","bytes[]"], args)
        # print(encoded.hex())

        func_ = getattr(self.contract.functions, 'attest')

        tx = make_tx(new_w3, account, value=0, args=args, func=func_, args_positioning=True)

        if tx == 'already_attested':
            return self.main(private_key=private_key, attempt=attempt + 1)

        if tx == "low_native" or not tx:
            return self.main(private_key=private_key, attempt=attempt + 1)

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, attempt=attempt + 1)
        self.logger.log_success(f"{self.project} | Успешно заминтил аттестацию!", account.address)
        return new_w3.to_hex(hash)

