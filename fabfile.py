import os
import logging

from fabric import Connection, task
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv("./.env")

SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_USER = os.getenv("REMOTE_USER")
GITHUB = os.getenv("GITHUB")
PROJECT_PATH = os.getenv("PROJECT_PATH")
LOCAL_PATH = os.getenv("LOCAL_PATH")


def init_connection() -> Connection:
    conn = Connection(
        host=REMOTE_HOST,
        user=REMOTE_USER,
        connect_kwargs={
            "key_filename": SSH_KEY_PATH,
        }
    )

    return conn

def upload_file(c: Connection, file_name: str):
    local_folder = os.path.join(LOCAL_PATH, file_name)
    remote_folder = PROJECT_PATH + "/" + file_name

    result = c.put(local_folder, remote_folder)
    logger.info("Uploaded {0.local} to {0.remote}".format(result))

def is_repo_exist(c: Connection) -> bool:
    result = c.run(f"if [ -d {PROJECT_PATH} ]; then echo 'exists'; else echo 'not found'; fi", hide=True)
    is_exist = result.stdout.strip() == "exists"
    if is_exist:
        return True
    
    logger.info(f"Repository '{PROJECT_PATH}' does not exist. Cloning... ")
    c.run(f"git clone {GITHUB}")
    return False

@task
def download_db(c: Connection):
    try:
        c = init_connection()
        remote_file_path = PROJECT_PATH + '/' + 'database/database.sqlite3'
        local_file_path = './database/remote_database.sqlite3'

        c.get(remote=remote_file_path, local=local_file_path)
        logger.info(f"File downloaded successfully to {local_file_path}")

    except Exception as e:
        logger.error(f"download_database has failed. {e}")


@task
def upload_db(c: Connection):
    c = init_connection()
    c.run(f'cd {PROJECT_PATH}/database && cp ./database.sqlite3 database.sqlite3.backup && rm ./database.sqlite3')

    # delete temporary files
    c.run(f'rm {PROJECT_PATH}/database/database.sqlite3-shm')
    c.run(f'rm {PROJECT_PATH}/database/database.sqlite3-wal')

    logger.info(f'database backup created: "database.sqlite3.backup"')
    db_name = './database/database.sqlite3'
    upload_file(c, db_name)

@task
def upload_farm(c: Connection):
    c = init_connection()
    upload_file(c, "do_not_commit.config/data/farm.txt")

@task
def deploy(c: Connection):
    try:
        c = init_connection()
        c.run(f"cd {PROJECT_PATH} && git fetch origin main && git reset --hard origin/main")

        # upload_file(c, "database/database.sqlite3") # Use with caution. Local database might contain expired auth tokens.
        upload_file(c, "do_not_commit.config/settings.yaml")
        upload_file(c, "do_not_commit.config/data/farm.txt")
        c.run(f"cd {PROJECT_PATH} && docker compose up -d --build")
    except Exception as e:
        logger.error(f"Deploy has failed. {e}")
