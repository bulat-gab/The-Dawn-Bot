import subprocess
import datetime
import os
import re
import csv
import sys
import time
import logging

from dotenv import load_dotenv

from google_sheets import GoogleSheetsEditor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

LOG_FILE_PATH = '/root/DawnBot/logs/logs.log'
RESULT_DIR = '/root/DawnBot/google-docs-updater/result'
DATETIME_FORMAT = '%Y-%m-%d'

SHEET_URL = os.getenv("SHEET_URL")


def get_last_lines(file_path=LOG_FILE_PATH, num_lines=100) -> list[str]:
    result = subprocess.run(
        ['tail', f'-n{num_lines}', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error reading file: {result.stderr.strip()}")
    return result.stdout.splitlines()

    # For debug
    # with open("../logs/logs.log", 'r') as f:
    #     return f.readlines()

def get_file_name_with_date(date: datetime = None, path: str = RESULT_DIR) -> str:
    if not os.path.exists(path):
        os.makedirs(path)

    if date is None:
        date = datetime.datetime.now()

    file_name = date.strftime(DATETIME_FORMAT + '.txt')
    file_path = os.path.join(path, file_name)
    return file_path

def seconds_until_tomorrow() -> int:
    now = datetime.datetime.now()
    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())

def load_stats(file_name: str) -> dict[str, float]:
    data = {}
    try:
        with open(file_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                email, points = line.strip().split(',')
                data[email] = float(points)
    except FileNotFoundError:
        data = {}

    return data

def get_yesterday_stats():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    file_name = get_file_name_with_date(yesterday)

    data = load_stats(file_name)
    return data

def _find_email_in_log_line(log_line:str):
    email_regex = r"Account:\s*([\w\.-]+@[\w\.-]+\.\w+)"

    match = re.search(email_regex, log_line)
    if match:
        email = match.group(1)
        return email
    else:
        return None
    
def _find_total_points(log_line:str):
    points_regex = r"Total points earned:\s*([\d\.]+)"

    match = re.search(points_regex, log_line)
    if match:
        total_points = float(match.group(1))
        return total_points
    else:
        return None
    
def _write_stats_to_file(data: dict[str, float]):
    file_name = get_file_name_with_date()

    existing_data = load_stats(file_name)
    for email, new_points in data.items():
        existing_data[email] = new_points

    with open(file_name, 'w', newline='') as f:
        to_write = [[email, points] for email, points in data.items()]
        writer = csv.writer(f)
        writer.writerows(to_write)

def _get_stats_from_server() -> dict[str, float]:
    logs = get_last_lines(num_lines=500)

    mapping = {}
    for log in logs:
        if 'Total points earned:' in log:
            email = _find_email_in_log_line(log)
            points = _find_total_points(log)

            mapping[email] = round(float(points), 1)

    sorted_mapping = dict(sorted(mapping.items()))
    return sorted_mapping

def update_stats():
    gse = GoogleSheetsEditor(SHEET_URL)
    wh = gse.worksheet('Dawn')

    email_col_index = gse.find_col_index('Email')
    points_col_index = gse.find_col_index('auto_Points')
    speed_col_index = gse.find_col_index('auto_Points per day')
    emails_col = wh.col_values(email_col_index)

    today_stats = _get_stats_from_server()
    yesterday_stats = get_yesterday_stats()

    for email, points in today_stats.items():
        email_row = emails_col.index(email) + 1

        yesterday_points = yesterday_stats.get(email)
        if yesterday_points is None:
            points_per_day = 'None'
        else:
            points_per_day = points - yesterday_points

        wh.update_cell(email_row, points_col_index, points)
        wh.update_cell(email_row, speed_col_index, points_per_day)
        logger.debug(f'Account {email} updated. Points {points}. points_per_day: {points_per_day}')
    
    _write_stats_to_file(today_stats)

def run():
    while True:
        date = datetime.datetime.now()

        today_result = get_file_name_with_date(date)
        if os.path.exists(today_result):
            sleep_time = seconds_until_tomorrow() + 1
            logger.info(f'Today\'s stats are there. Sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)
            
        update_stats()
        logger.info(f'Sleeping for 24 hours...')
        time.sleep(24 * 3600) # 24 hours


if __name__ == "__main__":
    run()