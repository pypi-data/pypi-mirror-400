import json
import os
import logging
from datetime import datetime

from .config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    PROJECT_NAME,
    PILLAR_NAME,
    AI_HEALING_APP_TYPE,
    AI_HEALING_DB_ENABLED,
)

logger = logging.getLogger("ai_healing")

try:
    import psycopg2

    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    logger.warning("psycopg2 not found. Database recording disabled.")


class HealingRecorder:
    def __init__(self, record_file="healing_records.json"):
        # Store in the same directory as this file
        self.record_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), record_file
        )
        self.records = self._load_records()
        self.staged_changes = {}

    def _load_records(self):
        """Loads records from the JSON file."""
        if not os.path.exists(self.record_path):
            return {}
        try:
            with open(self.record_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(
                f"Could not decode {self.record_path}, starting with empty records."
            )
            return {}
        except Exception as e:
            logger.error(f"Failed to load records: {e}")
            return {}

    def _save_records(self):
        """Saves records to the JSON file."""
        try:
            with open(self.record_path, "w") as f:
                json.dump(self.records, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save records: {e}")

    def _save_to_db(self, changes, testcase_id, session_id):
        """Saves staged changes to PostgreSQL."""
        if not HAS_POSTGRES or not AI_HEALING_DB_ENABLED:
            return

        conn = None
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
            )
            cur = conn.cursor()

            query = """
                INSERT INTO healing_history 
                (project_name, pillar_name, session_id, testcase_id, original_locator, healed_locator, app_type, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            for key, data in changes.items():
                healed_locator_json = (
                    json.dumps(data["healed_locator"])
                    if isinstance(data["healed_locator"], dict)
                    else str(data["healed_locator"])
                )

                cur.execute(
                    query,
                    (
                        PROJECT_NAME,
                        PILLAR_NAME,
                        session_id or "Unknown",
                        testcase_id or "Unknown",
                        key,  
                        healed_locator_json,  
                        AI_HEALING_APP_TYPE,
                        data["timestamp"],
                    ),
                )

            conn.commit()
            cur.close()
            logger.info(f"Saved {len(changes)} records to database.")

        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
        finally:
            if conn:
                conn.close()

    def _get_from_db(self, original_locator_key):
        """Retrieves the latest healed locator from PostgreSQL."""
        if not HAS_POSTGRES or not AI_HEALING_DB_ENABLED:
            return None

        conn = None
        healed_locator = None
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
            )
            cur = conn.cursor()

            query = """
                SELECT healed_locator 
                FROM healing_history 
                WHERE original_locator = %s AND app_type = %s
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            cur.execute(query, (original_locator_key, AI_HEALING_APP_TYPE))
            row = cur.fetchone()

            if row:
                try:
                    healed_locator = json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    try:
                        import ast

                        healed_locator = ast.literal_eval(row[0])
                    except (ValueError, SyntaxError):
                        healed_locator = row[0]

        except Exception as e:
            logger.error(f"Failed to fetch from DB: {e}")
        finally:
            if conn:
                conn.close()

        return healed_locator

    def get_healed_locator(self, original_locator_key, ignore_json=False):
        """
        Retrieves a healed locator for a given original locator key.
        The key should be a unique representation of the original element (e.g. stringified dict).
        """
        if original_locator_key in self.staged_changes:
            logger.info(f"Checking staged cache for {original_locator_key}: FOUND")
            return self.staged_changes[original_locator_key]["healed_locator"]

        if not ignore_json:
            record = self.records.get(original_locator_key)
            if record:
                logger.info(f"Checking JSON cache for {original_locator_key}: FOUND")
                return record.get("healed_locator")

        db_locator = self._get_from_db(original_locator_key)
        if db_locator:
            logger.info(f"Checking DB cache for {original_locator_key}: FOUND")
            return db_locator

        logger.info(f"Checking cache for {original_locator_key}: MISS")
        return None

    def stage_healed_locator(self, original_locator_key, healed_locator, metadata=None):
        """
        Stages a heal to be saved only if the test passes.
        """
        self.staged_changes[original_locator_key] = {
            "healed_locator": healed_locator,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        logger.info(f"Staged healed locator for {original_locator_key}")

    def commit_staged_changes(self, testcase_id=None, session_id=None):
        """
        Commits all staged changes to the persistent record.
        """
        if not self.staged_changes:
            logger.debug("No staged changes to commit.")
            return

        self.records.update(self.staged_changes)
        self._save_records()
        self._save_to_db(self.staged_changes, testcase_id, session_id)
        logger.info(f"Committed {len(self.staged_changes)} staged healing records.")
        self.staged_changes.clear()

    def discard_staged_changes(self):
        """
        Discards staged changes (e.g. if test failed).
        """
        if self.staged_changes:
            logger.info(
                f"Discarding {len(self.staged_changes)} staged healing records due to test failure/cleanup."
            )
            self.staged_changes.clear()

    def save_healed_locator(self, original_locator_key, healed_locator, metadata=None):
        """
        Directly saves a heal (Legacy/Immediate mode).
        """
        self.stage_healed_locator(original_locator_key, healed_locator, metadata)
        self.commit_staged_changes()
