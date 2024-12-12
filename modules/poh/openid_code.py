import asyncio, json
from playwright.async_api import async_playwright

async def new_session(playwright, account_data, proxy=None, headless=False):

    if not proxy:
        browser = await playwright.chromium.launch(headless=headless)
    else:
        proxy_1, proxy_2 = proxy.split("@")
        p_log, p_pass = proxy_1.split(":")
        p_ip, p_port = proxy_2.split(":")
        browser = await playwright.chromium.launch(channel="chrome", headless=headless, proxy={"server": f"http://{p_ip}:{p_port}","username": p_log, "password": p_pass})

    account_data = json.loads(account_data)
    cookies = account_data['session']['cookies']
    user_agent = account_data['useragent']

    context = await browser.new_context(user_agent=user_agent)

    for cookie in cookies:
        if cookie.get('sameSite') == 'no_restriction':
            cookie['sameSite'] = 'None'

    await context.add_cookies(cookies)

    page = await context.new_page()

    await page.goto('https://auth.openid3.xyz/', timeout=180000)

    async def inject_wallet_connet():

        await page.evaluate("""
            localStorage.setItem('-walletlink:https://www.walletlink.org:version', '3.7.2');
            localStorage.setItem('-walletlink:https://www.walletlink.org:session:linked', '0');
            localStorage.setItem('rk-latest-id', 'walletConnect');
            localStorage.setItem('wagmi.store', '{"state":{"data":{"account":"0xe79Cf0ccA5111a763abf5870bCd0F0bBE2cEC566","chain":{"id":59144,"unsupported":false}},"chains":[{"id":59144,"name":"Linea Mainnet","network":"linea-mainnet","nativeCurrency":{"name":"Linea Ether","symbol":"ETH","decimals":18},"rpcUrls":{"infura":{"http":["https://linea-mainnet.infura.io/v3"],"webSocket":["wss://linea-mainnet.infura.io/ws/v3"]},"default":{"http":["https://rpc.linea.build"],"webSocket":["wss://rpc.linea.build"]},"public":{"http":["https://rpc.linea.build"],"webSocket":["wss://rpc.linea.build"]}},"blockExplorers":{"default":{"name":"Etherscan","url":"https://lineascan.build"},"etherscan":{"name":"Etherscan","url":"https://lineascan.build"},"blockscout":{"name":"Blockscout","url":"https://explorer.linea.build"}},"contracts":{"multicall3":{"address":"0xcA11bde05977b3631167028862bE2a173976CA11","blockCreated":42}},"testnet":false}]},"version":2}');
            localStorage.setItem('-walletlink:https://www.walletlink.org:session:id', '451e6772fde38feb9c656515d001cbb7');
            localStorage.setItem('-walletlink:https://www.walletlink.org:session:secret', '6899ab4dd52bde284063cbaf99f60dca839194a3eb8ca655f06222b342a69deb');
            localStorage.setItem('WCM_VERSION', '2.6.2');
            localStorage.setItem('wagmi.cache', '{"buster":"","timestamp":1702136796074,"clientState":{"mutations":[],"queries":[{"state":{"dataUpdateCount":0,"dataUpdatedAt":0,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"loading","fetchStatus":"idle"},"queryKey":[{"entity":"ensName","chainId":59144}],"queryHash":"[{\"chainId\":59144,\"entity\":\"ensName\"}]"},{"state":{"dataUpdateCount":0,"dataUpdatedAt":0,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"loading","fetchStatus":"idle"},"queryKey":[{"entity":"ensAvatar","chainId":59144}],"queryHash":"[{\"chainId\":59144,\"entity\":\"ensAvatar\"}]"},{"state":{"dataUpdateCount":0,"dataUpdatedAt":0,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"loading","fetchStatus":"idle"},"queryKey":[{"entity":"balance","chainId":59144}],"queryHash":"[{\"chainId\":59144,\"entity\":\"balance\"}]"},{"state":{"dataUpdateCount":0,"dataUpdatedAt":0,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"loading","fetchStatus":"idle"},"queryKey":[{"entity":"waitForTransaction","chainId":59144}],"queryHash":"[{\"chainId\":59144,\"entity\":\"waitForTransaction\"}]"},{"state":{"dataUpdateCount":0,"dataUpdatedAt":0,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"loading","fetchStatus":"idle"},"queryKey":[{"entity":"ensName","address":"0xe79Cf0ccA5111a763abf5870bCd0F0bBE2cEC566","chainId":59144}],"queryHash":"[{\"address\":\"0xe79Cf0ccA5111a763abf5870bCd0F0bBE2cEC566\",\"chainId\":59144,\"entity\":\"ensName\"}]"},{"state":{"data":{"decimals":18,"formatted":"0","symbol":"ETH","value":"#bigint.0"},"dataUpdateCount":2,"dataUpdatedAt":1702136795232,"error":null,"errorUpdateCount":0,"errorUpdatedAt":0,"fetchFailureCount":0,"fetchFailureReason":null,"fetchMeta":null,"isInvalidated":false,"status":"success","fetchStatus":"idle"},"queryKey":[{"entity":"balance","address":"0xe79Cf0ccA5111a763abf5870bCd0F0bBE2cEC566","chainId":59144}],"queryHash":"[{\"address\":\"0xe79Cf0ccA5111a763abf5870bCd0F0bBE2cEC566\",\"chainId\":59144,\"entity\":\"balance\"}]"}]}}');
            localStorage.setItem('wagmi.requestedChains', '[59144]');
            localStorage.setItem('wagmi.connected', 'true');
            localStorage.setItem('rk-recent', '["walletConnect"]');
            localStorage.setItem('wagmi.wallet', '"walletConnect"');
            localStorage.setItem('rk-version', '1.3.0');
        """)
        await page.reload(timeout=180000)

    await inject_wallet_connet()
    await page.wait_for_load_state()
    await asyncio.sleep(5)

    code_wait = asyncio.Future()

    async def on_console(msg):
        if 'code' in str(msg):
            code = str(msg).split('code: ')[1].split(',')[0]
            code_wait.set_result(code)

    async def get_tab(browser, tab_url):
        while True:
            for tab in browser.contexts[0].pages:
                if tab_url in tab.url:
                    return tab
            await asyncio.sleep(2)

    for i in range(5):
        try:
            await page.locator('button').get_by_text('Google').click()
            break
        except:
            await inject_wallet_connet()
    await asyncio.sleep(3)

    gmail_tab = await get_tab(browser, 'accounts.google')

    found = False
    page.on('console', on_console)
    await asyncio.sleep(5)

    for i in range(10):
        if gmail_tab in browser.contexts[0].pages and await gmail_tab.locator('ul li div[role=link]').count() > 0:
            try:
                await asyncio.sleep(5)
                if 'signin/oauth/id?authuser' in gmail_tab.url:
                    print('continue text?')
                    await page.locator('button').get_by_text('Continue').click()
                    await asyncio.sleep(5)
                await gmail_tab.locator('ul li div[role=link]').first.click()
                found = True
                break
            except Exception:
                break
        else:
            await asyncio.sleep(5)

        if gmail_tab in browser.contexts[0].pages:
            if 'recaptcha' in gmail_tab.url:
                print('gmail captcha')
                found = False

            if 'signin/oauth/id?authuser' in gmail_tab.url:
                print('continue text?')
                await page.locator('button').get_by_text('Continue').click()
                await asyncio.sleep(5)

            if 'confirmidentifier' in gmail_tab.url:
                print('gmail verify')
                await gmail_tab.locator('div[role=presentation] button').click()
                await asyncio.sleep(5)

            if 'deniedsigninrejected' in gmail_tab.url or 'info/unknownerror' in gmail_tab.url:
                print('gmail deny, try again')
                await gmail_tab.locator('div#next button').click()
                await asyncio.sleep(5)

            if 'signin/rejected' in gmail_tab.url:
                print('gmail deny, try again')
                await gmail_tab.locator('div#next a').click()
                await asyncio.sleep(5)

            await asyncio.sleep(2)

    if found:
         code = await code_wait
    else:
        code = None

    await page.close()
    await browser.close()
    return code

async def get_gmail_code(account_data, proxy=None):
    async with async_playwright() as playwright:
        try:
            code = await new_session(playwright, account_data=account_data, proxy=proxy)
            return code
        except Exception as e:
            print(f"GET CODE EXP: {e}")
            return


if __name__ == "__main__":
    account_data = {"session":{"cookies":[{"domain":".google.com","name":"SNID","path":"/verify","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"AP5Nx0X7VFqxMdpTnMzd2V1fv3se4FAkTA7QsFlcnONxan7ZREY7fDjZWOj1tvFyxJVx6iXQb7g6Rv0ZmNgXHPJtZdfq","id":4,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":96,"priority":"Medium","session":False},{"domain":"www.google.com","name":"DV","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"Y4vWzQ8PC-wssH4dFRGdR1c-3ijliBgZWqaFSPtATwIAAAA","id":83,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":49,"priority":"Medium","session":False},{"domain":".google.com","name":"OGPC","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"19037049-1:","id":178,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":15,"priority":"Medium","session":False},{"domain":"ogs.google.com","name":"OTZ","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"7287527_28_28__28_","id":179,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"OTZ","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"7287527_28_28__28_","id":180,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":".google.com","name":"SID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmPPLlJFzejcfsrCRY3BLLiA.","id":181,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":74,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-1PSID","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmGiZQHLlAMUk71-fgMhs0yg.","id":182,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":85,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-3PSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmh0uH9xoLWVRHbS1k6ZokHw.","id":183,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":85,"priority":"Medium","session":False},{"domain":".google.com","name":"HSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"ANc0cgiHslRHtvWWJ","id":184,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":".google.com","name":"SSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"ALJmEYLDMyZbtO-8R","id":185,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":".google.com","name":"APISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"GUL0Oy80zRmaCu-H/ADd74PFtCHi0hk_uU","id":186,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":40,"priority":"Medium","session":False},{"domain":".google.com","name":"SAPISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":187,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":41,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-1PAPISID","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":188,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":51,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-3PAPISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":189,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":51,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"ACCOUNT_CHOOSER","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"AFx_qI5anCtAxwn-IwZfu6JK3thJ5cjLhoo6F--dvsEhLW4fk_hukDT8kDLGwoFxPqWaPjxCjo4Ddq7Ng21C9DCMFquemgyafQ7qmoTyB6n8VnqKNcFKVcw","id":190,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":134,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"__Host-GAPS","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1:7kIKA4l9ENGkpWdlH_qMggT-ZfTCFyX0tWFBEt-WpLn2oAGC20BLWc1gp4RhTA4eyuBhUVKYaPzpFHhifOWoLkfZu7SV7g:7aLdK-gBtywjfJWx","id":191,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":124,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"LSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"s.TH:cwgYZcrPGlojWAj0zFkXHjYpsBaksuSKh_i4K88_m-HjaR1uM5IRDR9znJSeI62gktV5BQ.","id":192,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":80,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"__Host-1PLSID","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"s.TH:cwgYZcrPGlojWAj0zFkXHjYpsBaksuSKh_i4K88_m-HjaR1uhEN3lzt1P2JKdt1Bp23uNA.","id":193,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":89,"priority":"Medium","session":False},{"domain":"accounts.google.com","name":"__Host-3PLSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"s.TH:cwgYZcrPGlojWAj0zFkXHjYpsBaksuSKh_i4K88_m-HjaR1uLC8x96OBOuYbBb5V-gdAZg.","id":194,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":89,"priority":"Medium","session":False},{"domain":".google.co.th","name":"SID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmPPLlJFzejcfsrCRY3BLLiA.","id":195,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":74,"priority":"Medium","session":False},{"domain":".google.co.th","name":"__Secure-1PSID","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmGiZQHLlAMUk71-fgMhs0yg.","id":196,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":85,"priority":"Medium","session":False},{"domain":".google.co.th","name":"__Secure-3PSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"cwgYZUdGbqKGpbt3IgXydtv_AMt18y4ul4GzUu61JP_72FAmh0uH9xoLWVRHbS1k6ZokHw.","id":197,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":85,"priority":"Medium","session":False},{"domain":".google.co.th","name":"HSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"AxpJaA5erAxuz8LdN","id":198,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":".google.co.th","name":"SSID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"AVZkR4Ibihu2xO0SR","id":199,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":21,"priority":"Medium","session":False},{"domain":".google.co.th","name":"APISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"GUL0Oy80zRmaCu-H/ADd74PFtCHi0hk_uU","id":200,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":40,"priority":"Medium","session":False},{"domain":".google.co.th","name":"SAPISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":201,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":41,"priority":"Medium","session":False},{"domain":".google.co.th","name":"__Secure-1PAPISID","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":202,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":51,"priority":"Medium","session":False},{"domain":".google.co.th","name":"__Secure-3PAPISID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"1smwcAkz6-hDuidD/A4lqNe5Bkp3Ya3Mf2","id":203,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":51,"priority":"Medium","session":False},{"domain":".google.co.th","name":"NID","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"511=AN_rQUXf8ke4IXJz6TQlfzn6z5ceQT6emEasAI5-BvKNCBB7TI8r8sUlF_HPXgLmYCHaErcpz41uwvBVTeKI2amtZxGf__QdFMgx3oLqCgsZA0PbSYtYEvR28HGsp6kYMvZqSDphHaS2DkrwZROeuSnLxlm_VVFsxsr5-R6XsEs","id":204,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":178,"priority":"Medium","session":False},{"domain":".google.com","name":"SEARCH_SAMESITE","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"CgQI1pkB","id":205,"sameSite":"no_restriction","expires":-1,"httpOnly":True,"size":23,"priority":"Medium","session":False},{"domain":".google.com","name":"1P_JAR","path":"/","sameParty":False,"sameSite":"no_restriction","secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"2023-11-18-10","id":206,"expires":1702895353,"httpOnly":True,"size":19,"priority":"Medium","session":False},{"domain":".google.com","name":"AEC","path":"/","sameParty":False,"sameSite":"no_restriction","secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"Ackid1QEPrcI75j-_2J3eARZPBXosbN35MiTGOKonf9qGq_GPmzSCATeCaA","id":207,"expires":1701566822,"httpOnly":True,"size":62,"priority":"Medium","session":False},{"domain":".google.com","name":"NID","path":"/","sameParty":False,"sameSite":"no_restriction","secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"511=REtpiHh2lehz-4qf8Ykhk_VdAnrdcLDdJIUv3duV-Q37Q2nvvxOiDNfdefg__AoIFUYAlDxoAulLNVWdH0hqP7c2uCbKQS3x-g34HCtHa_OAoUaJZsEspFkK-EOfo4DYwJXtjK4M9Eo377XY3GKvomCUNtEwSyDiAvq-SoZ6QqZ4B8SfzQpJeR-jEtdsjj7qDDngPHWuCs5kAE84vQaZku-XCCzV07NH_RwJwcE-8PwFwSkwiA","id":208,"expires":1715366817,"httpOnly":True,"size":249,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-1PSIDTS","path":"/","sameParty":True,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"sidts-CjIBNiGH7oy3pE3y4bpEtN43O4897dRqGYEWgMr7lrnSM_yup4YdQK77bsFarONyeeyqhBAA","id":209,"sameSite":"no_restriction","expires":1731839352,"httpOnly":True,"size":94,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-3PSIDTS","path":"/","sameParty":False,"sameSite":"no_restriction","secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"sidts-CjIBNiGH7oy3pE3y4bpEtN43O4897dRqGYEWgMr7lrnSM_yup4YdQK77bsFarONyeeyqhBAA","id":210,"expires":1731839352,"httpOnly":True,"size":94,"priority":"Medium","session":False},{"domain":".google.com","name":"SIDCC","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"ACA-OxNHYsdDVCm6EtIFEFSnhFcj2eH0HsyRk8dBOTEuVOX3nqj7bPVup9Jom1llKvCDZQdu4w","id":211,"sameSite":"no_restriction","expires":1731839352,"httpOnly":True,"size":79,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-1PSIDCC","path":"/","sameParty":False,"secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"ACA-OxO1718Pyb7UOBnQiObreYwEmPNbkKKvTlu7L4wt18pInjb_D4666T6B7XxDtfDTGEii","id":212,"sameSite":"no_restriction","expires":1731839352,"httpOnly":True,"size":88,"priority":"Medium","session":False},{"domain":".google.com","name":"__Secure-3PSIDCC","path":"/","sameParty":False,"sameSite":"no_restriction","secure":True,"sourcePort":443,"sourceScheme":"Secure","value":"ACA-OxMbPKe8LBcUP3fipOxk2vhplLfvHjE753RPJnIsEcVCdlg2zJhsnS8hlPuFdCbEv0yX","id":213,"expires":1731839352,"httpOnly":True,"size":88,"priority":"Medium","session":False}]},"account":"edithjolicoeur9@gmail.com:wi61hODUBoxOX:radiotelemetilated@yandex.ru","country":"+66Thailand (+66)","useragent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
    account_data = json.dumps(account_data)
    for i in range(500):
        code = asyncio.run(get_gmail_code(account_data))
        print(code)
