import concurrent.futures
from settings import settings
from helper import Helper
from voyager import Voyager
from logger import Logger
from web3.auto import w3
import pandas as pd

def start(wallets_array):

    logger = Logger()
    helper = Helper()
    voyager = Voyager(settings, logger, helper, w3)

    wallets_data = []

    for wallet in wallets_array:
        parts = wallet.split(';')

        p_key = None
        proxy = None
        twitter_auth_token = None

        if len(parts) >= 1:
            p_key = parts[0]
        if len(parts) >= 2:
            proxy = parts[1]
        if len(parts) >= 3:
            twitter_auth_token = parts[2]

        wallets_data.append({
            "address": w3.eth.account.from_key(p_key).address if p_key else None,
            "private_key": p_key,
            "proxy": proxy,
            "twitter_auth_token": twitter_auth_token,
        })

    logger.log('Начинаю работу...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(50, settings['max_batch_wallets'])) as executor:
        results = list(executor.map(voyager.main, wallets_data))

    wallets = []
    total_xp_list = []
    streak_list = []
    week_xp_lists = [[] for _ in range(9)]

    for result in results:
        if isinstance(result, dict):
            wallets.append(result['wallet'])
            total_xp_list.append(result['total_xp'])
            streak_list.append(result['streak'])

            quests_data = result['quests_data']
            for week_col in range(9):
                week_str = f'week_{week_col}'
                xp_value = next((item['xp'] for item in quests_data if item['week'] == week_str), None)
                week_xp_lists[week_col].append(xp_value)

    data = {'wallet': wallets, 'total_xp': total_xp_list, 'streak': streak_list}
    for week_col in range(9):
        data[f'week_{week_col}'] = week_xp_lists[week_col]

    df = pd.DataFrame(data)
    with pd.ExcelWriter('output_voyager.xlsx', engine='openpyxl') as excel_writer:
        df.to_excel(excel_writer, sheet_name='Sheet1', index=False)

with open("wallets.txt", "r") as f:
    wallets = [row.strip() for row in f]

start(wallets)