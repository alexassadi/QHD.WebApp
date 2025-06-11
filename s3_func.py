import boto3
from decouple import config
from urllib.parse import urlparse
from decouple import config, Csv

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def export_result_to_s3(s3_key, data, content_type):
    # Define S3 bucket and file path
    s3_bucket = AWS_STORAGE_BUCKET_NAME

    # Upload JSON to S3
    s3.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=data,
        ContentType=content_type  # Set content type
    )

    url = f"https://{s3_bucket}.s3.eu-west-2.amazonaws.com/{s3_key}"

    print(f"✅ JSON uploaded successfully to s3://{s3_bucket}/{s3_key}")
    return url

def delete_s3_file_from_url(s3_url):
    """
    Deletes an S3 object using its full S3 URL.
    """
    # Parse the URL to get the object key
    parsed_url = urlparse(s3_url)
    key = parsed_url.path.lstrip('/')  # Removes leading slash

    # Create an S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='eu-west-2',
    )

    try:
        s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        print(f"❌ Failed to delete {key}: {e}")
        return False