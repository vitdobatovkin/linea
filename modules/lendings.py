from helpers.utils import *
from helpers.data import lending_data, tokens_data_

class Layerbank():
    def __init__(self, w3, logger, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'LAYERBANK'
        self.logger = logger
        self.eth_contract = w3.eth.contract(address=w3.to_checksum_address(lending_data[self.project]['contracts']['ETH']),abi=lending_data[self.project]['ABI']['ETH'])
        self.usdc_contract = w3.eth.contract(address=w3.to_checksum_address(lending_data[self.project]['contracts']['USDC']),abi=lending_data[self.project]['ABI']['USDC'])
        self.wsteth_contract = w3.eth.contract(address=w3.to_checksum_address(lending_data[self.project]['contracts']['WSTETH']),abi=lending_data[self.project]['ABI']['WSTETH'])
        self.markets_contract = w3.eth.contract(address=w3.to_checksum_address(lending_data[self.project]['contracts']['MARKETS']),abi=lending_data[self.project]['ABI']['MARKETS'])

    # def check_markets(self, account, new_w3, token_to_enable, attempt=0):
    #     addresses = self.markets_contract.functions.allMarkets().call()
    #     for address_ in addresses:
    #         if not self.markets_contract.functions.checkMembership(account.address, new_w3.to_checksum_address(address_)).call():
    #             func_ = getattr(self.markets_contract.functions, 'enterMarkets')
    #             tx = make_tx(new_w3, account, func=func_, args=addresses, args_positioning=False)
    #             if tx == "low_native" or not tx:
    #                 return tx
    #             hash, _ = send_tx(new_w3, account, tx)
    #             tx_status = check_for_status(new_w3, hash)
    #             if not tx_status:
    #                 if attempt>2:
    #                     return 'error'
    #                 return self.check_markets(account=account, new_w3=new_w3, attempt=attempt+1)
    #     return

    def check_markets(self, account, new_w3, token_to_enable, attempt=0):
        if not self.markets_contract.functions.checkMembership(account.address, new_w3.to_checksum_address(lending_data[self.project]['contracts'][token_to_enable])).call():
            func_ = getattr(self.markets_contract.functions, 'enterMarkets')
            tx = make_tx(new_w3, account, func=func_, args=[lending_data[self.project]['contracts'][token_to_enable]], args_positioning=False)
            if tx == "low_native" or not tx:
                return tx
            hash, _ = send_tx(new_w3, account, tx)
            tx_status = check_for_status(new_w3, hash)
            if not tx_status:
                if attempt>2:
                    return 'error'
                return self.check_markets(account=account, new_w3=new_w3, attempt=attempt+1)
        return

    def redeem(self, value, token, account, new_w3):
        func_ = getattr(self.markets_contract.functions, 'redeemToken')
        tx = make_tx(new_w3, account, value=0, func=func_, args=[lending_data[self.project]['contracts'][token], int(value * 0.9999)], args_positioning=True)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return None
        return new_w3.to_hex(hash)

    def mint(self, value, token, account, new_w3):

        if token != 'ETH':
            allowance = check_approve(new_w3, account, tokens_data_[token]['address'],  lending_data[self.project]['contracts'][token])
            if not allowance:
                make_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])

        func_ = getattr(self.markets_contract.functions, 'supply')

        tx = make_tx(new_w3, account, value=0 if token != 'ETH' else value, func=func_, args=[lending_data[self.project]['contracts'][token], value], args_positioning=True)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return None
        return new_w3.to_hex(hash)

    def borrow(self, value, token, token_to_enable, account, new_w3):

        tx_hash = self.check_markets(account, new_w3, token_to_enable)
        if tx_hash == 'error':
            return None

        func_ = getattr(self.markets_contract.functions, 'borrow')
        args = [lending_data[self.project]['contracts'][token], value]

        tx = make_tx(new_w3, account, value=0, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return None
        return new_w3.to_hex(hash)

    def repay(self, value, token, account, new_w3):

        if token != 'ETH':
            allowance = check_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])
            if not allowance:
                make_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])

        func_ = getattr(self.markets_contract.functions, 'repayBorrow')

        args = [lending_data[self.project]['contracts'][token], value-1]

        tx = make_tx(new_w3, account, value=0 if token != 'ETH' else value-1, func=func_, args=args, args_positioning=True)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return None
        return new_w3.to_hex(hash)

    def main(self, private_key, token, value, withdraw=False, attempt=0):

        value_ = int(value * 10 ** tokens_data_[token]['decimal'])
        self.prices = self.help.get_prices_reserved()

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if token != 'ETH':
            value_ = min(value_, get_balance(new_w3, account, tokens_data_[token]['address']))

        snapshot_eth = self.eth_contract.functions.accountSnapshot(account.address).call()
        snapshot_usdc = self.usdc_contract.functions.accountSnapshot(account.address).call()
        snapshot_wsteth = self.wsteth_contract.functions.accountSnapshot(account.address).call()
        balance, borrow_balance, rate = snapshot_eth
        balance_, borrow_balance_, rate_ = snapshot_usdc
        balance__, borrow_balance__, rate__ = snapshot_wsteth

        tokens = {}
        tokens['ETH'] = {"actual_supplied": int(balance), "actual_borrowed": borrow_balance, "protocol_borrower": borrow_balance, "repay_token": "ETH", 'decimals': 18}
        tokens['USDC'] = {"actual_supplied": int(balance_), "actual_borrowed": borrow_balance_, "protocol_borrower": borrow_balance_, "repay_token": "ETH", 'decimals': 18}
        tokens['WSTETH'] = {"actual_supplied": int(balance__), "actual_borrowed": borrow_balance__, "protocol_borrower": borrow_balance__, "repay_token": "ETH", 'decimals': 18}

        # if withdraw and (tokens['ETH']['actual_supplied'] < 10**12 and tokens['USDC']['actual_supplied'] < 10000 and tokens['ETH']['actual_borrowed'] < 10**12 and tokens['USDC']['actual_borrowed'] < 1000):
        #     return 'good'
        if withdraw and (tokens[token]['actual_supplied'] / (10 ** tokens[token]['decimals']) * self.prices[token] < 0.1):
            return 'good'

        total_supplied = sum(t['actual_supplied'] / (10 ** tokens_data_[token]['decimal']) * self.prices[token] for t in tokens.values())
        total_borrowed = sum(t['actual_borrowed'] / (10 ** tokens_data_[token]['decimal']) * self.prices[token] for t in tokens.values())
        try:
            ratio = total_borrowed / total_supplied
        except:
            ratio = 0
        max_borrow_value = total_supplied * 0.675 - total_borrowed

        need_borrow, need_supply, need_redeem = False, False, False
        if (tokens['ETH']['actual_supplied'] > 10 ** 16 or tokens['USDC']['actual_supplied'] > 10000000 or tokens['WSTETH']['actual_supplied'] > 10 ** 14) and (tokens['ETH']['actual_borrowed'] < 10 ** 12 and tokens['USDC']['actual_borrowed'] < 10000 and tokens['WSTETH']['actual_borrowed'] < 10 ** 12):
            need_borrow = True
        if ratio > 0.5 and total_borrowed > 0.1:
            need_redeem = True
        if not need_redeem and not need_borrow:
            need_supply = True
        if withdraw:
            need_borrow, need_supply, need_redeem = False, False, True

        if need_supply:
            self.logger.log(f"{self.project} | Делаю SUPPLY {round(value_ / (10 ** tokens[token]['decimals']), 6)} {token}", wallet=account.address)
            tx_hash = self.mint(value_, token, account, new_w3)
            if tx_hash and tx_hash != 'low_native':
                tx_status = check_for_status(new_w3, tx_hash)
                if not tx_status:
                    return self.main(private_key=private_key, token=token, value=value, withdraw=withdraw, attempt=attempt + 1)
                self.logger.log_success(f"{self.project} | Сделал SUPPLY ({round(value_ / (10 ** tokens[token]['decimals']), 6)} {token}) успешно!", wallet=account.address)
            return tx_hash
        elif need_borrow:
            borrow_value = random.randint(int(max_borrow_value * 0.975), int(max_borrow_value * 1)) / self.prices[token]
            self.logger.log(f"{self.project} | Делаю BORROW {round(borrow_value, 6)} {tokens[token]['repay_token']}", wallet=account.address)
            tx_hash = self.borrow(int(round(borrow_value, 6) * 10**tokens[tokens[token]['repay_token']]['decimals']), tokens[token]['repay_token'], token, account, new_w3)
            if tx_hash and tx_hash != 'low_native':
                self.logger.log_success(f"{self.project} | Сделал BORROW ({round(borrow_value, 6)} {tokens[token]['repay_token']}) успешно!", wallet=account.address)
            return tx_hash
        elif need_redeem:

            tx_hash = True

            if tokens[token]['actual_supplied'] == 0:
                return True

            balance = self.w3.eth.get_balance(account.address) if tokens[token]['repay_token'] == 'ETH' else get_balance(self.w3, account, tokens_data_[token]['address'])
            borrowed_value = min(balance, tokens[tokens[token]['repay_token']]['actual_borrowed'])

            if borrowed_value == 0 and tokens[tokens[token]['repay_token']]['actual_borrowed'] > balance:
                return f'swap_{tokens[token]["repay_token"]}_{tokens[tokens[token]["repay_token"]]["actual_borrowed"]-balance}'
            if borrowed_value > (100000 if tokens[token]['repay_token'] == 'USDC' else 10**12):
                self.logger.log(f"{self.project} | Делаю REPAY {round(borrowed_value / (10 ** tokens[tokens[token]['repay_token']]['decimals']), 6)} {tokens[token]['repay_token']}",wallet=account.address)
                tx_hash = self.repay(borrowed_value, tokens[token]['repay_token'], account, new_w3)
                if tx_hash and tx_hash != 'low_native':
                    self.logger.log_success(f"{self.project} | Сделал REPAY ({round(borrowed_value / (10 ** tokens[tokens[token]['repay_token']]['decimals']), 6)} {tokens[token]['repay_token']}) успешно!", wallet=account.address)
                time.sleep(random.uniform(3, 5))

            if (tokens[token]['actual_supplied'] > 10**12 if token in ['ETH', 'WSTETH'] else 100000) and tokens[token]['actual_supplied'] != 0:
                self.logger.log(f"{self.project} | Делаю WITHDRAW {round(tokens[token]['actual_supplied'] / (10 ** tokens[token]['decimals']), 6)} {token}", wallet=account.address)
                tx_hash_ = self.redeem(tokens[token]['actual_supplied'], token, account, new_w3)
                if tx_hash_ and tx_hash_ != 'low_native':
                    tx_status = check_for_status(new_w3, tx_hash_)
                    if not tx_status:
                        return self.main(private_key=private_key, token=token, value=value, withdraw=withdraw, attempt=attempt + 1)
                    self.logger.log_success(f"{self.project} | Сделал WITHDRAW ({round(tokens[token]['actual_supplied'] / (10 ** tokens[token]['decimals']), 6)} {token}) успешно!", wallet=account.address)
                return tx_hash_
            else:
                return tx_hash

class Mendi():
    def __init__(self, w3, logger, helper):
        self.help = helper
        self.w3 = w3
        self.project = 'MENDI'
        self.logger = logger
        self.eth_contract = w3.eth.contract( address=w3.to_checksum_address(lending_data[self.project]['contracts']['ETH']), abi=lending_data[self.project]['ABI']['ETH'])
        self.usdc_contract = w3.eth.contract(address=w3.to_checksum_address(lending_data[self.project]['contracts']['USDC']),abi=lending_data[self.project]['ABI']['USDC'])
        self.wsteth_contract = w3.eth.contract( address=w3.to_checksum_address(lending_data[self.project]['contracts']['WSTETH']), abi=lending_data[self.project]['ABI']['WSTETH'])
        self.markets_contract = w3.eth.contract( address=w3.to_checksum_address(lending_data[self.project]['contracts']['MARKETS']),abi=lending_data[self.project]['ABI']['MARKETS'])
        self.contracts = {
            'ETH': self.eth_contract,
            'USDC': self.usdc_contract,
            'WSTETH': self.wsteth_contract,
        }

    def update_tokens(self, account):
        snapshot_eth = self.eth_contract.functions.getAccountSnapshot(account.address).call()
        snapshot_usdc = self.usdc_contract.functions.getAccountSnapshot(account.address).call()
        snapshot_wsteth = self.wsteth_contract.functions.getAccountSnapshot(account.address).call()
        _, balance, borrow_balance, rate = snapshot_eth
        _, balance_, borrow_balance_, rate_ = snapshot_usdc
        _, balance__, borrow_balance__, rate__ = snapshot_wsteth
        tokens = {}
        tokens['ETH'] = {"actual_supplied": int(balance * rate / (10 ** 18)), "protocol_supplied": balance, "actual_borrowed": borrow_balance, "protocol_borrower": borrow_balance, "repay_token": "ETH", 'decimals': 18}
        tokens['USDC'] = {"actual_supplied": int(balance_ * rate_ / (10 ** 18)), "protocol_supplied": balance_, "actual_borrowed": borrow_balance_, "protocol_borrower": borrow_balance_, "repay_token": "ETH", 'decimals': 18}
        tokens['WSTETH'] = {"actual_supplied": int(balance__ * rate__ / (10 ** 18)), "protocol_supplied": balance__, "actual_borrowed": borrow_balance__, "protocol_borrower": borrow_balance__, "repay_token": "ETH", 'decimals': 18}

        return tokens

    # def check_markets(self, account, new_w3, token_to_enable, attempt=0):
    #     addresses = self.markets_contract.functions.getAllMarkets().call()
    #     for address_ in addresses:
    #         if not self.markets_contract.functions.checkMembership(account.address, new_w3.to_checksum_address(address_)).call():
    #             func_ = getattr(self.markets_contract.functions, 'enterMarkets')
    #             tx = make_tx(new_w3, account, func=func_, args=addresses, args_positioning=False)
    #             if tx == "low_native" or not tx:
    #                 return tx
    #             sign = account.sign_transaction(tx)
    #             hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
    #             tx_status = check_for_status(new_w3, hash)
    #             if not tx_status:
    #                 if attempt > 2:
    #                     return 'error'
    #                 return self.check_markets(account=account, new_w3=new_w3, attempt=attempt + 1)
    #             return new_w3.to_hex(hash)
    #     return

    def check_markets(self, account, new_w3, token_to_enable, attempt=0):
        if not self.markets_contract.functions.checkMembership(account.address, new_w3.to_checksum_address(lending_data[self.project]['contracts'][token_to_enable])).call():
            func_ = getattr(self.markets_contract.functions, 'enterMarkets')
            tx = make_tx(new_w3, account, func=func_, args=[new_w3.to_checksum_address(lending_data[self.project]['contracts'][token_to_enable])], args_positioning=False)
            if tx == "low_native" or not tx:
                return tx
            sign = account.sign_transaction(tx)
            hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
            tx_status = check_for_status(new_w3, hash)
            if not tx_status:
                if attempt > 2:
                    return 'error'
                return self.check_markets(account=account, new_w3=new_w3, attempt=attempt + 1)
            return new_w3.to_hex(hash)
        return

    def redeem(self, value, token, account, new_w3):
        func_ = getattr(self.contracts[token].functions, 'redeem')
        tx = make_tx(new_w3, account, value=0, func=func_, args=int(value*0.9999), args_positioning=False)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return
        return new_w3.to_hex(hash)

    def mint(self, value, token, account, new_w3):

        allowance = check_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])
        if not allowance:
            make_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])

        func_ = getattr(self.contracts[token].functions, 'mint')
        tx = make_tx(new_w3, account, value=0, func=func_, args=int(value * 0.99999), args_positioning=False)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return
        return new_w3.to_hex(hash)

    def borrow(self, value, token, token_to_enable, account, new_w3):

        tx_hash = self.check_markets(account, new_w3, token_to_enable)
        if tx_hash == 'error':
            return None
        time.sleep(random.uniform(3, 5))

        func_ = getattr(self.contracts[token].functions, 'borrow')
        tx = make_tx(new_w3, account, value=0, func=func_, args=value, args_positioning=False)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return
        return new_w3.to_hex(hash)

    def repay(self, value, token, account, new_w3):

        allowance = check_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])
        if not allowance:
            make_approve(new_w3, account, tokens_data_[token]['address'], lending_data[self.project]['contracts'][token])

        func_ = getattr(self.contracts[token].functions, 'repayBorrow')
        tx = make_tx(new_w3, account, value=0, func=func_, args=int(value*0.9999999), args_positioning=False)
        if tx == "low_native" or not tx:
            return tx
        sign = account.sign_transaction(tx)
        hash = new_w3.eth.send_raw_transaction(sign.rawTransaction)
        tx_status = check_for_status(new_w3, hash)
        if not tx_status:
            return
        return new_w3.to_hex(hash)

    def main(self, private_key, token, value, withdraw=False, attempt=0):

        value_ = int(value * 10 ** tokens_data_[token]['decimal'])
        self.prices = self.help.get_prices_reserved()

        try:
            if private_key.get('proxy', None):
                new_w3 = self.help.get_web3(private_key['proxy'], self.w3)
            else:
                raise Exception
        except Exception:
            new_w3 = self.w3

        account = new_w3.eth.account.from_key(private_key['private_key'])

        if token != 'ETH':
            value_ = min(value_, get_balance(new_w3, account, tokens_data_[token]['address']))

        tokens = self.update_tokens(account)

        total_supplied = sum(t['actual_supplied'] / (10 ** tokens_data_[token]['decimal']) * self.prices[token] for t in tokens.values())
        total_borrowed = sum(t['actual_borrowed'] / (10 ** tokens_data_[token]['decimal']) * self.prices[token] for t in tokens.values())
        try:
            ratio = total_borrowed / total_supplied
        except:
            ratio = 0
        max_borrow_value = total_supplied * 0.675 - total_borrowed

        if withdraw and (tokens['ETH']['actual_supplied'] < 10 ** 12 and tokens['USDC']['actual_supplied'] < 100000 and tokens['ETH']['actual_borrowed'] < 10 ** 12 and tokens['USDC']['actual_borrowed'] < 100000 and tokens['WSTETH']['actual_supplied'] < 10 ** 12 and tokens['WSTETH']['actual_borrowed'] < 10 ** 12):
            return 'good'

        need_borrow, need_supply, need_redeem = False, False, False
        if (tokens['ETH']['actual_supplied'] > 10 ** 16 or tokens['USDC']['actual_supplied'] > 10000000 or tokens['WSTETH']['actual_supplied'] > 10 ** 14) and (tokens['ETH']['actual_borrowed'] < 10 ** 12 and tokens['USDC']['actual_borrowed'] < 100000 and tokens['WSTETH']['actual_borrowed'] < 10 ** 12):
            need_borrow = True
        if ratio > 0.25 and total_borrowed > 0.1:
            need_redeem = True
        if not need_redeem and not need_borrow:
            need_supply = True
        if withdraw:
            need_borrow, need_supply, need_redeem = False, False, True

        if need_supply or need_redeem and token == 'ETH':
            weth_value = get_balance(new_w3, account, '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f')
            if weth_value < value_:
                wrap = eth_wrapper(int(value_-weth_value), 'WETH', new_w3, private_key['private_key'], in_decimals=False)

        if need_supply:
            self.logger.log(f"{self.project} | Делаю SUPPLY {round(value_ / (10 ** tokens[token]['decimals']), 6)} {token}", wallet=account.address)
            tx_hash = self.mint(value_, token, account, new_w3)
            if tx_hash and tx_hash != 'low_native':
                tx_status = check_for_status(new_w3, tx_hash)
                if not tx_status:
                    return self.main(private_key=private_key, token=token, value=value, withdraw=withdraw, attempt=attempt + 1)
                self.logger.log_success( f"{self.project} | Сделал SUPPLY ({round(value_ / (10 ** tokens[token]['decimals']), 6)} {token}) успешно!",wallet=account.address)
            return tx_hash
        elif need_borrow:
            borrow_value = random.randint(int(max_borrow_value * 0.975), int(max_borrow_value * 1)) / self.prices[token]
            self.logger.log(f"{self.project} | Делаю BORROW {round(borrow_value, 6)} {tokens[token]['repay_token']}", wallet=account.address)
            tx_hash = self.borrow(int(borrow_value * 10 ** tokens[tokens[token]['repay_token']]['decimals']), tokens[token]['repay_token'], token, account, new_w3)
            if tx_hash and tx_hash != 'low_native':
                self.logger.log_success( f"{self.project} | Сделал BORROW ({round(borrow_value, 6)} {tokens[token]['repay_token']}) успешно!", wallet=account.address)
            return tx_hash
        elif need_redeem:
            tx_hash = True

            if tokens[token]['actual_supplied'] == 0:
                return True

            balance = get_balance(self.w3, account, tokens_data_[tokens[token]['repay_token']]['address'])
            borrowed_value = min(balance, tokens[tokens[token]['repay_token']]['actual_borrowed'])

            if borrowed_value == 0 and tokens[tokens[token]['repay_token']]['actual_borrowed'] > balance:
                return f'swap_{tokens[token]["repay_token"]}_{tokens[tokens[token]["repay_token"]]["actual_borrowed"] - balance}'
            if borrowed_value > (100000 if tokens[token]['repay_token'] == 'USDC' else 10 ** 12):
                self.logger.log(f"{self.project} | Делаю REPAY {round(borrowed_value / (10 ** tokens[tokens[token]['repay_token']]['decimals']), 6)} {tokens[token]['repay_token']}",wallet=account.address)
                tx_hash = self.repay(borrowed_value, tokens[token]['repay_token'], account, new_w3)
                if tx_hash and tx_hash != 'low_native':
                    self.logger.log_success(f"{self.project} | Сделал REPAY ({round(borrowed_value / (10 ** tokens[tokens[token]['repay_token']]['decimals']), 6)} {tokens[token]['repay_token']}) успешно!", wallet=account.address)
                time.sleep(random.uniform(3, 5))

            withdraw_value = tokens[token]['protocol_supplied']

            if (tokens[token]['actual_supplied'] > 10 ** 12 if token in ['ETH', 'WSTETH'] else 100000) and tokens[token]['actual_supplied'] != 0:
                self.logger.log( f"{self.project} | Делаю WITHDRAW {round(tokens[token]['actual_supplied'] / (10 ** tokens[token]['decimals']), 6)} {token}", wallet=account.address)
                tx_hash_ = self.redeem(withdraw_value, token, account, new_w3)
                if tx_hash_ and tx_hash_ != 'low_native':
                    tx_status = check_for_status(new_w3, tx_hash_)
                    if not tx_status: return self.main(private_key=private_key, token=token, value=value, withdraw=withdraw,attempt=attempt + 1)
                    self.logger.log_success( f"{self.project} | Сделал WITHDRAW ({round(tokens[token]['actual_supplied'] / (10 ** tokens[token]['decimals']), 6)} {token}) успешно!", wallet=account.address)
                return tx_hash_
            else:
                return tx_hash


def initialize_lendings(classes_to_init, w3, logger, helper):
    available_swaps = {
        "Layerbank": Layerbank,
        "Mendi": Mendi,
    }

    initialized_objects = {}

    for class_name, should_init in classes_to_init.items():
        if should_init:
            initialized_objects[class_name] = available_swaps[class_name](w3, logger, helper)

    return initialized_objects

