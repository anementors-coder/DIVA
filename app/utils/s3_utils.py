import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize S3 client
def get_s3_client():
    """Get S3 client with proper configuration."""
    try:
        # If using IAM roles (recommended for production)
        if hasattr(settings, 'AWS_USE_IAM_ROLE') and settings.AWS_USE_IAM_ROLE:
            s3_client = boto3.client(
                's3',
                region_name=settings.AWS_REGION
            )
        else:
            # Using AWS credentials
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return s3_client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {str(e)}")
        raise


async def upload_resume_to_s3(file_content: bytes, file_key: str, content_type: str = "application/pdf") -> str:
    """
    Upload resume file to S3 bucket and return the URL.
    
    Args:
        file_content: Binary content of the file
        file_key: S3 object key (path/filename)
        content_type: MIME type of the file
    
    Returns:
        str: Public URL of the uploaded file
    
    Raises:
        Exception: If upload fails
    """
    try:
        s3_client = get_s3_client()
        
        # Upload file to S3
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_key,
            Body=file_content,
            ContentType=content_type,
            # Make file privately readable (adjust based on your security requirements)
            ACL='private',
            # Optional: Add metadata
            Metadata={
                'uploaded_by': 'eva_api',
                'file_type': 'resume'
            }
        )
        
        # Generate public URL
        if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN') and settings.AWS_S3_CUSTOM_DOMAIN:
            # If using CloudFront or custom domain
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
        else:
            # Standard S3 URL
            file_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        
        logger.info(f"Successfully uploaded file to S3: {file_key}")
        return file_url
        
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise Exception("AWS credentials not configured")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"AWS S3 ClientError: {error_code} - {str(e)}")
        
        if error_code == 'NoSuchBucket':
            raise Exception("S3 bucket not found")
        elif error_code == 'AccessDenied':
            raise Exception("Access denied to S3 bucket")
        else:
            raise Exception(f"Failed to upload to S3: {error_code}")
    except Exception as e:
        logger.error(f"Unexpected error uploading to S3: {str(e)}")
        raise Exception("Failed to upload file to storage")


async def delete_resume_from_s3(file_key: str) -> bool:
    """
    Delete resume file from S3 bucket.
    
    Args:
        file_key: S3 object key (path/filename)
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        s3_client = get_s3_client()
        
        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_key
        )
        
        logger.info(f"Successfully deleted file from S3: {file_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {file_key} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting from S3: {str(e)}")
        return False


def generate_presigned_url(file_key: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate a presigned URL for secure file access.
    
    Args:
        file_key: S3 object key (path/filename)
        expiration: URL expiration time in seconds (default: 1 hour)
    
    Returns:
        str: Presigned URL or None if generation fails
    """
    try:
        s3_client = get_s3_client()
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_S3_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )
        
        return presigned_url
        
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {file_key} - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {str(e)}")
        return None


def extract_file_key_from_url(url: str) -> Optional[str]:
    """
    Extract S3 file key from a full S3 URL.
    
    Args:
        url: Full S3 URL
    
    Returns:
        str: File key or None if extraction fails
    """
    try:
        if not url:
            return None
            
        # Handle different URL formats
        if 'amazonaws.com' in url:
            # Standard S3 URL format
            parts = url.split('amazonaws.com/')
            if len(parts) > 1:
                return parts[1]
        elif hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN') and settings.AWS_S3_CUSTOM_DOMAIN in url:
            # Custom domain format
            parts = url.split(f"{settings.AWS_S3_CUSTOM_DOMAIN}/")
            if len(parts) > 1:
                return parts[1]
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to extract file key from URL: {url} - {str(e)}")
        return None


def validate_file_size(file_content: bytes, max_size: int = 5 * 1024 * 1024) -> bool:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_content: Binary content of the file
        max_size: Maximum allowed size in bytes (default: 5MB)
    
    Returns:
        bool: True if file size is valid, False otherwise
    """
    return len(file_content) <= max_size


def validate_pdf_content(file_content: bytes) -> bool:
    """
    Basic validation to check if file content is a PDF.
    
    Args:
        file_content: Binary content of the file
    
    Returns:
        bool: True if content appears to be a PDF, False otherwise
    """
    try:
        # PDF files start with %PDF
        return file_content[:4] == b'%PDF'
    except Exception:
        return False

async def get_resume_content_from_s3(file_key: str) -> Optional[bytes]:
    """
    Retrieve the binary content of a resume file from S3.
    
    Args:
        file_key: S3 object key (path/filename)
    
    Returns:
        bytes: Binary content of the file, or None if not found or on error.
    """
    try:
        s3_client = get_s3_client()
        
        response = s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_key
        )
        
        file_content = response['Body'].read()
        logger.info(f"Successfully retrieved content for file from S3: {file_key}")
        return file_content
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"File not found in S3: {file_key}")
        else:
            logger.error(f"Failed to retrieve file content from S3: {file_key} - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving file content from S3: {str(e)}")
        return None