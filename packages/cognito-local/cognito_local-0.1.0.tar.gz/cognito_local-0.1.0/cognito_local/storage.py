import logging
import os
import pickle

from moto.backends import get_backend

logger = logging.getLogger(__name__)


class StorageManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.backends = {
            "idp": get_backend("cognitoidp"),
            "identity": get_backend("cognitoidentity"),
        }

    def save(self):
        logger.info(f"Saving state to {self.data_file}")
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
            temp_file = f"{self.data_file}.tmp"

            # We dump the dictionary containing both backends
            with open(temp_file, "wb") as f:
                pickle.dump(self.backends, f)  # type: ignore

            os.replace(temp_file, self.data_file)
            logger.info("Save complete.")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load(self):
        if not os.path.exists(self.data_file):
            logger.info("No existing data found. Starting fresh.")
            return

        if os.path.getsize(self.data_file) == 0:
            logger.warning(f"Data file {self.data_file} is empty (corrupt). Skipping.")
            return

        logger.info(f"Loading state from {self.data_file}")
        try:
            with open(self.data_file, "rb") as f:
                data = pickle.load(f)

                # Check format (Backward compatibility check)
                if not isinstance(data, dict) or "idp" not in data:
                    logger.warning("Old database format detected. Migrating.")
                    self.backends["idp"].clear()
                    self.backends["idp"].update(data)
                else:
                    # New format: Load both
                    if "idp" in data:
                        self.backends["idp"].clear()
                        self.backends["idp"].update(data["idp"])

                    if "identity" in data:
                        self.backends["identity"].clear()
                        self.backends["identity"].update(data["identity"])

            logger.info("State loaded successfully (User Pools + Identity Pools).")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
