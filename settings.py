                                        # /// НАСТРОЙКИ ///

settings_dict = {                       #   /////ОБЩИЕ/////
    "max_gwei": 99,                                                  # МАКСИМУМ ГАЗ В ЭФИРЕ ПРИ РАБОТЕ
    "attempts" : 5,                                                  # МАКСИМУМ ПОПЫТОК ПРИ ОШИБКЕ
    "tx_min" : 1,                                                    # МИНИМУМ ДЕЙСТВИЙ
    "tx_max": 1,                                                     # МАКСИМУМ ДЕЙСТВИЙ
    "min_sleep": 10,                                                 # МИНИМУМ СОН МЕЖДУ ДЕЙСТВИЯМИ
    "max_sleep": 20,                                                 # МАКСИМУМ СОН МЕЖДУ ДЕЙСТВИЯМИ
    "max_start_delay": 10,                                           # МАКСИМАЛЬНАЯ ЗАДЕРЖКУ ПЕРЕД СТАРТОМ КОШЕЛЬКА В ПАЧКЕ
    "min_after_gas_delay": 0,                                        # МИНИМАЛЬНАЯ ЗАДЕРЖКА ПОСЛЕ ВЫХОДА ИЗ ЦИКЛА ПРОВЕРКИ ГАЗА (ЧТОБЫ КОШЕЛЬКИ НЕ НАЧИНАЛИ В ОДНУ МИНУТУ)
    "max_after_gas_delay": 100,                                      # МАКСИМАЛЬНАЯ ЗАДЕРЖКА ПОСЛЕ ВЫХОДА ИЗ ЦИКЛА ПРОВЕРКИ ГАЗА (ЧТОБЫ КОШЕЛЬКИ НЕ НАЧИНАЛИ В ОДНУ МИНУТУ)
    "max_batch_wallets": 10,                                         # МАКСИМУМ КОШЕЛЬКОВ ЗА ПАЧКУ (20 МАКСИМУМ)
    "shuffle_wallets": True,                                         # МЕШАТЬ ЛИ КОШЕЛЬКИ
    "min_eth_balance": 0.10,                                         # МИНИМАЛЬНЫЙ БАЛАНС ЭФИРА В LINEA (МЕНЬШЕ - БУДЕТ БРИДЖИТЬ)
    "show_warnings": True,                                           # ВЫВОДИТЬ ЛИ WARNING ЛОГИ
    "requests_proxy": None,                                          # ПРОКСИ ДЛЯ ЗАПРОСОВ (ИНАЧЕ НЕ БУДУТ РАБОТАТЬ KYBERSWAP, ELEMENT, OPENSEA, OPENOCEAN И Т.П)
                                                                     # ЛИБО ВКЛЮЧАЕМ VPN | ФОРМАТ - log:pass@ip:port
                                        #  /////МОСТ/////
    "to_linea_min": 0.03,                                            # МИНИМУМ БРИДЖ В LINEA
    "to_linea_max": 0.05,                                            # МАКСИМУМ БРИДЖ В LINEA
    "min_after_bridge_delay": 0,                                     # МИНИМАЛЬНАЯ ЗАДЕРЖКА ПОСЛЕ БРИДЖА
    "max_after_bridge_delay": 100,                                   # МАКСИМАЛЬНАЯ ЗАДЕРЖКА ПОСЛЕ БРИДЖА
    "black_chains": ['ETH'],                                         # ЧЕЙНЫ С КОТОРЫМИ НЕ РАБОТАЕМ
    "max_bridge_slippage": 5,                                        # МАКСИМАЛЬНЫЙ СПИЛЕДЖ БРИДЖА
    "main_prioritet": True,                                          # ПРИОРИТЕТ НА МЕЙН БРИДЖ (ЕСЛИ ЕСТЬ ЭФИР В ОСНОВНОЙ СЕТИ)
                                        #  /////СВАПЫ/////
    "max_slippage": 20,                                              # МАКСИМАЛЬНЫЙ СЛИПЕДЖ СВАПОВ
    "max_swap_value": 100,                                           # МАКСИМАЛЬНОЕ ВЕЛЬЮ СВАПА В $
    "swap_out_after": True,                                          # СВАПНУТЬ ОБРАТНО ВСЕ ТОКЕНЫ В ETH В КОНЦЕ КРУГА
    "high_volume": True,                                             # ПОВЫШЕННЫЕ ОБЪЁМЫ (ЭКСПЕРЕМЕНТАЛЬНАЯ ФУНКЦИЯ) МЕНЯЕТ АЛГОРИТМ, ПОВЫШАЯ ОБЪЁМЫ СВАПОВ (НЕ ЮЗАТЬ С МЕЛКИМ БАЛАНСОМ!
                                        #   /////НФТ/////
    "max_nft_price": 0.0005,                                         # МАКСИМУМ ЦЕНА НФТ НА МАРКЕТАХ ДЛЯ ПОКУПКИ (В ETH)
    "list_nfts": True,                                               # ЛИСТИТЬ ЛИ НФТ
                                        #  /////ДОМЕНЫ//////
    "multiple_domains": False,                                       # МИНТИТЬ ЛИ ДОМЕН ЕСЛИ УЖЕ ЕСТЬ 1 (РАБОТАЕТ НА ВСЕХ КРОМЕ ZNS.ID)
    "domain_reg_time": 1,                                            # КОЛ-ВО ЛЕТ ДЛЯ МИНТА ДОМЕНА (ЛУЧШЕ НЕ МЕНЯТЬ - ЦЕНА БУДЕТ ДОРОЖЕ)
    "domain_dop_action": True,                                       # ДОП ДЕЙСТВИЕ НА ДОМЕНАХ
                                        #/////ЛИКВИДНОСТЬ/////
    "max_liq_in_usd": 15,                                            # МАКСИМУМ ДОБАВЛЯЕМ В ЛИКВУ В $ (ОДНОГО ТОКЕНА)
    "remove_liq_after": False,                                       # ВЫВОДИТЬ ЛИ ИЗ ВСЕХ ПУЛОВ В КОНЦЕ КРУГА
                                        #  /////ЛЕНДИНГИ/////
    "lendings_max_value": 50,                                        # МАКСИМАЛЬНО ИСПОЛЬЗУЕМОЕ ВЕЛЬЮ ДЛЯ ЛЕНДИНГОВ (В $)
    "remove_lendings_afrer": False,                                  # УБИРАТЬ ЛИ ИЗ ЛЕНДИНГОВ В КОНЦЕ КРУГА

                                        # ///// ETH ПРОГРЕВ /////
    "warmup": True,                                                  # ДЕЛАТЬ ЛИ ПРОГРЕВ ТРАНЗЫ В ДРУГИХ ЧЕЙНАХ
    "min_warmup_tx": 1,                                              # МИН ТРАНЗ ПРОГРЕВА
    "max_warmup_tx": 2,                                              # МАКС ТРАНЗ ПРОГРЕВА
    "warmup_before_dep": True,                                       # ДЕЛАТЬ ТРАНЗЫ ДО ДЕПА В LINEA
    "warmup_before_withdraw": True,                                  # ДЕЛАТЬ ТРАНЗЫ ДО ВЫВОДА НА ОКЕКС

                                        # ///// OKX /////
    "okx": True,                                                     # ВКЛЮЧИТЬ РАБОТУ С OKX (ЕСЛИ ВКЛЮЧИЛИ - БУДЕТ ВЫВОДИТЬ В ЛЮБОЙ ЧЕЙН ЭФИР - ЗАТЕМ НА УНИКАЛЬНЫЙ НОВЫЙ АДРЕС НА OKX)
    "ignore_main_bridge_withdraw": True,                             # ИГНОРИТЬ МЕЙН БРИДЖ ПРИ ВЫВОДЕ
    "use_only_okx_to_dep": False,                                    # ИСПОЛЬЗОВАТЬ ЛИ ТОЛЬКО (!) OKX ДЛЯ ПОПОЛНЕНИЯ LINEA
    "use_only_okx_to_wd": False,                                     # ИСПОЛЬЗОВАТЬ ЛИ ТОЛЬКО (!) OKX ДЛЯ ВЫВОДА ИЗ LINEA
    "okx_min_percent_wd": 99,                                        # МИНИМУМ В % ВЫВОДИТЬ ИЗ LINEA
    "okx_max_percent_wd": 99,                                        # МАКСИМУМ В % ВЫВОДИТЬ ИЗ LINEA
    "okx_auth": '',                                                  # OKX AUTH
    "okx_devid": '',                                                 # OKX DEVID
    "okx_2fa": '',                                                   # OKX 2FA SECRET CODE
    "okx_mail": '',                                                  # OKX ПОЧТА ОТ АККАУНТА (НУЖНО ВКЛЮЧИТЬ IMAP)
    "okx_mail_pass": '',                                             # OKX ПАРОЛЬ ОТ ПОЧТЫ
    "okx_imap": '',                                                  # IMAP АДРЕС ПОЧТЫ ОТ OKX

    "linea_voyage_work": False,                                     # ВКЛЮЧИТЬ ЛИ МОДУЛЬ VOYAGE
    "min_usd_to_otc": 13,                                           # МАКСИМУМ КИДАТЬ В OTC
    "max_usd_to_otc": 14,                                           # МИНИМУМ КИДАТЬ В OTC
    "voyage_other_actions": False,                                  # ДЕЙСТВИЯ ИЗ OTHER (ДЛЯ РАЗБАВКИ)
    "min_other": 1,                                                 # МИНИМУМ ДОП ТРАНЗ
    "max_other": 1,                                                 # МАКСИМУМ ДОП ТРАНЗ

    "voyage_poh": False,                                             # ВКЛЮЧИТЬ ЛИ МОДУЛЬ VOYAGE POH
    "voyage_poh_openid": False,                                      # ВКЛЮЧИТЬ ЛИ POH OPENID
    "voyage_poh_trusta_human": False,                               # ВКЛЮЧИТЬ ЛИ POH TRUSTA HUMAN
    "voyage_poh_trusta_media": False,                               # ВКЛЮЧИТЬ ЛИ POH TRUSTA MEDIA
}




                                        # ///// RPC НАСТРОЙКИ /////
w3_dict = {
    "ETH": "https://rpc.ankr.com/eth",
    "LINEA": "https://rpc.ankr.com/linea",
    "ARB": "https://rpc.ankr.com/arbitrum",
    "OPT": "https://rpc.ankr.com/optimism"
}
                                        # ///// МОДУЛИ СВАПОВ /////
swaps_dict = {
    "Syncswap": True,                                                        # SYNCSWAP   | syncswap.xyz
    "Lynex": True,                                                           # LYNEX      | lynex.fi
    "Echodex": True,                                                         # ECHODEX    | echodex.io
    "Horizon": True,                                                         # HORIZON    | horizondex.io
    "Vooi": True,                                                            # VOOI       | vooi.io
    "Izumi": True,                                                           # IZUMI      | izumi.finance
    "Pancake": True,                                                         # PANCAKE    | pancakeswap.finance
    "Velocore": True,                                                        # VELOCORE   | velocore.xyz
    "Woofi": True,                                                           # WOOFI      | fi.woo.org
    'Sushiswap': True,                                                       # SUSHISWAP  | sushi.com
    'Symbiosis': True,                                                       # SYMBIOSIS  | app.symbiosis.finance
    "Spaceswap": False,                                                      # SPACESWAP  | spaceswap.tech
    "Dodoex": True,                                                          # DODOEX     | dodoex.io
    "Wowmax": True,                                                          # WOWMAX     | wowmax.exchange
    "Openocean": True,                                                       # OPENOCEAN  | openocean.finance
    "Okx": True,                                                             # OKX        | okx.com/web3/dex
    "Kyberswap": True,                                                       # KYBERSWAP  | kyberswap.com
    "Xyfinance": True,                                                       # XYFINANCE  | app.xy.finance
    "Metamask": True,                                                        # METAMASK   | https://portfolio.metamask.io/swap
}
                                        # ///// МОДУЛИ ЛИКВИДНОСТИ /////
liqs_dict = {
    "Velocore_liq": True,                                                    # VELOCORE   | linea.velocore.xyz
    "Lynex_liq": True,                                                       # LYNEX      | app.lynex.fi
    "Horizon_liq": True,                                                     # HORIZON    | horizondex.io
    "Echodex_liq": True,                                                     # ECHODEX    | echodex.io
    "Vooi_liq": True,                                                        # VOOI       | vooi.io
    "Syncswap_liq": True,                                                    # SYNCSWAP   | syncswap.xyz
    "XyfinanceVoayge": True,                                                 # XYFINANCE  | VOAYGE 5 WAWE
    "VelocoreVoayge": True,                                                  # VELOCORE   | VOAYGE 5 WAWE
}
                                        # ///// МОДУЛИ ЛЕНДИНГОВ /////
lendings_dict = {
    "Layerbank": True,                                                       #  LAYERBANK  | layerbank.finance
    "Mendi": True,                                                           #  MENDI      | mendi.finance
}
                                        # ///// МОДУЛИ НФТ МАРКЕТОВ /////
nft_markets_dict = {
    "Element": True,                                                         #  ELEMENT    | element.market
    'Alienswap': True,                                                       #  ALIENSWAP  | alienswap.xyz
    'Zonic': True,                                                           #  ZONIC      | zonic.app
}

                                        # ///// МОДУЛИ ДОМЕННЫХ СЕРВИСОВ /////
name_services_dict = {
    "Openname" : True,                                                       #  OPENNAME   | app.open.name
    'Lineans': True,                                                         #  LINEANS    | app.lineans.domains
    'Lin': True,                                                             #  LIN        | lin.domains
}
                                        # ///// МОДУЛИ МОСТОВ /////
bridges_dict = {
    "Main" : True,                                                           #  MAIN       | bridge.base.org
    "Orbiter" : True,                                                        #  ORBITER    | orbiter.finance
    "Symbiosis": True,                                                       #  SYMBIOSIS  | app.symbiosis.finance
    "Xyfinance": True,                                                       #  XYFINANCE  | app.xy.finance
    "Lifi": True,                                                            #  LIFI       | li.fi
    "Omnibtc": True,                                                         #  OMNIBTC    | app.omnibtc.finance
    "Layerswap": True,                                                       #  LAYERSWAP  | layerswap.io
    "Metamask": True,                                                        #  METAMASK   | https://portfolio.metamask.io/bridge
    "Rhino": True,
}
                                        # ///// МОДУЛИ РАЗНЫЕ /////
misc_dict = {
    "Bilinear": True,                                                         #  BILINEAR    | bilinear.io
    "Nfts2me": True,                                                          #  NFTS2ME     | nfts2me.com
    "Mirror": True,                                                           #  MIRROR      | mirror.xyz
    "Omnisea": True,                                                          #  OMNISEA     | omnisea.org
    "Dmail": True,                                                            #  DMAIL       | dmail.ai
    "Backer_nft": False,                                                      #  BACKER      | НЕ АКТУАЛЬНО
    "Gnosis": True,                                                           #  GNOSIS      | safe.linea.build
    "AlienMint": True,                                                        #  ALIENTMINT  | alienswap.xyz/mint
    "ElementMint": True,                                                      #  ELEMENTMINT | element.market/rankinglist/mints
    "Tatarot": True,                                                          #  TATAROT     | tatarot.ai
    "RandomTransfer": True,                                                   #  TRANSFER    | NO LINK
    "RandomApprove": True,                                                    #  APPROVE     | NO LINK
}


                            # ///// МОДУЛИ ПРОГРЕВА ОСНОВНЫХ СЕТЕЙ /////

#ДЛЯ ВЫКЛЮЧЕНИЕ - ПРОСТО УБЕРИ НЕНУЖНЫЙ МОДУЛЬ ИЗ СПИСКА ДЛЯ НУЖНОЙ СЕТИ
#ДЛЯ ВКЛЮЧЕНИЯ - ДОБАВЬ ОБРАТНО

warmup_modules = {
    'ETH': [ # ВСЕ ВОЗМОЖНЫЕ - MINTFUN | LIDO | OPTIMISM | ARBITRUM | POLYGON | AAVE | APPROVE | UNISWAP | SUSHISWAP | ZORA | WRAPPER | BLUR | MIRROR | STARKNET | OKXNFT | TOFUNFT | ELEMENTNFT | RADIANT | OPENSEANFT

        'MINTFUN', # МИНТ СЛУЧАЙНОЙ ФРИШНОЙ НФТ ИЗ ТЕКУЩИЙ ФРИМИНТОВ
        'LIDO', # ДЕПОЗИТ НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'OPTIMISM', # ОФФ МОСТ В ОПТИМИЗМ
        'ARBITRUM', # ОФФ МОСТ В АРБИТРУМ ИЛИ НОВУ
        'POLYGON', # ОФФ МОСТ В ПОЛИГОН
        'AAVE', # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'APPROVE', # АПРУВ СЛУЧАЙНОГО ТОКЕНА ДЛЯ SUSHI, CURVE, 1INCH ИЛИ UNISWAP
        'UNISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        '1INCH',  # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'SUSHISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'WRAPPER', # ВРАП / АНВАР НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'ZORA', # ОФФ МОСТ В ЗОРУ
        'STARKNET', # ОФФ МОСТ В СТАРК (СЛУЧАЙНЫЙ АДРЕС)
        'BLUR', # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'MIRROR', # МИНТ СЛУЧАЙНОЙ ФРИШНОЙ СТАТЬИ (КОМ-СА ПРОТОКОЛА 0.00069 ETH)
        'RADIANT', # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'OKXNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'TOFUNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'ELEMENTNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'OPENSEANFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
    ],
    'OPT': [ # ВСЕ ВОЗМОЖНЫЕ - MINTFUN | MINTFUN | APPROVE | UNISWAP | SUSHISWAP | WRAPPER | MIRROR | OPTIMISM | OKXNFT | OPENSEANFT

        'MINTFUN', # МИНТ СЛУЧАЙНОЙ ФРИШНОЙ НФТ ИЗ ТЕКУЩИЙ ФРИМИНТОВ
        'AAVE',  # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'APPROVE', # АПРУВ СЛУЧАЙНОГО ТОКЕНА ДЛЯ SUSHI, CURVE, 1INCH ИЛИ UNISWAP
        'UNISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        '1INCH',  # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'SUSHISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'WRAPPER', # ВРАП / АНВАР НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'MIRROR', # МИНТ СЛУЧАЙНОЙ ФРИШНОЙ СТАТЬИ (КОМ-СА ПРОТОКОЛА 0.00069 ETH)
        'OPTIMISM', # ОФФ МОСТ ИЗ ОПТИМИЗМ В ЭФИР
        'OKXNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'OPENSEANFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
    ],
    'ARB': [  # ВСЕ ВОЗМОЖНЫЕ - ARBITRUM | AAVE | APPROVE | UNISWAP | SUSHISWAP | WRAPPER | RADIANT | OKXNFT | TOFUNFT | ELEMENTNFT | OPENSEANFT

        'ARBITRUM', # ОФФ МОСТ ИЗ АРБИТРУМА В ЭФИР
        'AAVE',  # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'APPROVE', # АПРУВ СЛУЧАЙНОГО ТОКЕНА ДЛЯ SUSHI, CURVE, 1INCH ИЛИ UNISWAP
        'UNISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        '1INCH', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'SUSHISWAP', # ПОКУПКА СЛУЧАЙНОГО ТОКЕНА НА НЕБОЛЬШОЕ КОЛ-ВО ЭФИРА
        'WRAPPER', # ВРАП / АНВАР НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'RADIANT', # ДЕПОЗИТ / ВЫВОД НЕБОЛЬШОГО КОЛ-ВА ЭФИРА
        'OKXNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'TOFUNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'ELEMENTNFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
        'OPENSEANFT', # ПОКУПКА СЛУЧАЙНО NFT ОТ 0.00001 ДО 0.0001 ETH (ДО 18 ЦЕНТОВ)
    ],
}