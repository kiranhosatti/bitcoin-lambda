import json
import boto3
import requests
import os
from datetime import datetime

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # ✅ Reads your bucket name from Lambda environment variable

# List of cryptocurrencies
CRYPTOCURRENCIES = ["bitcoin", "ethereum", "dogecoin"]
CURRENCY = "usd"

def lambda_handler(event, context):
    try:
        print("Lambda started")
        
        # Build CoinGecko API URL
        id = ",".join(CRYPTOCURRENCIES)
        url = f"https://api.github.com/repos/apache/airflow/issues"
        print(f"Fetching data from CoinGecko: {url}")
        
        response = requests.get(url)
        data = response.json()
        print(f"Data fetched: {data}")
        
        # Generate S3 folder & filename
        now = datetime.utcnow()
        folder = now.strftime("%Y/%m/%d")
        filename = f"{now.strftime('%H%M%S')}.json"
        key = f"cryptos/{folder}/{filename}"  # Example: cryptos/2026/02/22/072204.json
        print(f"Storing file in S3: {key}")
        
        # Upload JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        
        print("Stored successfully")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Stored successfully",
                "file": key,
                "data": data
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}