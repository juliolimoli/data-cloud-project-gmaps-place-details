# import libs
import requests as req
import os
import time
from datetime import datetime
import json

# function that retry and abort on attempts to do something
def retry_abort(func: function, max_retries: int = 3):
    def retry_abort_wrapper(*args, **kwargs):
        function_name = func.__name__
        print(f"Initializing the function: {function_name}")
        for attempt in range(1, max_retries+1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                if attempt == max_retries:
                    # abort
                    raise e
                time.sleep(5)
    return retry_abort_wrapper

# function that requests in the details search
@retry_abort
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
@retry_abort
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
    # File to upload
    upload_byte_stream = bytes(file.encode("UTF-8"))

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        response = s3_client.put_object(
            Bucket=bucket_name, 
            Key=file_key, 
            Body=upload_byte_stream
            )
    except ClientError as e:
        print(e)
        return False
    return True

def lambda_handler(event, context):

    # loop through event ids
    ids = event['places_ids']
    for id in ids:

        # make the requests to details api

        response = details_search(id=id)
        response_dict = json.loads(response.text)

        # Upload to S3
        t = datetime.now()
        timestamp = datetime.strftime(t, "%Y%m%d%H%M%S%f")
        bucket = "SoR"
        prefix = "gmaps/details/"
        file_name = f"{id}_{timestamp}.json"
        key = f"{prefix}{file_name}"

        s3_put_object(
            bucket_name=bucket,
            file_key=key,
            file=response_dict
            )