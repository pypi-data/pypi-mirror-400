import math
import time
import logging
import datetime as dt
from typing import List
from pandas.tseries.offsets import BDay

from slack_message.bot import slack_bot

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)


def get_all_user_files(client, upload_user_id):
    all_files = []
    page = 1
    while True:
        try:
            response = client.files_list(
                user_id=upload_user_id,
                page=page,
                count=500
            )
            current_page = response.get("page", 1)
            total_pages = response.get("total_pages", 1)

            if not response.get("ok"):
                _log.error(f"Failed to get files for user {upload_user_id} on page {page}")
                break

            files = response.get("files", [])
            all_files.extend(files)
            _log.info(f"Fetched {len(files)} files from page {current_page}/{total_pages} for user {upload_user_id}")

            if current_page >= total_pages:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            _log.error(f"Error fetching files for user {upload_user_id} on page {page}: {str(e)}")
            break

    return all_files


def cleanup_old_files(client,
                      all_file_prefix: List[str],
                      retention_time: int = 60 * 24,
                      tz=None,
                      use_business_days: bool = False,
                      ):
    """
    Delete files older than retention_time from a Slack channel.

    Args:
        client: Slack client instance
        all_file_prefix: file name prefix
        retention_time: File retention time in minutes
        tz: timezone for datetime calculation
        use_business_days: If True, calculate retention based on business days only
    """
    bot_user_id = client.auth_test().get("user_id")
    current_time = dt.datetime.now(tz)

    if use_business_days:
        business_days = retention_time / (24 * 60)
        cutoff_time = current_time - BDay(math.ceil(business_days))
        _log.info(f"Using business days calculation: {business_days:.2f} business days")
    else:
        cutoff_time = current_time - dt.timedelta(minutes=retention_time)
        _log.info(f"Using calendar days calculation: {retention_time} minutes")

    cutoff_timestamp = int(cutoff_time.timestamp())

    # Get all files first
    _log.info("Retrieving all files...")
    all_files = get_all_user_files(client, bot_user_id)
    _log.info(f"Retrieved {len(all_files)} total files for {bot_user_id}")

    deleted_count = 0
    for file_prefix in all_file_prefix:
        for file in all_files:
            file_name = file.get("name", "")
            file_id = file.get("id")
            if file_prefix and not file_name.startswith(file_prefix):
                continue
            file_created_timestamp = file.get("created", 0)

            if file_created_timestamp < cutoff_timestamp:
                try:
                    delete_response = client.files_delete(file=file_id)
                    if delete_response.get("ok"):
                        deleted_count += 1
                        _log.info(f"Deleted file: {file_name} (ID: {file_id})")
                    else:
                        _log.error(f"Failed to delete file: {file_name} (ID: {file_id})")
                except Exception as e:
                    _log.error(f"Error deleting file {file_name}: {str(e)}")

    time_type = "business days" if use_business_days else "calendar time"
    _log.info(f"Deleted {deleted_count} files older than {retention_time} minutes ({time_type}) with prefix {all_file_prefix}")


if __name__ == "__main__":
    token = 'xoxb-9346380601200-9352923381523-wFI5q7OCcWwRTTxxUQonfojp'
    slack_bot.connect(token=token)
    cleanup_old_files(client=slack_bot.client,
                      all_file_prefix=['shipping', 'orders'],
                      use_business_days=True
                      )