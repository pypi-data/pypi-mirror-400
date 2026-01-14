import mypylib
from mypylib.sjtools import SJ_wrapper, Stock
from mypylib import timeIt, get_punishment_list, get_short_selling_list
import os
import finlab
from finlab import data
from datetime import datetime, timedelta

from mypylib.keys import SHIOAJI_API_KEY, SHIOAJI_SECRET_KEY
from mypylib.keys import FINLAB_API_KEY


mypylib.path_cronlog = os.path.expanduser("~/daily_stock_data")

if not os.path.isdir(mypylib.path_cronlog):
    os.makedirs(mypylib.path_cronlog, exist_ok=True)

try:
    sj = SJ_wrapper(api_key=SHIOAJI_API_KEY,
                    secret_key=SHIOAJI_SECRET_KEY,
                    bool_fake_login=False)
    sj.save_all_contracts(f'{mypylib.path_cronlog}/all_stocks.pickle')
except Exception as e:
    print(f"Error getting all stocks: {e}")

try:
    list_punishments = get_punishment_list()
    print(list_punishments)
except Exception as e:
    print(f"Error getting punishments: {e}")

try:    
    list_short_selling_list = get_short_selling_list()
    print(list_short_selling_list)
except Exception as e:
    print(f"Error getting short selling list: {e}")

try:
    finlab.login(FINLAB_API_KEY)
    with data.universe("TSE_OTC"):
        capital = data.get('financial_statement:股本')
        capital.iloc[-1].to_csv(f'~/daily_stock_data/capital.txt')
except Exception as e:
    print(f"Error getting capital: {e}")


try:
    finlab.login(FINLAB_API_KEY)
    with data.universe("TSE_OTC"):
        date_10_days_ago = datetime.now() - timedelta(days=10)
        data.truncate_start = date_10_days_ago.strftime('%Y-%m-%d')
        volume_odd = data.get('intraday_odd_lot_trade:成交股數')
        str_date = volume_odd.index[-1].strftime('%Y-%m-%d')
        latest = volume_odd.iloc[-1, :]
        latest.to_csv(f'~/daily_stock_data/odd_volume.txt')
        latest.to_csv(f'~/daily_stock_data/odd_volume-{str_date}.txt')

except Exception as e:
    print(f"Error getting odd volume: {e}")


try:
    import re
    import glob
    
    # 1. scandir ~/daily_stock_data
    data_dir = os.path.expanduser("~/daily_stock_data")
    
    # 2. Find all files matching pattern all_stocks-YYYYMMDD.txt and find the largest (latest) one
    pattern = os.path.join(data_dir, "all_stocks-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].txt")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        print("No files found matching pattern all_stocks-YYYYMMDD.txt")
    else:
        # Extract dates and find the latest one
        file_date_pairs = []
        for filepath in matching_files:
            filename = os.path.basename(filepath)
            match = re.search(r'all_stocks-(\d{8})\.txt', filename)
            if match:
                date_str = match.group(1)
                file_date_pairs.append((date_str, filepath))
        
        if not file_date_pairs:
            print("No valid date found in matching files")
        elif len(file_date_pairs) < 2:
            print(f"Not enough files found. Need at least 2 files, but found {len(file_date_pairs)}")
        else:
            # Sort by date (largest = latest)
            file_date_pairs.sort(key=lambda x: x[0], reverse=True)
            # Find the one before last one (second newest)
            second_newest_file = file_date_pairs[1][1]
            print(f"Using second newest file: {second_newest_file}")
            
            # 3. Read the second newest file and create dict_yesterday (symbol -> limit_up)
            dict_yesterday = {}
            with open(second_newest_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('\t')  # Tab-separated
                    if len(parts) >= 3:
                        symbol = parts[0]
                        limit_up = parts[2]  # limit_up is the 3rd column (index 2)
                        try:
                            dict_yesterday[symbol] = float(limit_up)
                        except ValueError:
                            continue
            
            print(f"Loaded {len(dict_yesterday)} symbols from yesterday file")
            
            # 4. Read ~/daily_stock_data/all_stocks.txt and create dict_today (symbol -> reference)
            today_file = os.path.join(data_dir, "all_stocks.txt")
            if not os.path.exists(today_file):
                print(f"File not found: {today_file}")
            else:
                dict_today = {}
                with open(today_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split('\t')  # Tab-separated
                        if len(parts) >= 5:
                            symbol = parts[0]
                            reference = parts[4]  # reference is the 5th column (index 4)
                            try:
                                dict_today[symbol] = float(reference)
                            except ValueError:
                                continue
                
                print(f"Loaded {len(dict_today)} symbols from today file")
                
                # 5. Compare and write symbols where dict_today[symbol] == dict_yesterday[symbol]
                output_file = os.path.join(data_dir, "yesterday_limit_up_lock.txt")
                matching_symbols = []
                
                for symbol in dict_today:
                    if symbol in dict_yesterday:
                        if dict_today[symbol] == dict_yesterday[symbol]:
                            matching_symbols.append(symbol)
                
                # Write each symbol to a new line
                with open(output_file, 'w', encoding='utf-8') as f:
                    for symbol in sorted(matching_symbols):
                        f.write(f"{symbol}\n")
                
                print(f"Found {len(matching_symbols)} symbols where today's reference equals yesterday's limit_up")
                print(f"Results written to: {output_file}")

except Exception as e:
    print(f"Error processing limit up lock: {e}")
    import traceback
    traceback.print_exc()

