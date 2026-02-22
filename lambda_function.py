import json
import boto3
import requests
import os
from datetime import datetime

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # Your S3 bucket name

# List of cryptocurrencies to fetch
CRYPTOCURRENCIES = ["bitcoin", "ethereum", "dogecoin"]
CURRENCY = "usd"

def lambda_handler(event, context):
    try:
        # Build API URL
        ids = ",".join(CRYPTOCURRENCIES)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={CURRENCY}"
        
        # Fetch prices from CoinGecko
        response = requests.get(url)
        data = response.json()
        
        # Generate folder structure based on date
        now = datetime.utcnow()
        folder = now.strftime("%Y/%m/%d")
        filename = f"{now.strftime('%H%M%S')}.json"
        key = f"cryptos/{folder}/{filename}"  # e.g., cryptos/2026/02/22/072204.json

        # Upload JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Stored successfully",
                "file": key,
                "data": data
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }