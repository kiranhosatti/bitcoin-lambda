import json
import boto3
import requests
import os
from datetime import datetime
import pandas as pd

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # Reads bucket name from Lambda environment variable

# List of cryptocurrencies (not used for GitHub API but left here)
CRYPTOCURRENCIES = ["bitcoin", "ethereum", "dogecoin"]

def lambda_handler(event, context):
    try:
        print("Lambda started")
        
        # GitHub issues API URL
        url = "https://api.github.com/repos/apache/airflow/issues"
        print(f"Fetching data from GitHub: {url}")
        
        response = requests.get(url)
        data = response.json()
        print(f"Data fetched: {len(data)} issues")

        # Extract only labels from issues
        all_labels = []
        for issue in data:
            for label in issue.get("labels", []):
                label_info = {
                    "issue_number": issue["number"],
                    "issue_title": issue["title"],
                    "label_id": label["id"],
                    "label_name": label["name"],
                    "label_color": label["color"],
                    "label_description": label.get("description", "")
                }
                all_labels.append(label_info)

        # Convert labels list to DataFrame (optional, just for local debugging)
        df_labels = pd.DataFrame(all_labels)
        print(f"Total labels extracted: {len(df_labels)}")
        print(df_labels.head())

        # Generate S3 folder & filename
        now = datetime.utcnow()
        folder = now.strftime("%Y/%m/%d")
        filename = f"{now.strftime('%H%M%S')}_labels.json"
        key = f"labels/{folder}/{filename}"  # Example: labels/2026/02/22/072204_labels.json
        print(f"Storing labels file in S3: {key}")

        # Upload labels JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(all_labels),
            ContentType="application/json"
        )

        print("Labels stored successfully")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Labels stored successfully",
                "file": key,
                "labels_count": len(all_labels)
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}