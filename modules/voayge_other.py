from helpers.utils import *
from eth_account.messages import encode_structured_data
from eth_account import Account

class Airswap():

    def __init__(self, helper, logger, w3):

        self.project = 'AIRSWAP'
        self.orders = []
        self.busy = False

        self.w3 = w3
        self.help = helper
        self.logger = logger

        self.types = {
            'EIP712Domain': [
                {'name': 'name', 'type': 'string'},
                {'name': 'version', 'type': 'string'},
                {'name': 'chainId', 'type': 'uint256'},
                {'name': 'verifyingContract', 'type': 'address'},
            ],
            'OrderERC20': [
                {'name': 'nonce', 'type': 'uint256'},
                {'name': 'expiry', 'type': 'uint256'},
                {'name': 'signerWallet', 'type': 'address'},
                {'name': 'signerToken', 'type': 'address'},
                {'name': 'signerAmount', 'type': 'uint256'},
                {'name': 'protocolFee', 'type': 'uint256'},
                {'name': 'senderWallet', 'type': 'address'},
                {'name': 'senderToken', 'type': 'address'},
                {'name': 'senderAmount', 'type': 'uint256'},
            ],
        }
        self.domain = {
            'name': 'SWAP_ERC20',
            'version': '4.1',
            'chainId': 59144,
            'verifyingContract': '0x0C9b31Dc37718417608CE22bb1ba940f702BF90B',
        }

        self.contract = self.w3.eth.contract(address='0x0C9b31Dc37718417608CE22bb1ba940f702BF90B', abi='[{"inputs":[{"internalType":"uint256","name":"_protocolFee","type":"uint256"},{"internalType":"uint256","name":"_protocolFeeLight","type":"uint256"},{"internalType":"address","name":"_protocolFeeWallet","type":"address"},{"internalType":"uint256","name":"_discountScale","type":"uint256"},{"internalType":"uint256","name":"_discountMax","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"ChainIdChanged","type":"error"},{"inputs":[],"name":"InvalidFee","type":"error"},{"inputs":[],"name":"InvalidFeeLight","type":"error"},{"inputs":[],"name":"InvalidFeeWallet","type":"error"},{"inputs":[],"name":"InvalidShortString","type":"error"},{"inputs":[],"name":"InvalidStaking","type":"error"},{"inputs":[],"name":"MaxTooHigh","type":"error"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"NonceAlreadyUsed","type":"error"},{"inputs":[],"name":"OrderExpired","type":"error"},{"inputs":[],"name":"ScaleTooHigh","type":"error"},{"inputs":[],"name":"SignatoryInvalid","type":"error"},{"inputs":[],"name":"SignatoryUnauthorized","type":"error"},{"inputs":[],"name":"SignatureInvalid","type":"error"},{"inputs":[{"internalType":"string","name":"str","type":"string"}],"name":"StringTooLong","type":"error"},{"inputs":[],"name":"Unauthorized","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"signer","type":"address"},{"indexed":true,"internalType":"address","name":"signerWallet","type":"address"}],"name":"Authorize","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":true,"internalType":"address","name":"signerWallet","type":"address"}],"name":"Cancel","type":"event"},{"anonymous":false,"inputs":[],"name":"EIP712DomainChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"signer","type":"address"},{"indexed":true,"internalType":"address","name":"signerWallet","type":"address"}],"name":"Revoke","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"discountMax","type":"uint256"}],"name":"SetDiscountMax","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"discountScale","type":"uint256"}],"name":"SetDiscountScale","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"protocolFee","type":"uint256"}],"name":"SetProtocolFee","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"protocolFeeLight","type":"uint256"}],"name":"SetProtocolFeeLight","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"feeWallet","type":"address"}],"name":"SetProtocolFeeWallet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"staking","type":"address"}],"name":"SetStaking","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":true,"internalType":"address","name":"signerWallet","type":"address"}],"name":"SwapERC20","type":"event"},{"inputs":[],"name":"DOMAIN_CHAIN_ID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_NAME","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_VERSION","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"FEE_DIVISOR","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ORDER_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"signatory","type":"address"}],"name":"authorize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"authorized","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"stakingBalance","type":"uint256"},{"internalType":"uint256","name":"feeAmount","type":"uint256"}],"name":"calculateDiscount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"wallet","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"calculateProtocolFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"nonces","type":"uint256[]"}],"name":"cancel","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"senderWallet","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"address","name":"signerWallet","type":"address"},{"internalType":"address","name":"signerToken","type":"address"},{"internalType":"uint256","name":"signerAmount","type":"uint256"},{"internalType":"address","name":"senderToken","type":"address"},{"internalType":"uint256","name":"senderAmount","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"check","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes32[]","name":"","type":"bytes32[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"discountMax","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"discountScale","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"eip712Domain","outputs":[{"internalType":"bytes1","name":"fields","type":"bytes1"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"version","type":"string"},{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"address","name":"verifyingContract","type":"address"},{"internalType":"bytes32","name":"salt","type":"bytes32"},{"internalType":"uint256[]","name":"extensions","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"signer","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"nonceUsed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeLight","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeWallet","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"revoke","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_discountMax","type":"uint256"}],"name":"setDiscountMax","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_discountScale","type":"uint256"}],"name":"setDiscountScale","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_protocolFee","type":"uint256"}],"name":"setProtocolFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_protocolFeeLight","type":"uint256"}],"name":"setProtocolFeeLight","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_protocolFeeWallet","type":"address"}],"name":"setProtocolFeeWallet","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_stakingToken","type":"address"}],"name":"setStaking","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"stakingToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"address","name":"signerWallet","type":"address"},{"internalType":"address","name":"signerToken","type":"address"},{"internalType":"uint256","name":"signerAmount","type":"uint256"},{"internalType":"address","name":"senderToken","type":"address"},{"internalType":"uint256","name":"senderAmount","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"address","name":"signerWallet","type":"address"},{"internalType":"address","name":"signerToken","type":"address"},{"internalType":"uint256","name":"signerAmount","type":"uint256"},{"internalType":"address","name":"senderToken","type":"address"},{"internalType":"uint256","name":"senderAmount","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"swapAnySender","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"address","name":"signerWallet","type":"address"},{"internalType":"address","name":"signerToken","type":"address"},{"internalType":"uint256","name":"signerAmount","type":"uint256"},{"internalType":"address","name":"senderToken","type":"address"},{"internalType":"uint256","name":"senderAmount","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"swapLight","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

    def create_order(self, new_w3, account, amount):

        balance = get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f')
        if balance < amount:
            needed_value = amount-balance
            wrap = eth_wrapper(int(needed_value), 'WETH', new_w3, account._private_key, in_decimals=False)

        time.sleep(random.uniform(5, 10))

        approve = check_approve(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f', '0x0C9b31Dc37718417608CE22bb1ba940f702BF90B')
        if not approve:
            make_approve(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f', '0x0C9b31Dc37718417608CE22bb1ba940f702BF90B')

        order_time = time.time()
        message = {
            "expiry": int(order_time + 60 * 60 * 12),  # int
            "nonce": int(order_time * 1000),  # int
            "protocolFee": 7,  # int fixed
            "senderAmount": int(amount),  # int
            "senderToken": '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f',  # weth
            "senderWallet": '0x0000000000000000000000000000000000000000',
            "signerAmount": int(amount),  # int
            "signerToken": '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f',  # weth
            "signerWallet": account.address,

        }
        message_to_sign = {
            'domain': self.domain,
            'types': self.types,
            'message': message,
            'primaryType': 'OrderERC20'
        }

        encoded_message = encode_structured_data(message_to_sign)
        signed_message = Account.sign_message(encoded_message, account._private_key)

        order_id = len(self.orders)

        self.orders.append({"order": message, "sig": signed_message, "status": 0, "order_id": order_id})

        return order_id

    def fill_order(self, new_w3, unfilled_order, amount, private_key, account, attempt):

        balance = get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f')
        if balance < unfilled_order['order']['signerAmount']:
            needed_value = unfilled_order['order']['signerAmount'] - balance
            wrap = eth_wrapper(int(needed_value), 'WETH', new_w3, account._private_key, in_decimals=False)

        time.sleep(random.uniform(5, 10))

        approve = check_approve(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f','0x0C9b31Dc37718417608CE22bb1ba940f702BF90B')
        if not approve:
            make_approve(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f','0x0C9b31Dc37718417608CE22bb1ba940f702BF90B')

        ord_data = unfilled_order['order']
        sig_data = unfilled_order['sig']
        v, r, s = sig_data['v'], new_w3.to_bytes(hexstr=(hex(sig_data['r']))[2:]), new_w3.to_bytes(hexstr=(hex(sig_data['s']))[2:])

        args = account.address, ord_data['nonce'], ord_data['expiry'], ord_data['signerWallet'], ord_data['signerToken'], ord_data['signerAmount'], ord_data['senderToken'], ord_data['senderAmount'], v, r, s
        func_ = getattr(self.contract.functions, 'swapAnySender')

        tx = make_tx(new_w3, account, value=0, args=args, func=func_, args_positioning=True)

        if tx == "low_native" or not tx:
            self.orders[unfilled_order['order_id']]['status'] = 0

            return self.main(private_key=private_key, amount=amount, attempt=attempt + 1)

        hash, _ = send_tx(new_w3, account, tx)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return self.main(private_key=private_key, amount=amount, attempt=attempt + 1)

        return True

    def wait_for_order_fill(self, order_id):

        while True:
            try:
                if self.orders[order_id]['status'] == 2:
                    return True
                else:
                    raise Exception
            except Exception:
                time.sleep(random.uniform(60, 120))

    def convert_weth(self, new_w3, account):

        while True:
            try:
                balance = get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f')
                if balance:
                    wrap = eth_wrapper(int(balance), 'ETH', new_w3, account._private_key, in_decimals=False)
                    time.sleep(random.uniform(5, 10))

                return True
            except:
                time.sleep(random.uniform(5, 10))

    def main(self, private_key, amount, attempt=0):

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

        while True:
            if not self.busy:
                self.busy = True
                break
            else:
                time.sleep(random.uniform(60, 150))

        unfilled_order = None
        for order in self.orders:
            if order['status'] == 0:
                order['status'] = 1
                unfilled_order = order

        if not unfilled_order:

            amount_ = int(amount * 10 ** 18)
            order_id = self.create_order(new_w3, account, amount_)
            self.busy = False
            self.logger.log_success(f"{self.project} | Успешно сделал ордер, жду заполнения...", account.address)
            self.wait_for_order_fill(order_id)
            self.logger.log_success(f"{self.project} | Ордер заполнен, конвертирую WETH...", account.address)
            self.convert_weth(new_w3, account)
            self.logger.log_success(f"{self.project} | Закончил работу!", account.address)
            return True

        else:

            self.logger.log_success(f"{self.project} | Нашёл ордер для заполнения...", account.address)
            order_fill = self.fill_order(new_w3, unfilled_order, amount, private_key, account, attempt=attempt)
            self.orders[unfilled_order['order_id']]['status'] = 2
            self.busy = False
            self.logger.log_success(f"{self.project} | Заполнил ордер, конвертирую WETH...", account.address)
            self.convert_weth(new_w3, account)
            self.logger.log_success(f"{self.project} | Закончил работу!", account.address)
            return True
