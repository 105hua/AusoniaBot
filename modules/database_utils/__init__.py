# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import os
import json
from typing import Optional
from datetime import datetime
from uuid import uuid4
import psycopg
from discord import Member
from modules.logging_utils import Logger

SYNC_LOGGER = Logger()
DB_NAME = "ausonia"
USERNAME = "ausonia_user"
PASSWORD = os.environ["DB_PASSWORD"]
CONNECTION = psycopg.connect(
    dbname=DB_NAME,
    host=os.environ["POSTGRES_URL"] if "POSTGRES_URL" in os.environ else "127.0.0.1",
    user=USERNAME,
    password=PASSWORD
)

with open(os.path.join(os.getcwd(), "defaults", "user_config.json"), encoding="UTF-8") as f:
    try:
        DEFAULT_USER_CONFIG = json.loads(f.read())
    except IOError as exc:
        raise exc

with open(os.path.join(os.getcwd(), "defaults", "server_config.json"), encoding="UTF-8") as f:
    try:
        DEFAULT_SERVER_CONFIG = json.loads(f.read())
    except IOError as exc:
        raise exc

#
# General Functions
#

def setup_database() -> bool:
    try:
        cursor = CONNECTION.cursor()
        # Add server configurations table.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS server_configurations (
                server_id BIGINT PRIMARY KEY,
                config JSON
            )
            """
        )
        # Add user configurations table.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_configurations (
                user_id BIGINT PRIMARY KEY,
                config JSON
            )
            """
        )
        # Add punishments table.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS punishments (
                punishment_id TEXT PRIMARY KEY,
                server_id BIGINT NOT NULL,
                enforcer_id BIGINT NOT NULL,
                offender_id BIGINT NOT NULL,
                reason TEXT NOT NULL,
                issued_epoch BIGINT NOT NULL,
                expiry_epoch BIGINT NOT NULL
            )
            """
        )
        # Commit changes.
        CONNECTION.commit()
        return True
    except psycopg.OperationalError:
        return False

#
# Server Configuration Functions
#

def server_config_exists_in_db(server_id: int) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT * FROM server_configurations WHERE server_id = %s", (server_id,))
        result = cursor.fetchone()
        return bool(result)
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operation Error when checking for server config.")
        return True

def add_server_config(server_id: int, moderator_id: int, diffusion_id: int) -> bool:
    try:
        cursor = CONNECTION.cursor()
        if not server_config_exists_in_db(server_id):
            config_copy = DEFAULT_SERVER_CONFIG
            config_copy["MODERATOR_ROLE_ID"] = str(moderator_id)
            config_copy["DIFFUSION_ROLE_ID"] = str(diffusion_id)
            cursor.execute("INSERT INTO server_configurations VALUES (%s, %s)", (server_id, json.dumps(DEFAULT_SERVER_CONFIG)))
            CONNECTION.commit()
            return True
        SYNC_LOGGER.warn("Server already exists in database.")
        return False
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error in adding server config.")
        return False

def get_server_config(server_id: int) -> Optional[dict]:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT config FROM server_configurations WHERE server_id = %s", (server_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when getting server config.")
        return None

def update_server_config(server_id: int, new_config: dict) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute(
            "UPDATE server_configurations SET config = %s WHERE server_id = %s",
            (json.dumps(new_config), server_id)
        )
        CONNECTION.commit()
        return True
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operation Error when updating server config.")
        return False

def is_moderator(server_id: int, member: Member) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT config FROM server_configurations WHERE server_id = %s", (server_id,))
        server_config = cursor.fetchone()
        if server_config is None:
            return False
        server_config = server_config[0]
        SYNC_LOGGER.info(server_config)
        moderator_role_id = server_config["MODERATOR_ROLE_ID"]
        for role in member.roles:
            if role.id == int(moderator_role_id):
                return True
        return False
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when checking if user is moderator.")
        return False

def is_allowed_diffusion(server_id: int, member: Member) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT config FROM server_configurations WHERE server_id = %s", (server_id,))
        server_config = cursor.fetchone()
        if server_config is None:
            return False
        server_config = server_config[0]
        diffusion_role_id = server_config["DIFFUSION_ROLE_ID"]
        for role in member.roles:
            if role.id == int(diffusion_role_id):
                return True
        return False
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when checking if user is allowed to use diffusion commands.")
        return False

#
# User Configuration Functions
#

def user_config_exists_in_db(user_id: int) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT * FROM user_configurations WHERE user_id = %s", (user_id,))
        return bool(cursor.fetchone())
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when getting user config.")
        return False

def add_user_config(user_id: int) -> bool:
    try:
        cursor = CONNECTION.cursor()
        if not user_config_exists_in_db(user_id):
            cursor.execute("INSERT INTO user_configurations VALUES (%s, %s)", (user_id, json.dumps(DEFAULT_USER_CONFIG)))
            CONNECTION.commit()
            return True
        return False
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when adding user config.")
        return False

def get_user_config(user_id: int) -> Optional[dict]:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT * FROM user_configurations WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        return None
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when getting user config.")
        return None

def update_user_config(user_id: int, new_config: dict) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute(
            "UPDATE user_configurations SET config = %s WHERE user_id = %s",
            (json.dumps(new_config), user_id)
        )
        CONNECTION.commit()
        return True
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when updating user config.")
        return False

#
# Punishments Functions
#

def punishment_id_exists(punishment_id: str) -> bool:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("SELECT * FROM punishments WHERE punishment_id = %s", (punishment_id,))
        return bool(cursor.fetchone())
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when checking for Punishment ID")
        return False

def create_punishment(server_id: int, enforcer_id: int, offender_id: int, reason: str, expiry_epoch: int) -> bool:
    try:
        while True:
            punishment_id = str(uuid4())
            if not punishment_id_exists(punishment_id):
                break
        cursor = CONNECTION.cursor()
        cursor.execute(
            "INSERT INTO punishments VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (punishment_id, server_id, enforcer_id, offender_id, reason, int(datetime.now().timestamp()), expiry_epoch)
        )
        CONNECTION.commit()
        return True
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when creating punishment.")
        return False

def get_recent_punishments_for_server(server_id: int) -> Optional[list]:
    try:
        cursor = CONNECTION.cursor()
        cursor.execute(
            "SELECT * FROM punishments WHERE server_id = %s ORDER BY issued_epoch DESC LIMIT 5",
            (server_id,)
        )
        return cursor.fetchall()
    except psycopg.OperationalError:
        SYNC_LOGGER.warn("Operational Error when getting recent punishments for server.")
        return None
