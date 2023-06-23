# import libs
import requests as req
import os
from datetime import datetime
import json
import boto3

def details_search(
    id: str = None,
    response_format: str = 'json'
    ):
    """Function that makes the requests for the Maps API - Details Search. 
    
    Parameters:
        id (str): Place id.
        response_format: Response format (json or xml).

    Returns:
        Response of the request
    """
    API_KEY = os.environ.get('GMAPS_API_KEY')
    endpoint = 'https://maps.googleapis.com/maps/api/place/details/'
    payload={}
    headers = {}

    # request the API
    url_loc = f"{endpoint}{response_format}?placeid={id}&key={API_KEY}"
    response = req.request("GET", url_loc, headers=headers, data=payload)
    return response

# function that saves data in S3 bucket
#@retry_abort
def s3_put_object(
    bucket_name: str, 
    file_key: str,
    file: object
    ):
    """Upload a file to an S3 bucket

    Parameters:
        file: File to upload
        bucket: Bucket to upload to
        object_name: S3 object name. If not specified then file_name is used
    Return:
        True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        response = s3_client.put_object(
            Bucket=bucket_name, 
            Key=file_key,
            Body=file,
            ContentType="text/plain;charset=utf-8"
            )
    except ClientError as e:
        print(e)
        return False
    return True

def lambda_handler(event, context):
    print("begin")
    # loop through event ids
    print(event)
    for id in event["detail"]["places_ids"]:
        print(id)
        # make the requests to details api

        response = details_search(id=id)
        response_dict = json.loads(response.text)
        response_encoded = json.dumps(
            response_dict, 
            ensure_ascii=False
            ).encode('utf8')
        
        # Upload to S3
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        bucket = "dcpgm-sor"
        prefix = "gmaps/details/"
        file_name = f"{id}_{timestamp}.json"
        key = f"{prefix}{file_name}"

        s3_put_object(
            bucket_name=bucket,
            file_key=key,
            file=response_encoded
            )