import cbpro

import json

# Import keys to api coinbase pro
with open("keys.json", 'r') as f:
    api_keys = json.loads(f.read())
    coinbase_pro_public_key = api_keys["coinbase-pro"]["public"]
    coinbase_pro_pass_key = api_keys["coinbase-pro"]["pass"]
    coinbase_pro_secret_key = api_keys["coinbase-pro"]["secret"]

auth_client = cbpro.AuthenticatedClient(coinbase_pro_public_key, coinbase_pro_secret_key, coinbase_pro_pass_key)

public_client = cbpro.PublicClient()

"""Auxiliary functions"""
# Downloading all information about cryptocurrencies.
result_about_all_cryptocurrencies = public_client.get_products()

