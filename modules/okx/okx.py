from helpers.logger import Logger
from helpers.help import helper
import random, re, pyotp, time
from modules.okx.mail_module import imaplib, get_code


class OKEX():

    def __init__(self, settings, logger, helper):

        self.auth = settings['okx_auth']
        self.devid = settings['okx_devid']
        self.tfa = settings['okx_2fa']
        self.mail = settings['okx_mail']
        self.mail_pass = settings['okx_mail_pass']
        self.imap = settings['okx_imap']
        self.helper = helper
        self.logger = logger
        self.last_code = 000000
        self.subs_auth = {}
        self.wallets = {}
        self.subs_to_task = {}
        self.busy = False
        self.data = {
            "ETH": {"name": 'ETH', "id": 2, "sub_id": 2},
            "ARB": {"name": 'ARB', "id": 2, "sub_id": 1917},
            "OPT": {"name": 'OPT', "id": 2, "sub_id": 1999},
            "LINEA": {"name": 'LINEA', 'id': 2, 'sub_id': 2868},
        }
        self.add_wl_data = None

    def get_timestamp(self):
        timestamp = int(time.time() * 1000)
        return timestamp

    def get_headers(self, auth=False):
        headers = {
            "authorization": auth if auth else self.auth,
            'timeout': '10000',
            'timesout': '10000',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0',
            "accept": "application/json",
            'devid': self.devid,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru-RU',
            'app-type': 'web',
        }
        return headers

    def check_tfa(self):
        try:
            TFA = pyotp.TOTP(self.tfa)
            tfa_code = TFA.now()
            return TFA
        except:
            return False

    def check_email(self):
        for i in range(5):
            try:
                imap = imaplib.IMAP4_SSL(self.imap)
                imap.login(self.mail, self.mail_pass)
                check = True
            except:
                check = False
        if check == True:
            return check
        return False

    def check_okx(self):
        balance_transfered = self.transfer_all_from_subs()
        if balance_transfered is False or balance_transfered == "bad_auth":
            return False
        return True

    def check_deposit_status(self, address, auth):
        for i in range(25):
            try:
                url_dep = f"https://www.okx.com/v2/asset/deposit/list?t={self.get_timestamp()}&currentPage=1&pageLength=100&currencyId=2"
                res = self.helper.fetch_url(url=url_dep, type='get', headers=self.get_headers(auth=auth))
                if res["code"] == 0:
                    for i in res["data"]["rechargeHistory"]:
                        if i["address"].lower() == address.lower():# and float("{:.6f}".format(float(i["amount"]))) == float("{:.6f}".format(amount)):
                            return True, int(i["statusNum"])
                    return "not_found", 0
                elif res["code"] == 800:
                    return "bad_auth", 0
                else:
                    if res['code'] == 50011:
                        time.sleep(1)
                        continue
                    return "error", 0
            except:
                return False, 0

    def get_all_accs(self):
        url = f"https://www.okx.com/v3/users/subaccount/accountListForSwitching?t={self.get_timestamp()}"
        res = self.helper.fetch_url(url=url, type='get', headers=self.get_headers())
        if res["code"] == 0:
            return res["data"]
        elif res["code"] == 800:
            return "bad_auth"
        return False

    def transfer_all_from_sub(self, log):
        url_switch = f"https://www.okx.com/v3/users/subaccount/switchAccount?t={self.get_timestamp()}"
        payload = {"loginId": log}
        res = self.helper.fetch_url(url=url_switch, type='post', payload=payload, headers=self.get_headers())
        if res["code"] == 800:
            return "bad_auth"
        token = res["data"]["token"]

        self.auth_ = self.auth
        self.auth = token

        url = f"https://www.okx.com/v2/asset/balance?t={self.get_timestamp()}&transferFrom=6&valuationUnit=USDT"
        res = self.helper.fetch_url(url=url, type='get', headers=self.get_headers())
        if res["code"] != 0:
            if res["code"] == 800:
                return "bad_auth"
            return False
        else:
            balances = res["data"]["balance"]

        self.auth = self.auth_

        for b in balances:
            if float(b["balance"]) != 0:
                balance = self.get_balance(log, b["currencyId"])
                transfer, msg = self.transfer_from_sub(b["currencyId"], balance, log)
                if transfer == "bad_auth":
                    return "bad_auth"
                time.sleep(0.5)
        return True

    def get_balance(self, log, id):
        code = 1
        while code != 0:
            url = f"https://www.okx.com/v2/asset/accounts/transfer?t={self.get_timestamp()}&transferFrom=6&transferTo=6&currencyId={id}&productId=-1&invalidAsset=false&subAccount={log}"
            res = self.helper.fetch_url(url=url, type='get', headers=self.get_headers())
            code = res["code"]
        return res["data"]["max"]

    def transfer_from_sub(self, id, value, login):
        url = f"https://www.okx.com/v2/asset/accounts/transfer?t={self.get_timestamp()}"
        payload = {"amount": value, "currencyId": id, "productId": -1, "subAccount": login, "toProductId": -1,
                   "transferFrom": 6, "masterOut": False, "transferTo": 6, "loanTrans": False, "omitPosRisk": False,
                   "invalidAsset": False}
        res = self.helper.fetch_url(url=url, type='post', payload=payload, headers=self.get_headers())
        if res["code"] == 0:
            return True, res["msg"]
        else:
            if res["code"] == 800:
                return "bad_auth", res["msg"]
            return False, res["msg"]

    def switch_acc(self, log):
        url_switch = f"https://www.okx.com/v3/users/subaccount/switchAccount?t={self.get_timestamp()}"
        payload = {"loginId": log}
        res = self.helper.fetch_url(url=url_switch, type='post', payload=payload, headers=self.get_headers())
        if res["code"] == 0:
            token = res["data"]["token"]
            return token
        elif res["code"] == 3905:
            return "wrong_login"
        elif res["code"] == 800:
            return "bad_auth"
        return False

    def transfer_all_from_subs(self):

        accs = self.get_all_accs()
        if not accs:
            return False
        elif accs == "bad_auth":
            return accs

        if len(accs) - 1 == 0:
            return True
        balance_transfered = 0
        for acc in accs:
            if not acc["masterAccount"]:
                log = acc["loginId"]
                url_switch = f"https://www.okx.com/v3/users/subaccount/switchAccount?t={self.get_timestamp()}"
                payload = {"loginId": log}
                for i in range(3):
                    res = self.helper.fetch_url(url=url_switch, headers=self.get_headers(), payload=payload, type='post')
                    if res['code'] != 0:
                        if res['code'] == 3113:
                            pass
                        else:
                            pass
                        if "IP" in str(res['msg']):
                           pass #change proxy
                    else:
                        break
                token = res["data"]["token"]


                url = f"https://www.okx.com/v2/asset/balance?t={self.get_timestamp()}&transferFrom=6&valuationUnit=USDT"
                res = self.helper.fetch_url(url=url, headers=self.get_headers(auth=token), type='get')
                balance_transfered += float(res["data"]["usdTotalValuation"])
                if res["code"] != 0:
                    continue
                else:
                    balances = res["data"]["balance"]

                for b in balances:
                    if float(b["balance"]) != 0:
                        balance = self.get_balance(log, b["currencyId"])
                        res, text = self.transfer_from_sub(b["currencyId"], balance, log)
                        if res:
                           pass
                        else:
                           pass
                        time.sleep(1)
            time.sleep(1)
        return balance_transfered

    def get_dep_addresses(self, auth):
        url_list = f"https://www.okx.com/v2/asset/deposit/address/list?t={self.get_timestamp()}&currencyId=2&subCurrencyId=2&all=true"
        res = self.helper.fetch_url(url=url_list, type='get', headers=self.get_headers(auth=auth))
        if res["code"] != 0:
            if res["code"] == 800:
                return "bad_auth"
            return False
        addresses = len(res["data"])
        while True:
            if addresses == 20:
                break
            r = self.create_address(auth=auth)
            if r is True:
                addresses += 1
            else:
                if r == "bad_auth":
                    return r
                continue
        addresses_list = []
        url_list = f"https://www.okx.com/v2/asset/deposit/address/list?t={self.get_timestamp()}&currencyId=2&subCurrencyId=2&all=true"
        res = self.helper.fetch_url(url=url_list, type='get', headers=self.get_headers(auth=auth))
        if res["code"] != 0:
            if res["code"] == 800:
                return "bad_auth"
            return False
        for i in res['data']:
            addresses_list.append(i["address"])
        return addresses_list

    def create_address(self, auth):
        url = f"https://www.okx.com/v2/asset/deposit/address?t={self.get_timestamp()}"
        payload = {"currencyId": 2, "subCurrencyId": 2, "isIsolationAddress": False}
        res = self.helper.fetch_url(url=url, type='post', payload=payload, headers=self.get_headers(auth=auth))
        if res["code"] == 0:
            return True
        else:
            if res["code"] == 800:
                return "bad_auth"
            return False

    #RETURNS RESULT IF ADDRESS WL
    def is_wl(self, address, id, sub_id):

        for i in range(10):
            address = address.lower()
            url = f"https://www.okx.com/v2/asset/withdraw/address-by-type?t={self.get_timestamp()}&type=0&currencyId={id}"
            result = self.helper.fetch_url(url=url, type="get", headers=self.get_headers())
            if result["code"] == 0:
                for i in result["data"]["addressList"]:
                    if i["address"].lower() == address.lower() and int(i["generalType"]) == 2:
                        return True, address
                return False, address
            elif int(result["code"]) == 50011:
                time.sleep(random.uniform(3, 6))
                continue
            elif int(result["code"]) == 800:
                return "bad_auth", address
            else:
                time.sleep(random.uniform(5, 10))
        return False, address

    #ADDING MAX 20 WALLETS TO WL IN CHAIN-TOKEN
    def okx_add_wl_batch(self, addresses, id, sub_id):

        addr_str = ''
        for i, address in enumerate(addresses):
            if i > 0:
                addr_str += ','
            addr_str += address

        while True:
            mail_code = None
            while True:

                url_email = f"https://www.okx.com/v2/asset/withdraw/add/address/sendEmailCode?t={self.get_timestamp()}&addressStr={addr_str}&includeAuth=true"
                res_email = self.helper.fetch_url(url_email, "get", headers=self.get_headers())
                if res_email["code"] == 0:
                    break
                elif res_email["code"] == 800:
                    return "bad_auth"
                elif res_email["code"] == 50011:
                    time.sleep(random.uniform(10, 60))
                    continue
                else:
                    time.sleep(45)

            time.sleep(random.uniform(15, 20))

            for i in range(3):
                mail_code = get_code(self.mail, self.mail_pass, self.imap)
                if mail_code == 0:
                    time.sleep(random.uniform(60 * (i + 1), 120 * (i + 1)))
                elif mail_code == self.last_code:
                    time.sleep(random.uniform(15, 30))
                else:
                    break

            if mail_code and mail_code != self.last_code:
                self.last_code = mail_code
                break

        addressInfoList = []
        for i, address in enumerate(addresses):
            addressInfoList.append({"address": address, "validateName": f"addressInfoList.{i}.address"})

        while True:
            totp = pyotp.TOTP(self.tfa)
            twofa = totp.now()

            url_add = f" https://www.okx.com/v2/asset/withdraw/addressBatch?t={self.get_timestamp()}"
            # payload = {"emailCode": str(mail_code), "totpCode": str(twofa), "_allow": True, "chooseChain": True,
            #            "formGroupIndexes": list(range(len(addresses))), "authFlag": True, "subCurrencyId": sub_id,
            #            "generalType": 2, "targetType": -1, "currencyId": id, "addressInfoList": addressInfoList,
            #            "whiteFlag": 1, "includeAuth": True}
            payload = {'emailCode': str(mail_code),'totpCode':  str(twofa),'_allow': True,'chooseChain': True,
                       'formGroupIndexes': list(range(len(addresses))),'crypto': 'ETH','subCurrencyId': -1,'authFlag': True,
                       'generalType': 2,'targetType': -1,'currencyId': '2','addressInfoList': addressInfoList,'includeAuth': True,'validateOnly': False,}
            res_add = self.helper.fetch_url(url=url_add, type="post", payload=payload, headers=self.get_headers())
            if res_add["code"] != 0:
                if res_add["error_message"]:
                    self.logger.log_error(f'Ошибка добавления в WL: {res_add["error_message"]}')
                if res_add["code"] == 4026:
                    return 'already_added', [wallet['address'].lower() for wallet in res_add['data']]
                elif res_add["code"] == 4011:
                    time.sleep(20)
                elif res_add["code"] == 4081:
                    return "wrong_mail_code"
                elif res_add["code"] == 4083 or res_add["code"] == 4320:
                    return "mail_code_expired"
                elif res_add["code"] == 800:
                    return "bad_auth"
                elif res_add['code'] == 4023:
                    return "wrong_address"
                else:
                    return False
            else:
                return True

    def okx_withdraw(self, address, amount, id, sub_id):

        currency_id_url = f"https://www.okx.com/v2/asset/accounts/networks?t={self.get_timestamp()}"
        payload = {"currencyId": id, "isWithdraw": True, "address": address}
        res = self.helper.fetch_url(url=currency_id_url, type='post', payload=payload, headers=self.get_headers())
        if res["code"] == 0:
            networks = res["data"]["networks"]
            for n in networks:
                if int(n["subCurrencyId"]) == sub_id:
                    can_withdraw = True if n['status'] == True else False
                    valid_address = True if n["validAddress"] == True else False
                    chain_ok = True
                    break
                else:
                    chain_ok = False
        else:
            self.logger.log_error(f"Error while getting withdrawal data: {res['data']['msg']}")
            if res["code"] == 800:
                return "bad_auth", 0, 0, 0
            return "error", 0, 0, 0
        if not chain_ok:
            return "no_chain", 0, 0, 0
        if not can_withdraw:
            return "withdraw_off", 0, 0, 0
        if not valid_address:
            return "not_valid_address", 0, 0, 0

        for i in range(3):
            url_fee = f"https://www.okx.com/v2/asset/withdraw?t={self.get_timestamp()}&currencyId={id}&subCurrencyId={sub_id}&addressId=&isAddress=true&needAmounts=true&invalidAsset=false&useUsdtFee=false&targetType=-1"
            res_fee = self.helper.fetch_url(url=url_fee, type='get', headers=self.get_headers())
            if res_fee["code"] == 0:
                fee = float(res_fee["data"]["feeDefault"])
                balance = float(res_fee["data"]["balance"])
                got_fee = True
                break
            else:
                self.logger.log_error(f"Error while getting withdrawal fee data: {res_fee['data']['msg']}")
                if res_fee["code"] == 800:
                    return "bad_auth", 0, 0, 0
                got_fee = False

        if not got_fee:
            return "no_fee", 0, 0, 0
        if balance < amount + fee:
            return "low_balance", 0, balance, fee

        # FIRST VERIFY
        url_get_fee = f'https://www.okx.com/v2/asset/withdraw/address-verify?t={self.get_timestamp()}&invalidAsset=false&amount={amount}&currencyId={id}&targetType=-1&tag=&subCurrencyId={sub_id}&areaCode=0&address={address}&riskAddressCheck=true&validateAmount=true'
        res = self.helper.fetch_url(url=url_get_fee, type='get', headers=self.get_headers())
        if res["code"] == 0:
            address_id = int(res["data"]["addressId"])
            # need_2fa = res["data"]["need2FA"]
            # need_email = res["data"]["needEmailCode"]
        else:
            if res["code"] == 800:
                return "bad_auth", 0, balance, fee
            if res["code"] == 4039:
                return "not_min", 0, balance, fee
            return res["msg"], 0, balance, fee

        # if need_email and need_2fa:
        #     return "not_wl", 0, balance, fee

        # FIRST WITHDRAW

        url_ = f'https://www.okx.com/v2/asset/withdraw/first-withdraw-address?t={self.get_timestamp()}'
        payload = {"address": address}
        res = self.helper.fetch_url(url=url_, type='post', payload=payload, headers=self.get_headers())
        if res["code"] == 0:
            is_first = res["data"]["isFirst"]
        else:
            if res["code"] == 800:
                return "bad_auth", 0, balance, fee
            return res["msg"], 0, balance, fee

        # SUBMIT
        url_submit = f"https://www.okx.com/v2/asset/withdraw/submit-with-amounts?t={self.get_timestamp()}"
        payload = {"domain": "", "amounts": [{"amount": amount + fee, "target": 6}], "address": address, "invoice": "",
                   "addressId": address_id, "currencyId": id, "subCurrencyId": sub_id, "emailCode": "",
                   "phoneCode": "",
                   "totpCode": "", "targetType": -1, "title": "", "authFlag": False, "fee": fee, "excludeFee": False,
                   "validateAllCode": True, "loanTrans": False, "invalidAsset": False}
        res_submit = self.helper.fetch_url(url=url_submit, type="post", payload=payload, headers=self.get_headers())
        if res_submit["code"] == 0:
            return True, int(res_submit["data"]["id"]), balance, fee
        else:
            self.logger.log_error(f"Withdrawal error: {res_submit['data']['msg']}")
            if res_submit["code"] == 800:
                return "bad_auth", 0, balance, fee

            return res_submit["msg"], 0, balance, fee

    def withdraw(self, address, fee=0):
        withdraw = False
        # formatted_address = "[" + address['address'][:5] + "..." + address['address'][-5:] + "] "
        for i in range(5):
            try:
                withdraw, wd_id, token_balance, fee = self.okx_withdraw(address['address'], address['value'], id=2, sub_id=address['sub_id'])
            except:
                time.sleep(random.uniform(10, 15))
                continue
            if withdraw is True:
                # self.logger.log_success(f"{formatted_address}Requested withdrawal successful: {address['value']} {self.args['token']} (fee {fee} {self.args['token']})")
                break
            elif withdraw == "bad_auth":
                self.logger.log_error("AUTH CODE IS NOT VALID. STOPPED")
                return False, False
            elif withdraw == "withdraw_off":
                self.logger.log_error(f" OKX | Ошибка вывода 'Выводы выключены'!", address['address'])
                return False, False
            elif withdraw == "low_balance":
                self.logger.log_error(f"OKX | Ошибка вывода 'Недостаточно баланса'", address['address'])
                try:
                    balance = self.transfer_all_from_subs()
                except:
                    continue
            elif withdraw == "not_wl":
                self.logger.log_error(f"OKX | Ошибка вывода 'Address is not whitelisted'!", address['address'])
                return False, False
            elif withdraw == "not_min":
                self.logger.log_error(f"OKX | Ошибка вывода 'Value less than minimal'!", address['address'])
                return False, False
            else:
                self.logger.log_error(f"OKX | Ошибка вывода - {withdraw}, жду 30 секунд", address['address'])
                time.sleep(30)

        if withdraw is not True:
            return False, 0

        return True, fee

    def get_deposit_address(self):

        def find_unused_wallet(wallets_data):
            for wallet, data in wallets_data.items():
                if data['status'] == 0:
                    return wallet
            return None
        while True:
            if not self.busy:
                self.busy = True
                break
            else:
                time.sleep(random.uniform(30, 60))
        address = find_unused_wallet(self.wallets)
        if address:
            self.wallets[address]['status'] = 1
            self.busy = False
            return self.wallets[address]['address']
        else:
            accs = self.get_all_accs()
            if not accs:
                return
            if len(accs) == 6:
                for acc in accs:
                    if not acc["masterAccount"]:
                        log = acc["loginId"]
                        sub_wallets_used = sum(1 for data in self.wallets.values() if data.get('sub', False) == log and data.get('status', 0) == 2)
                        if log not in list(self.subs_to_task.keys()) or sub_wallets_used == 20:
                            for i in range(3):
                                delete = self.delete_sub(log)
                                if delete is True:
                                    break
                                elif delete == "has_funds":
                                    withdraw_from_sub = self.transfer_all_from_sub(log)
                                    if withdraw_from_sub == "bad_auth":
                                        return False
                                elif delete == "bad_auth":
                                    return False
                                else:
                                    if "Эта операция была заблокирована" in delete:
                                        time.sleep(120)
                                        continue
                                    break
            while True:
                add, sub_login = self.create_sub()
                if add is True:
                    self.subs_to_task[sub_login] = []
                    break
                elif add == "ip_blocked":
                    time.sleep(60)
                    continue
                elif add == "blocked":
                    time.sleep(60 * 120 + 1)
                elif add == "bad_auth":
                    return False
                elif not add:
                    return False
                else:
                    if "Эта операция была заблокирована" in add:
                        time.sleep(120)
                        continue
                    break
            token_sub = self.switch_acc(sub_login)
            if token_sub:
                if token_sub == "bad_auth":
                    return
                if not token_sub:
                    return
                self.subs_auth[sub_login] = token_sub
                self.auth_ = self.auth
                self.auth = token_sub
                res = self.get_dep_addresses(auth=token_sub)
                if res == "bad_auth":
                    return
                self.auth = self.auth_
                #res = [{r: 0} for r in res]
                self.subs_to_task[sub_login] = res
                for r in res:
                    self.wallets[r] = {"status": 0, "sub": sub_login, "token": token_sub, 'address': r}
        address = find_unused_wallet(self.wallets)
        if address:
            self.wallets[address]['status'] = 1
            self.busy = False
            return self.wallets[address]['address']
        else:
            self.busy = False
            return

    def get_available_deposit_chains(self):
        for i in range(5):
            try:
                res = self.helper.fetch_url(url='https://www.okx.com/v2/asset/accounts/networks?t=1692708917212', type='post', payload={"isWithdraw":False,"currencyId":2}, headers=self.get_headers())
                if int(res['code']) == 0:
                    chains = []
                    for chain in res['data']['networks']:
                        if chain["status"]:
                            chain_name = next((chain_ for chain_, data in self.data.items() if data['sub_id'] == int(chain['subCurrencyId'])), None)
                            if chain_name != None:
                                chains.append(chain_name)
                    return chains
                else:
                    raise Exception
            except Exception:
                time.sleep(i*1)
        return []
    #CREATES SUB WITH RANDOM LOGIN/PASS
        
    def create_sub(self):

        import string, secrets

        def generate_login_password():
            characters = string.ascii_letters + string.digits
            login = ''.join(secrets.choice(characters) for _ in range(14))
            password = ''.join(secrets.choice(characters) for _ in range(15))
            return login, password + "." + random.choice(string.ascii_letters).upper() + random.choice(string.digits)

        totp = pyotp.TOTP(self.tfa)
        while True:
            login, password = generate_login_password()
            #self.logger.log(f"Creating subaccount: {login}")
            twofa = totp.now()
            url = f"https://www.okx.com/v3/users/subaccount/addBatchSubAccount?t={self.get_timestamp()}"
            payload = {"list": [
                {"id": 1, "password": password, "accountType": "1", "settingParam": {}, "subAccountName": login,
                 "tradeLevel": "1", "isAllowRecharge": True}], "unifiedCheckCode": True, "googleCode": twofa}
            res = self.helper.fetch_url(url=url, type='post', payload=payload, headers=self.get_headers())
            if res["code"] != 0:
                if int(res["code"]) == 3944:
                    time.sleep(random.uniform(30, 35))
                    continue
                elif int(res["code"]) == 3113:
                    return "ip_blocked", login
                elif int(res["code"]) == 3114:
                    return "blocked", login
                elif int(res["code"]) == 800:
                    return "bad_auth", login
                elif int(res["code"]) == 3911:
                    time.sleep(10)
                    continue
                elif int(res["code"]) == 3909:
                    time.sleep(91)
                    continue
                return False, login
            else:
                break

        url_make_switchable = f"https://www.okx.com/v3/users/subaccount/toggleSwitchable?t={self.get_timestamp()}"
        payload = {"loginId": login, "turnOn": True}
        res = self.helper.fetch_url(url=url_make_switchable, type='post', payload=payload, headers=self.get_headers())
        if res["code"] != 0:
            if res["code"] == 800:
                return "bad_auth"
            return False

        return True, login
    #DELETES SUB WITH LOGIN
    def delete_sub(self, login):
        totp = pyotp.TOTP(self.tfa)
        url_delete = f"https://www.okx.com/v3/users/subaccount/delete-go?t={self.get_timestamp()}"
        payload = {"subUserId": 0, "subAccountName": login}
        res = self.helper.fetch_url(url=url_delete, type='post', payload=payload, headers=self.get_headers())
        if res["code"] != 0:
            if res["code"] == 800:
                return "bad_auth"
            #print(f"Ошибка удаления саба (1) : {res}")
            return res["msg"]

        while True:
            url_delete = f"https://www.okx.com/v3/users/subaccount/delete?t={self.get_timestamp()}"
            twofa = totp.now()
            payload = {"subUserId": 0, "subAccountName": login, "unifiedCheckCode": True, "googleCode": twofa}
            res = self.helper.fetch_url(url=url_delete, type='post', payload=payload, headers=self.get_headers())
            if res["code"] != 0:
                if res["code"] == 3944:
                    time.sleep(15)
                    continue
                if res["code"] == 3360:
                    return "has_funds"
                if res["code"] == 800:
                    return "bad_auth"
                #print(f"Ошибка удаления саба (2) : {res}")
                return res["msg"]
            else:
                break

        return True

