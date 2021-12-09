import json
import boto3
from ring_doorbell import Auth
import requests
from datetime import datetime
import os


s3 = boto3.resource('s3')
token_obj = s3.Object(os.getenv["BUCKET_NAME"], "token/test_token.cache")


def token_updated(token):
    token_obj.put(Body=json.dumps(token))

def lambda_handler(event, context):
    token = json.loads(token_obj.get()['Body'].read())
    
    headers = {'user-agent': 'android:com.ringapp:2.0.67(423)', "Authorization": "Bearer %s" %token["access_token"]}
    
    url = "https://api.ring.com/clients_api/" + "ring_devices"
    r = requests.get(url, headers=headers)
    response = r.json()
    device_id = (response["doorbots"][0]["id"])
    url = "https://api.ring.com/clients_api/" + "snapshots/image/" + str(device_id)
    r = requests.get(url, headers=headers)
    open('/tmp/snapshot.jpg', 'wb').write(r.content)
    s3.Bucket(os.getenv["BUCKET_NAME"]).upload_file('/tmp/snapshot.jpg',f'images/{datetime.now()}.jpg')