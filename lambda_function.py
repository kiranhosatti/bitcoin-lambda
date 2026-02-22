import json
import boto3
import requests
import os
import csv
from datetime import datetime
from io import StringIO

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # From Lambda environment

def lambda_handler(event, context):
    try:
        print("Lambda started")

        # GitHub issues API URL
        url = "https://api.github.com/repos/apache/airflow/issues"
        print(f"Fetching data from GitHub: {url}")

        response = requests.get(url)
        data = response.json()
        print(f"Data fetched: {len(data)} issues")

        # Extract only labels
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

        print(f"Total labels extracted: {len(all_labels)}")
        print("Sample labels:", all_labels[:5])

        # Generate S3 folder & filenames
        now = datetime.utcnow()
        folder = now.strftime("%Y/%m/%d")
        json_filename = f"{now.strftime('%H%M%S')}_labels.json"
        csv_filename = f"{now.strftime('%H%M%S')}_labels.csv"
        json_key = f"labels/{folder}/{json_filename}"
        csv_key = f"labels/{folder}/{csv_filename}"

        # Upload JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=json_key,
            Body=json.dumps(all_labels, indent=2),
            ContentType="application/json"
        )
        print(f"JSON labels stored in S3: {json_key}")

        # Convert to CSV and upload
        if all_labels:
            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=all_labels[0].keys())
            writer.writeheader()
            writer.writerows(all_labels)
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=csv_key,
                Body=csv_buffer.getvalue(),
                ContentType="text/csv"
            )
            print(f"CSV labels stored in S3: {csv_key}")
        else:
            print("No labels to store in CSV")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Labels stored successfully",
                "json_file": json_key,
                "csv_file": csv_key,
                "labels_count": len(all_labels)
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}