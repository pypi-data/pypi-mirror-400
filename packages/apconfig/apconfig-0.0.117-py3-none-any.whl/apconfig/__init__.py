import os
from typing import List

import requests


def get_api_setup_data():
    try:
        print(f"Connecting to http://{os.getenv('TSO_SETUP_URL')}/setup")
        with requests.Session() as session:
            response = session.get(url=f"http://{os.getenv('TSO_SETUP_URL')}/setup")
            response.raise_for_status()
            setup = response.json()
            return setup

    except Exception as e:
        raise


setup_data = get_api_setup_data()

# TSO Configuration
chains = setup_data["chains"]

# Data Service Streamers and APIs
WS = 'ws://'
WSS = 'wss://'
HTTP = 'http://'
HTTPS = 'https://'

tso_utilities_streamer_endpoint = setup_data["algorithms"]["streamers"]["utilities"]["url"]
tso_trades_streamer_endpoint = setup_data["algorithms"]["streamers"]["trades"]["url"]
tso_ticks_streamer_endpoint = setup_data["algorithms"]["streamers"]["ticks"]["url"]
tso_prepared_streamer_endpoint = setup_data["algorithms"]["streamers"]["prepared"]["url"]

streams = {
    'utilities': tso_utilities_streamer_endpoint,
    'trades': tso_trades_streamer_endpoint,
    'ticks': tso_prepared_streamer_endpoint,
    'prepared': tso_prepared_streamer_endpoint
}

tso_utility_topics = [topic for topic in setup_data["algorithms"]["tso"]["utility_topics"]]
print(tso_utility_topics)

# voting_round_symbol_data_endpoint = setup_data["algorithms"]["data"]["voting_round_symbol_data"]["url"]
chain_gateway_endpoint = setup_data["algorithms"]["data-connectors"]["flare-chain-gateway"]["url"]




# CHAIN VOTING ROUNDS
algorithm_prepared_data_buffer = 20
ml_predictions_buffer = 12
submission_commit_buffer = 7

# Web3 Providers
web3_provider_list: dict = {}
web3_websocket_list: dict = {}
for chain in chains:
    try:
        web3_provider_list[chain] = setup_data["chains"][chain]["providers"]["rpc"]
        web3_websocket_list[chain] = setup_data["chains"][chain]["providers"]["ws"]
    except Exception as e:
        print(e)

web3_urls: dict = {}
for chain in chains:
    try:
        web3_urls[chain] = list(zip(setup_data["chains"][chain]["providers"]["rpc"],
                                    setup_data["chains"][chain]["providers"]["ws"]))
    except Exception as e:
        print(e)


test_web3_provider_list = [os.getenv("WEB3_PROVIDER")]
test_web3_websocket_list = [os.getenv("WEB3_WEBSOCKETS")]

# Chain Wallet Configuration
ftso_reward_offers_manager_addresses = {}
ftso_feed_publisher_addresses = {}
for chain in chains:
    try:
        ftso_reward_offers_manager_addresses[chain] \
            = setup_data["chains"][chain]["ftso_reward_offers_manager_address"]
        ftso_feed_publisher_addresses[chain] \
            = setup_data["chains"][chain]["ftso_feed_publisher_address"]
    except Exception as e:
        print(e)


# print(f"froma {ftso_reward_offers_manager_addresses}")

# Database Configuration
environment = os.getenv("ENVIRONMENT")

assert environment is not None, "Environment not set. "
assert environment in ['development', 'production'], f"Environment has invalid value. Must be 'development' or 'production'."
assert environment in setup_data["environments"], f"Environment {environment} not found in setup data. "

mongo_database_name = setup_data["environments"][environment]["databases"]["mongo"]["name"]
mongo_database_uri = setup_data["environments"][environment]["databases"]["mongo"]["uri"]
mongo_database_uri_remote = setup_data["environments"][environment]["databases"]["mongo"]["uri_remote"]

# MySQL Main Database Configuration
try:
    mysql_main_host = setup_data["environments"][environment]["databases"]["mysql"]["main"]["host"]
    mysql_main_port = setup_data["environments"][environment]["databases"]["mysql"]["main"]["port"]
    mysql_main_name = setup_data["environments"][environment]["databases"]["mysql"]["main"]["name"]
    mysql_main_user = setup_data["environments"][environment]["databases"]["mysql"]["main"]["user"]
    mysql_main_password = setup_data["environments"][environment]["databases"]["mysql"]["main"]["password"]
except (KeyError, TypeError):
    mysql_main_host = None
    mysql_main_port = None
    mysql_main_name = None
    mysql_main_user = None
    mysql_main_password = None

# MySQL Indexer Database Configuration
try:
    mysql_indexer_host = setup_data["environments"][environment]["databases"]["mysql"]["indexer"]["host"]
    mysql_indexer_port = setup_data["environments"][environment]["databases"]["mysql"]["indexer"]["port"]
    mysql_indexer_name = setup_data["environments"][environment]["databases"]["mysql"]["indexer"]["name"]
    mysql_indexer_user = setup_data["environments"][environment]["databases"]["mysql"]["indexer"]["user"]
    mysql_indexer_password = setup_data["environments"][environment]["databases"]["mysql"]["indexer"]["password"]
except (KeyError, TypeError):
    mysql_indexer_host = None
    mysql_indexer_port = None
    mysql_indexer_name = None
    mysql_indexer_user = None
    mysql_indexer_password = None

# Chain Feeds and Symbols
all_chain_feeds = setup_data["assets"]
all_chain_symbols = setup_data["symbols"]

active_feed = os.getenv("FEED")
# assert active_feed in all_chain_feeds, f"Feed {active_feed} not found in setup data. "

# TSO Stuff
preparation_time_buffer = setup_data['tso']['preparation_time_buffer']
commit_submission_time_buffer = setup_data['tso']['commit_submission_time_buffer']
reveal_submission_time_buffer = setup_data['tso']['reveal_submission_time_buffer']
reveal_cutoff_time = setup_data['tso']['reveal_cutoff_time']
