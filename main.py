import time
import random
from web3 import Web3
from eth_account import Account
import requests


# _______________________________ CONFIG PARAMETERS ___________________________________

INFURA_PROJECT_ID = "e00000000000000000000000000000" # Получить тут https://app.infura.io/

GAS_PRICE_MIN = 1                         # Минимальная цена газа в Gwei
GAS_PRICE_MAX = 10                           # Максимальная цена газа в Gwei

DEPOSIT_AMOUNT_MIN = 0.0001                 # Минимальная сумма депозита в ETH
DEPOSIT_AMOUNT_MAX = 0.0002                 # Максимальная сумма депозита в ETH

DELAY_MIN = 5                               # Минимальная задержка между транзакциями в секундах
DELAY_MAX = 15                              # Максимальная задержка между транзакциями в секундах

SHUFFLE_WALLETS = True                      # Перемешивать кошельки перед отправкой транзакций

# Адрес контракта Elixir https://etherscan.io/address/0x1f75881dc0707b5236f739b5b64a87c211294abb
CONTRACT_ADDRESS = "0x1F75881DC0707b5236f739b5B64A87c211294Abb" # Менять не нужно

# ________________________________________________________________________________

art = '''

███████╗██╗     ██╗██╗  ██╗██╗██████╗      █████╗ ██╗   ██╗████████╗ ██████╗ ███████╗ ██████╗ ███████╗████████╗
██╔════╝██║     ██║╚██╗██╔╝██║██╔══██╗    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝██╔═══██╗██╔════╝╚══██╔══╝
█████╗  ██║     ██║ ╚███╔╝ ██║██████╔╝    ███████║██║   ██║   ██║   ██║   ██║███████╗██║   ██║█████╗     ██║   
██╔══╝  ██║     ██║ ██╔██╗ ██║██╔══██╗    ██╔══██║██║   ██║   ██║   ██║   ██║╚════██║██║   ██║██╔══╝     ██║   
███████╗███████╗██║██╔╝ ██╗██║██║  ██║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝███████║╚██████╔╝██║        ██║   
╚══════╝╚══════╝╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝        ╚═╝   

CHANNEL: @VPoiskahGema

'''
print(art)

# Функция получения цены Eth в usdt
def get_eth_price_in_usdt():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на наличие ошибок
        data = response.json()
        eth_price = data['ethereum']['usd']
        return eth_price
    except requests.RequestException as e:
        print(f"Ошибка при получении цены ETH: {e}. Используем 3070 usdt\n")
        return 3070


# Функция проверки газа
def normal_gwei_price():
    # Получаем текущую рекомендуемую цену газа
    gas_price = web3.eth.gas_price
    # Конвертируем цену газа из Wei в Gwei
    gas_price_gwei = web3.from_wei(gas_price, 'gwei')

    if (gas_price_gwei > GAS_PRICE_MIN) and (gas_price_gwei < GAS_PRICE_MAX):
        print(f'Газ в норме: {gas_price_gwei} [от {GAS_PRICE_MIN} до {GAS_PRICE_MAX}]')
        return True
    else:
        print(f'Газ не в норме: {gas_price_gwei} [от {GAS_PRICE_MIN} до {GAS_PRICE_MAX}]\nЖдем 10 сек\n')
        time.sleep(10)
        return normal_gwei_price()


# Функция для добавления ликвидности
def add_liquidity(private_key):

    account = Account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    gas_price = random.uniform(GAS_PRICE_MIN, GAS_PRICE_MAX)
    deposit_amount = random.uniform(DEPOSIT_AMOUNT_MIN, DEPOSIT_AMOUNT_MAX)

    tx = contract.functions.deposit().build_transaction({
        'chainId': 1,  # Mainnet
        'gas': 200000,
        'gasPrice': web3.to_wei(gas_price, 'gwei'),
        'nonce': nonce,
        'value': web3.to_wei(deposit_amount, 'ether')  # Рандомное значение депозита
    })

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {
        "tx_hash": tx_hash,
        "account_address": account.address,
        "deposit_amount": deposit_amount,
        "gas_price": gas_price,
        "gas_used": tx['gas']
    }


# Настройка подключения к сети Ethereum (например, через Infura)
infura_url = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Проверка подключения
if not web3.is_connected():
    print("Ошибка подключения к сети Ethereum")
    exit()

# Адрес контракта и ABI (Application Binary Interface) https://etherscan.io/address/0x1f75881dc0707b5236f739b5b64a87c211294abb#code
contract_address = web3.to_checksum_address(CONTRACT_ADDRESS)
contract_abi = [
    {"inputs": [{"internalType": "address", "name": "_owner", "type": "address"}], "stateMutability": "nonpayable",
     "type": "constructor"},
    {"inputs": [], "name": "DepositFailed", "type": "error"},
    {"inputs": [], "name": "DepositsPaused", "type": "error"},
    {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}], "name": "OwnableInvalidOwner",
     "type": "error"},
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}],
     "name": "OwnableUnauthorizedAccount", "type": "error"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"},
                                    {"indexed": True, "internalType": "uint256", "name": "amount", "type": "uint256"}],
     "name": "Deposit", "type": "event"},
    {"anonymous": False,
     "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
     "name": "OwnershipTransferred", "type": "event"},
    {"inputs": [], "name": "controller", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "user", "type": "address"}], "name": "deposits",
     "outputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}], "stateMutability": "view",
     "type": "function"},
    {"inputs": [], "name": "depositsPaused", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bool", "name": "pauseDeposits", "type": "bool"}], "name": "pause", "outputs": [],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "_controller", "type": "address"}], "name": "setController",
     "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership",
     "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

# Считываем кошельки
private_keys_file = 'private_keys.txt'
with open(private_keys_file) as f:
    private_keys = f.readlines()
    # Удаление символов новой строки '\n' с конца каждой строки
    private_keys = [key.strip() for key in private_keys]

# Перемешивание кошельков, если включено
if SHUFFLE_WALLETS:
    random.shuffle(private_keys)

# Добавление ликвидности для каждого кошелька
for idx, private_key in enumerate(private_keys, start=1):

    # Если газ в норме
    if normal_gwei_price():
        result = add_liquidity(private_key)
        tx_hash = result['tx_hash'].hex()
        account_address = result['account_address']
        deposit_amount = result['deposit_amount']
        gas_price = result['gas_price']
        gas_used = result['gas_used']
        gas_cost_eth = web3.from_wei(gas_price * gas_used, 'ether')
        eth_price = get_eth_price_in_usdt()
        gas_cost_usd = float(gas_cost_eth) * eth_price  # Используйте текущий курс ETH/USD

        print(f"№ кошелька {idx}:")
        print(f"  Транзакция:      {tx_hash}")
        print(f"  Кошелек:         {account_address}")
        print(f"  Сумма депозита:  {deposit_amount:.6f} ETH [{eth_price * deposit_amount:.6f} USDT]")
        print(f"  Цена газа:       {gas_price:.6f} gwei")

        # Рандомная задержка между транзакциями
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        print(f"  Задержка:        {delay:.2f} секунд")
        time.sleep(delay)


