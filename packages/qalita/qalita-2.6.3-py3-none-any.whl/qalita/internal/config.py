"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import sys
import json
import base64
import yaml

from qalita.internal.utils import logger


class Config(object):

    def __init__(self):
        self.name = ""
        self.mode = ""
        self.token = ""
        self.url = ""
        self.verbose = False
        self.worker_id = None
        self.config = None
        self._qalita_home = os.path.expanduser("~/.qalita")

    @property
    def qalita_home(self):
        if not self._qalita_home:
            self._qalita_home = os.environ.get(
                "QALITA_HOME", os.path.expanduser("~/.qalita")
            )
        return self._qalita_home

    def save_source_config(self):
        config_path = os.path.join(self._qalita_home, "sources-conf.yaml")
        abs_path = os.path.abspath(config_path)

        # Ensure the directory exists before saving the file
        os.makedirs(self._qalita_home, exist_ok=True)

        logger.info(f"Saving source configuration to [{abs_path}]")
        with open(abs_path, "w") as file:
            yaml.dump(self.config, file)

    def load_source_config(self, verbose=True):
        config_path = os.path.join(self._qalita_home, "sources-conf.yaml")
        abs_path = os.path.abspath(config_path)

        try:
            if verbose:
                logger.info(f"Loading source configuration from [{abs_path}]")
            with open(abs_path, "r") as file:
                self.config = yaml.safe_load(file)
                return self.config
        except FileNotFoundError:
            logger.warning(
                f"Configuration file [{abs_path}] not found, creating a new one."
            )
            self.config = {"version": 1, "sources": []}
            self.save_source_config()
            return self.config
        except Exception as e:
            logger.warning(
                f"An unexpected error occurred while loading the configuration [{abs_path}]: {e}"
            )
            self.config = {"version": 1, "sources": []}
            self.save_source_config()
            return self.config

    def get_worker_file_path(self):
        """Get the path for the worker file based on QALITA_HOME env or default."""
        return os.path.join(self._qalita_home, ".worker")

    def get_worker_run_path(self):
        """Get the path for the worker run folder based on QALITA_HOME env or default."""
        return os.path.join(self._qalita_home, "jobs")

    def save_worker_config(self, data):
        """Save the worker config in file to persist between context."""
        worker_file_path = self.get_worker_file_path()

        # Ensure the directory exists before saving the file
        os.makedirs(os.path.dirname(worker_file_path), exist_ok=True)

        with open(worker_file_path, "wb") as file:  # open in binary mode
            json_str = json.dumps(data, indent=4)  # convert to json string
            json_bytes = json_str.encode("utf-8")  # convert to bytes
            base64_bytes = base64.b64encode(json_bytes)  # encode to base64
            file.write(base64_bytes)

    def load_worker_config(self):
        worker_file_path = self.get_worker_file_path()
        try:
            with open(worker_file_path, "rb") as file:  # open in binary mode
                base64_bytes = file.read()  # read base64
                json_bytes = base64.b64decode(base64_bytes)  # decode from base64
                json_str = json_bytes.decode("utf-8")  # convert to string
                return json.loads(json_str)  # parse json
        except FileNotFoundError as exception:
            logger.error(f"Worker can't load data file : {exception}")
            logger.error("Make sure you have logged in before > qalita worker login")
            sys.exit(1)

    # Alias for backward compatibility (agent -> worker refactoring)
    def load_agent_config(self):
        return self.load_worker_config()

    def get_agent_run_path(self):
        return self.get_worker_run_path()

    def set_worker_id(self, worker_id):
        self.worker_id = worker_id

    def json(self):
        data = {
            "name": self.name,
            "mode": self.mode,
            "token": self.token,
            "url": self.url,
            "verbose": self.verbose,
        }
        return data


