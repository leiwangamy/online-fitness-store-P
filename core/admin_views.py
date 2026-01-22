"""
Admin views for database backup functionality
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse

# Import boto3 for S3 support (required for backup functionality)
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False


def get_backup_dir():
    """Get the backup directory path"""
    backup_dir = Path(settings.BASE_DIR) / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup():
    """
    Create a database backup using pg_dump
    Returns: (success: bool, backup_file: Path or None, error_message: str or None)
    """
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config.get('PASSWORD', '')
    db_host = db_config.get('HOST', 'localhost')
    db_port = db_config.get('PORT', '5432')
    
    backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = backup_dir / f"{db_name}_{timestamp}.backup"
    
    # Set up environment
    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password
    
    # Use pg_dump directly - it's installed in the web container
    # In Docker, containers can connect to each other using service names (e.g., 'db')
    # For local development, use localhost or the configured host
    pg_dump_path = os.getenv('PG_DUMP_PATH', 'pg_dump')
    command = [
        pg_dump_path,
        '-U', db_user,
        '-h', db_host,  # This will be 'db' in Docker, 'localhost' locally
        '-p', db_port,
        '-F', 'c',  # Custom format (compressed)
        '-b',      # Include blobs
        '-f', str(backup_file),
        db_name
    ]
    
    try:
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Check if backup file was created and has content
        if not backup_file.exists():
            error_msg = result.stderr or result.stdout or "Backup file was not created"
            return False, None, f"Backup failed: {error_msg}"
        
        file_size = backup_file.stat().st_size
        if file_size == 0:
            backup_file.unlink()
            error_msg = result.stderr or result.stdout or "Backup file is empty"
            return False, None, f"Backup failed: {error_msg}"
        
        if result.returncode == 0 and file_size > 0:
            # Clean up old backups (keep only 5 most recent)
            cleanup_old_backups(backup_dir, keep_count=5)
            
            file_size_mb = file_size / (1024 * 1024)
            return True, backup_file, f"Backup created successfully ({file_size_mb:.2f} MB)"
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            if backup_file.exists():
                backup_file.unlink()
            return False, None, f"Backup failed: {error_msg}"
            
    except subprocess.TimeoutExpired:
        if backup_file.exists():
            backup_file.unlink()
        return False, None, "Backup timed out after 5 minutes"
    except FileNotFoundError:
        return False, None, f"pg_dump not found. Please rebuild the web container to install PostgreSQL client tools: docker compose -f docker-compose.prod.yml build web && docker compose -f docker-compose.prod.yml up -d"
    except Exception as e:
        if backup_file.exists():
            backup_file.unlink()
        return False, None, f"Error creating backup: {str(e)}"


def cleanup_old_backups(backup_dir, keep_count=5):
    """Keep only the most recent backups"""
    backups = sorted(
        backup_dir.glob("*.backup"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    if len(backups) > keep_count:
        for old_backup in backups[keep_count:]:
            try:
                old_backup.unlink()
            except Exception:
                pass  # Ignore errors when deleting old backups


def delete_old_backups(keep_count=5, delete_empty=True, days_old=None):
    """
    Delete old backup files with safety checks
    
    Args:
        keep_count: Number of most recent backups to keep (default: 5)
        delete_empty: Whether to delete empty backup files (default: True)
        days_old: Delete backups older than this many days (optional)
    
    Returns:
        (deleted_count: int, deleted_files: list, error_message: str or None)
    """
    backup_dir = get_backup_dir()
    deleted_files = []
    deleted_count = 0
    
    try:
        backups = list(backup_dir.glob("*.backup"))
        
        if not backups:
            return 0, [], None
        
        # Safety check: Don't delete if we have fewer backups than keep_count
        non_empty_backups = [b for b in backups if b.stat().st_size > 0]
        if len(non_empty_backups) <= keep_count and not delete_empty:
            return 0, [], "Not enough backups to delete. All backups are within retention policy."
        
        # Delete empty backups first if requested
        if delete_empty:
            empty_backups = [b for b in backups if b.stat().st_size == 0]
            for backup in empty_backups:
                try:
                    backup.unlink()
                    deleted_files.append(backup.name)
                    deleted_count += 1
                    backups.remove(backup)
                except Exception as e:
                    pass  # Ignore errors
        
        # Delete backups older than specified days (only if days_old is set)
        if days_old and days_old > 0:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            backups_to_delete_by_age = []
            for backup in backups:
                try:
                    backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                    if backup_time < cutoff_date:
                        backups_to_delete_by_age.append(backup)
                except Exception:
                    pass
            
            # Only delete if we'll still have at least keep_count backups remaining
            remaining_after_age_delete = len(backups) - len(backups_to_delete_by_age)
            if remaining_after_age_delete >= keep_count:
                for old_backup in backups_to_delete_by_age:
                    try:
                        old_backup.unlink()
                        deleted_files.append(old_backup.name)
                        deleted_count += 1
                        backups.remove(old_backup)
                    except Exception:
                        pass
        
        # Keep only the most recent N backups (only delete if we have more than keep_count)
        if len(backups) > keep_count:
            backups_sorted = sorted(
                backups,
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            backups_to_delete = backups_sorted[keep_count:]
            
            for old_backup in backups_to_delete:
                try:
                    old_backup.unlink()
                    deleted_files.append(old_backup.name)
                    deleted_count += 1
                except Exception:
                    pass  # Ignore errors
        
        return deleted_count, deleted_files, None
        
    except Exception as e:
        return deleted_count, deleted_files, f"Error during cleanup: {str(e)}"


def upload_to_s3(backup_file):
    """
    Upload backup file to S3 from EC2 server
    Uses IAM role credentials if available, otherwise falls back to access keys
    Returns: (success: bool, s3_url: str or None, error_message: str or None)
    """
    if not S3_AVAILABLE:
        return False, None, "boto3 is not installed. Install it with: pip install boto3"
    
    # Get S3 settings from environment
    aws_region = os.environ.get('AWS_REGION', 'ca-central-1')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    backup_prefix = os.environ.get('AWS_BACKUP_PREFIX', 'db-backups/')
    
    if not bucket_name:
        return False, None, "S3 bucket not configured. Set AWS_STORAGE_BUCKET_NAME environment variable."
    
    # Check if using IAM role (no access keys) or explicit credentials
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    use_iam_role = not (aws_access_key_id and aws_secret_access_key)
    
    try:
        # If IAM role is available, boto3 will automatically use it
        # Otherwise, use explicit credentials if provided
        if use_iam_role:
            # Use IAM role (boto3 will automatically use instance profile credentials)
            s3_client = boto3.client('s3', region_name=aws_region)
        else:
            # Use explicit credentials
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
        
        # Ensure prefix ends with /
        if not backup_prefix.endswith('/'):
            backup_prefix += '/'
        
        s3_key = f"{backup_prefix}{backup_file.name}"
        
        s3_client.upload_file(
            str(backup_file),
            bucket_name,
            s3_key,
            ExtraArgs={'ServerSideEncryption': 'AES256'}
        )
        
        s3_url = f"s3://{bucket_name}/{s3_key}"
        return True, s3_url, f"Backup uploaded to S3: {s3_url}"
        
    except ClientError as e:
        return False, None, f"S3 upload failed: {str(e)}"
    except Exception as e:
        return False, None, f"Error uploading to S3: {str(e)}"


@staff_member_required
def cleanup_backups(request):
    """Admin view to manually clean up old backups"""
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('admin_backup_database'))
    
    try:
        keep_count = int(request.POST.get('keep_count', 5))
        delete_empty = request.POST.get('delete_empty') == 'on'
        days_old = request.POST.get('days_old', '').strip()
        days_old = int(days_old) if days_old and days_old.isdigit() else None
        
        deleted_count, deleted_files, error = delete_old_backups(
            keep_count=keep_count,
            delete_empty=delete_empty,
            days_old=days_old
        )
        
        if error:
            messages.error(request, error)
        else:
            if deleted_count > 0:
                file_list = ', '.join(deleted_files[:5])
                if len(deleted_files) > 5:
                    file_list += f" and {len(deleted_files) - 5} more"
                messages.success(
                    request, 
                    f"Successfully deleted {deleted_count} backup file(s): {file_list}"
                )
            else:
                messages.info(request, "No backups were deleted. All backups are within the retention policy.")
        
    except ValueError:
        messages.error(request, "Invalid input. Please enter valid numbers.")
    except Exception as e:
        messages.error(request, f"Error during cleanup: {str(e)}")
    
    return HttpResponseRedirect(reverse('admin_backup_database'))


@staff_member_required
def backup_database(request):
    """Admin view to create database backup on EC2 server and upload to S3"""
    if request.method == 'POST' and 'action' in request.POST:
        # Handle cleanup action
        if request.POST['action'] == 'cleanup':
            return cleanup_backups(request)
    
    if request.method == 'POST':
        # Create backup on EC2 server
        success, backup_file, message = create_backup()
        
        if success:
            # Verify backup file exists and has content before uploading
            if backup_file.exists() and backup_file.stat().st_size > 0:
                messages.success(request, message)
                
                # Always upload to S3 from EC2 server
                s3_success, s3_url, s3_message = upload_to_s3(backup_file)
                if s3_success:
                    messages.success(request, s3_message)
                    # Keep the file temporarily for download option
                    # It will be cleaned up by the cleanup_old_backups function
                else:
                    messages.warning(request, f"S3 upload failed: {s3_message}")
                    # Still allow download even if S3 upload failed
                
                # Redirect to download page
                return HttpResponseRedirect(
                    reverse('admin_backup_download', kwargs={'filename': backup_file.name})
                )
            else:
                messages.error(request, "Backup file is empty or was not created properly.")
        else:
            messages.error(request, message)
    
    # Get list of existing backups (for download only - these are temporary copies)
    backup_dir = get_backup_dir()
    backups = sorted(
        backup_dir.glob("*.backup"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    backup_list = []
    for backup in backups[:10]:  # Show last 10 backups
        size_mb = backup.stat().st_size / (1024 * 1024)
        backup_list.append({
            'filename': backup.name,
            'size_mb': size_mb,
            'created': datetime.fromtimestamp(backup.stat().st_mtime)
        })
    
    # Check S3 configuration (IAM role or access keys)
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # S3 is configured if bucket name is set AND (IAM role available OR access keys provided)
    s3_configured = bool(bucket_name) and (
        bool(aws_access_key_id and aws_secret_access_key) or 
        # IAM role will be automatically used if no access keys are provided
        (not aws_access_key_id and not aws_secret_access_key)
    )
    
    context = {
        'backups': backup_list,
        's3_available': S3_AVAILABLE,
        's3_configured': s3_configured if S3_AVAILABLE else False,
        'using_iam_role': bool(bucket_name) and not (aws_access_key_id and aws_secret_access_key),
    }
    
    return render(request, 'admin/backup_database.html', context)


@staff_member_required
def download_backup(request, filename):
    """Download a backup file"""
    backup_dir = get_backup_dir()
    backup_file = backup_dir / filename
    
    if not backup_file.exists() or not backup_file.is_file():
        messages.error(request, f"Backup file '{filename}' not found.")
        return HttpResponseRedirect(reverse('admin_backup_database'))
    
    # Security check: ensure file is in backup directory
    try:
        backup_file.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        messages.error(request, "Invalid backup file path.")
        return HttpResponseRedirect(reverse('admin_backup_database'))
    
    # Serve the file
    with open(backup_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

