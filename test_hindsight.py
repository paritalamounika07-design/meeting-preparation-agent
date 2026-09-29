import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY")
base_url = os.getenv("HINDSIGHT_BASE_URL")
bank_id = os.getenv("HINDSIGHT_BANK_ID")

print("API key loaded:", bool(api_key))
print("Base URL:", base_url)
print("Bank ID:", bank_id)

client = Hindsight(
    base_url=base_url,
    api_key=api_key
)

print("Hindsight client created successfully!")