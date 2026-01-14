# 這是用來從永豐的網站下載所有的 ticks。為的是模擬每天放空的真實情況
import sys
import datetime
import time
import shioaji as sj
from shioaji import contracts
from shioaji import constant
import json
import requests
import os
import platform
import queue
import threading
import configparser
import gzip
from datetime import timedelta, date
import pandas as pd
import platform
from mypylib import get_all_stock_code_name_dict
from time import sleep
from pathlib import Path

from mypylib.keys import SHIOAJI_API_KEY, SHIOAJI_SECRET_KEY

list_all_symbol = get_all_stock_code_name_dict()
print(list_all_symbol)

dir_basepath = '../shioaji_ticks'
start_date = date(2022, 1, 1)
end_date = datetime.datetime.today().date()
security_type_downloaded = 0


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def contracts_cb(security_type):
    global security_type_downloaded
    security_type_downloaded += 1
    print(f"{repr(security_type)} fetch done.")


def login(api_key=SHIOAJI_API_KEY,
          secret_key=SHIOAJI_SECRET_KEY,
          ca_path="certificate/SinopacKen.pfx",
          ca_password='H121933940',
          person_id='H121933940'):
    api = sj.Shioaji()
    api.login(api_key, secret_key, contracts_cb=contracts_cb)
    while True:
        if security_type_downloaded != 4:
            sleep(1)
            continue
        break
    return api


def do_redownload(api, dir_basepath, symbol, date_str):
    print(f'Re-downlaod {symbol} on {date_str}')
    ticks = api.ticks(api.Contracts.Stocks[symbol], date_str)
    df = pd.DataFrame({**ticks})
    # print(df)
    df.ts = pd.to_datetime(df.ts)
    df.to_csv(f'{dir_basepath}/{symbol}/{date_str}.csv', mode='w+')


def recheck_all_ticks(dir_basepath):
    dirs = os.listdir(dir_basepath)
    dirs.sort()
    for _dir in dirs:
        if _dir.startswith('.'):
            continue
        if _dir == 'cache':
            continue
        if not os.path.isdir(f'{dir_basepath}/{_dir}'):
            continue
        # if _dir < '3171':
        #     continue
        print(_dir)

        files = os.listdir(f'{dir_basepath}/{_dir}')
        files.sort()
        for file in files:
            if not file.endswith('csv'):
                continue
            file_full_path = f'{dir_basepath}/{_dir}/{file}'
            # print(file_full_path)
            try:
                df = pd.read_csv(file_full_path, low_memory=False)
            except Exception as e:
                print(f'{file_full_path} {e}')
                do_redownload(api, dir_basepath, _dir, file.split('.')[0])
                continue

            ret = df[df['ts'] == 'ts']
            if ret.empty:
                continue

            # Data duplicated
            if (df.shape[0] - 1) / 2 == ret.index[0]:
                upper = df.iloc[:ret.index[0], 1:]
                lower = df.iloc[ret.index[0] + 1:, 1:]
                lower.index = range(0, lower.shape[0])

                if upper.equals(lower):
                    print(f'{_dir} {file} data duplicated')
                    df = pd.DataFrame({**upper})
                    if os.path.exists(file_full_path):
                        os.remove(file_full_path)
                    df.to_csv(file_full_path, mode='w+')

                continue
            else:
                do_redownload(api, dir_basepath, _dir, file.split('.')[0])
                sleep(1)


if __name__ == '__main__':

    # Ken
    if True:
        api = login()
    else:
        # William
        api = login(api_key='C8Uk3Vj1AVM6xoSmz3B9h2LWmga4S2CGkYQTY29Pphk9',
                    secret_key='2EeCpaJe6VrHuhk72z53oM4pH1bF2NhLp1wCyX3oWrva')

    if not os.path.isdir(dir_basepath):
        os.mkdir(dir_basepath)

    # Check command line arguments
    if len(sys.argv) == 1:
        # Original functionality - download all symbols
        pass
    elif len(sys.argv) >= 2 and sys.argv[1] == '-check':
        # Check for incomplete data
        redownload = '-redownload' in sys.argv
        
        dirs = os.listdir(dir_basepath)
        dirs.sort()
        for _dir in dirs:
            if _dir.startswith('.') or _dir.startswith('0') or _dir == 'cache' or not os.path.isdir(f'{dir_basepath}/{_dir}'):
                continue
            
            files = os.listdir(f'{dir_basepath}/{_dir}')
            files.sort()
            for file in files:
                if not file.endswith('csv'):
                    continue
                file_date = file.split('.')[0]
                if file_date < '2022-01-01':
                    continue
                file_full_path = f'{dir_basepath}/{_dir}/{file}'
                try:
                    df = pd.read_csv(file_full_path, low_memory=False)
                except Exception as e:
                    print(f'Error reading {file_full_path}: {e}')
                    continue

                # Check for missing 13:30:00 time
                if not any(df['ts'].str.contains('13:30:00')):
                    print(f'Incomplete data for {_dir} on {file_date}')
                    if redownload:
                        do_redownload(api, dir_basepath, _dir, file_date)
                        print(f'Re-downloaded {_dir} on {file_date}')
                        sleep(1)

        exit(0)
    elif len(sys.argv) >= 2 and sys.argv[1] == '-ticktype':
        # Check for missing tick_type column
        dirs = os.listdir(dir_basepath)
        dirs.sort()
        for _dir in dirs:
            if len(_dir) != 4 or not _dir.isdigit():
                continue

            files = os.listdir(f'{dir_basepath}/{_dir}')
            files.sort()
            for file in files:
                if not file.startswith('20') or not file.endswith('csv'):
                    continue
                file_date = file.split('.')[0]
                if file_date < '2020-01-01':
                    continue
                file_full_path = f'{dir_basepath}/{_dir}/{file}'
                try:
                    df = pd.read_csv(file_full_path, low_memory=False)
                except Exception as e:
                    print(f'Error reading {file_full_path}: {e}')
                    continue

                # Check for missing tick_type column
                if 'tick_type' not in df.columns:
                    print(f'Missing tick_type for {_dir} on {file_date}')
                    do_redownload(api, dir_basepath, _dir, file_date)
                    print(f'Re-downloaded {_dir} on {file_date}')
                    sleep(1)

        exit(0)
    elif len(sys.argv) == 3:
        # New functionality - download specific symbol and date
        symbol = sys.argv[1]
        date_str = sys.argv[2]
        
        try:
            # Validate date format
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            
            # Create directory for symbol if it doesn't exist
            base_symbol_path = f'{dir_basepath}/{symbol}'
            if not os.path.isdir(base_symbol_path):
                os.mkdir(base_symbol_path)
            
            # Download ticks for specific symbol and date
            contract = api.Contracts.Stocks[symbol]
            ticks = api.ticks(contract, date_str)
            
            if len(ticks.ts) == 0:
                print(f'No data available for {symbol} on {date_str}')
                exit(0)
            
            # Save to CSV
            df = pd.DataFrame({**ticks})
            df.ts = pd.to_datetime(df.ts)
            output_file = f'{dir_basepath}/{symbol}/{date_str}.csv'
            df.to_csv(output_file, mode='w+')
            print(f'Successfully downloaded {symbol} data for {date_str}')
            exit(0)
            
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format")
            exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            exit(1)
    else:
        print("Usage:")
        print("  No arguments: Download all symbols")
        print("  check: Check and fix existing data")
        print("  <symbol> <date>: Download specific symbol data for date (YYYY-MM-DD)")
        exit(1)

    symbols = get_all_stock_code_name_dict(_api=api)
    symbols = sorted(symbols.keys(), reverse=len(sys.argv) > 1)

    contract_2303 = api.Contracts.Stocks['2303']
    ticks = api.ticks(contract_2303, '2024-05-03')
    if len(ticks.ts) == 0:
        print('We are banned... fuck it..')
        exit(0)

    bool_start = False

    
    list_contract = [api.Contracts.Indexs['TSE'].TSE001] + list(api.Contracts.Stocks.OTC) + list(api.Contracts.Stocks.TSE)

    for x in list_contract:
        if len(x.code) != 4 and x.code != '001':
            continue

        symbol = x.code

        if symbol in ['4804', '7642']:
            continue

        if False:

            if symbol == '4952':
                bool_start = True

            if not bool_start:
                continue

        contract = x 

        if x.code == '001':
            end_date = datetime.datetime.strptime(api.Contracts.Stocks['2303'].update_date, "%Y/%m/%d").date()
        else:
            end_date = datetime.datetime.strptime(x.update_date, "%Y/%m/%d").date()

        base_symbol_path = f'{dir_basepath}/{symbol}'

        if not os.path.isdir(base_symbol_path):
            os.mkdir(base_symbol_path)

        files_array = os.listdir(base_symbol_path)
        files_array.sort()

        try:
            this_symbol_start_date = (datetime.datetime.strptime(files_array[-1], '%Y-%m-%d.csv') + datetime.timedelta(days=1)).date()
        except Exception as e:
            this_symbol_start_date = start_date

        single_date: datetime.date
        print(f'{symbol} {this_symbol_start_date} -> {end_date}')
        for single_date in date_range(this_symbol_start_date, end_date):
            if single_date.weekday() in (5, 6):
                continue

            date_str = single_date.strftime("%Y-%m-%d")

            if os.path.isfile(f'{dir_basepath}/{symbol}/{date_str}.csv'):
                continue

            bool_tick_downloaded = False

            while not bool_tick_downloaded:
                try:
                    ticks = api.ticks(contract, date_str)
                    bool_tick_downloaded = True
                except Exception as e:
                    print(f'Error downloading {symbol} on {date_str}: {str(e)}')
                    time.sleep(60)
                    api = login()
                    print("Finish re-login")

            if len(ticks.ts) == 0:
                print(f'{symbol} {date_str} len = 0')
                time.sleep(1)
                continue

            time.sleep(1)

            print(f'{symbol} {date_str}')

            df = pd.DataFrame({**ticks})
            df.ts = pd.to_datetime(df.ts)

            if False:
                with open(f'{dir_basepath}/{symbol}/{date_str}.csv', 'w') as f:
                    f.write('\ufeff')

            df.to_csv(f'{dir_basepath}/{symbol}/{date_str}.csv', mode='w+')
