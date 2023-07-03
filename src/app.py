# import libs
import requests as req
import os
from datetime import datetime
import json
import boto3
import gzip

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
def s3_upload_file(
    bucket_name: str, 
    file_key: str,
    file_path: str
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
        response = s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=file_key
        )
    except ClientError as e:
        print(e)
        return False
    return True

def gzip_file(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            f_out.writelines(f_in)

def lambda_handler(event, context):
    print("begin")
    # loop through event ids
    print(event)
    for id in event["detail"]["places_ids"]:
        print(id)
        # make the requests to details api

        response = details_search(id=id)
        response_dict = json.loads(response.text)
        
        # Upload to S3
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        year_month_day = timestamp[0:8]
        bucket = "dcpgm-sor"
        prefix = f"gmaps/details/{year_month_day}/"
        file_name = f"{id}_{timestamp}"
        key = f"{prefix}{file_name}.gz"

        # Create a temporary file in the /tmp directory
        tmp_file_path_json = f'/tmp/{file_name}.json'
        tmp_file_path_gz = f'/tmp/{file_name}.gz'
        with open(tmp_file_path_json, 'w') as f:
            json.dump(
                obj=response_dict,
                fp=f,
                ensure_ascii=False
                )

        gzip_file(
            input_file=tmp_file_path_json,
            output_file=tmp_file_path_gz
            )

        s3_upload_file(
            bucket_name=bucket,
            file_key=key,
            file_path=tmp_file_path_gz
            )