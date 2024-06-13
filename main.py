import time
import okx.Funding as Funding
import re
import ast
import threading
import random

# API initialization
apikey = ""
secretkey = ""
passphrase = ""
eth = 'eth'
flag = "0"  # Production trading: 0, Demo trading: 1

fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

def get_currencies():
    result = fundingAPI.get_currencies()
    with open('withdrawal_result.txt', 'w') as file:
        file.write(str(result))

def check_min_fee():
    file_path = 'withdrawal_result.txt'

    # Read the file content
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Find all dictionary-like objects in the file content using a regular expression
    pattern = re.compile(r'\{.*?\}', re.DOTALL)
    matches = pattern.findall(file_content)

    # Search for the ETH-ERC20 entry
    eth_erc20_entry = None

    for match in matches:
        try:
            entry = ast.literal_eval(match)
            if isinstance(entry, dict) and entry.get('chain') == 'ETH-ERC20':
                eth_erc20_entry = entry
                break
        except (ValueError, SyntaxError):
            continue

    # Extract the minFee if the entry is found
    if eth_erc20_entry is not None and 'minFee' in eth_erc20_entry:
        return float(eth_erc20_entry['minFee'])
    else:
        print("ETH-ERC20 not found in the data.")
        return None

def perform_action(address):
    # Random sleep between 1 to 7 days
    sleep_time = random.randint(1, 7) * 87600  # Засыпает рандомно от 1 до 7 дней
    print(f"{address} заснул на {sleep_time}\n")
    time.sleep(sleep_time)

    attempts = 0
    while True:
        get_currencies()
        min_fee = check_min_fee()
        if min_fee is not None:
            print(f"The minFee for ETH-ERC20 is: {min_fee}")
            if min_fee <= 0.00056 or attempts >= 100:
                if min_fee > 0.0009:
                    print("minFee is greater than 0.0009. Retrying...")
                    attempts = 0  # Reset attempts if min_fee is greater than 0.0009
                    time.sleep(600)  # Wait for 10 minutes before retrying
                    continue
                # Generate random amount
                random_amount = round(random.uniform(0.01051, 0.01105), 5) # тут указывайте сумму на вывод ОТ и ДО
                # Perform the desired action
                print("Performing the action...")
                flag = "0"  # Production trading: 0, Demo trading: 1

                fundingAPI = Funding.FundingAPI(apikey, secretkey, passphrase, False, flag)

                # Withdrawal
                result = fundingAPI.withdrawal(
                    ccy="ETH",
                    toAddr=address,
                    amt=f"{random_amount}",
                    fee=f"{min_fee}",
                    dest="4",
                    chain="ETH-ERC20"
                )
                print(result)
                print(f"Деньги были отправлены на Адрес {address} с суммой {random_amount} и комиссией {min_fee} $ETH")
                break

        attempts += 1
        time.sleep(600)  # Wait for 10 minutes before checking again

def main():
    with open('adr.txt', 'r') as file:
        addresses = file.readlines()

    threads = []
    for address in addresses:
        address = address.strip()
        thread = threading.Thread(target=perform_action, args=(address,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
