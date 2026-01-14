import json
from typing import List

import requests

from airflow_commons.internal.mixpanel.auth import Connection
from airflow_commons.internal.mixpanel.constants import (
    ENGAGE_API_URL,
    ENGAGE_BATCH_SIZE,
    IMPORT_API_URL,
    REPLACE_LOOKUP_TABLE,
    GET_LOOKUP_TABLES,
)
from airflow_commons.internal.mixpanel.defaults import TIMEOUT


class ServiceAccount(object):
    def __init__(self, username, secret):
        self.username = username
        self.secret = secret


class MixpanelOperator(object):
    def __init__(
        self,
        project_id: str = None,
        service_account_name: str = None,
        service_account_secret: str = None,
        access_token: str = None,
        timeout: int = TIMEOUT,
    ):
        self.session = requests.Session()
        self.project_id = project_id
        self.connection = Connection(
            service_account_name=service_account_name,
            service_account_secret=service_account_secret,
            access_token=access_token,
        )
        self.timeout = timeout

    def engage(self, values: List[dict]):
        """
        Updates profiles using engage API.
        :param values: List of profile updates. Must include $distinct_id and $set values. $set involves all profile parameters with their updated values.
        :return:
        """
        token = self.connection.get_access_token()
        for value in values:
            value["$token"] = token
        batches = [
            values[i : i + ENGAGE_BATCH_SIZE]
            for i in range(0, len(values), ENGAGE_BATCH_SIZE)
        ]
        for batch in batches:
            request = requests.Request(
                "POST",
                ENGAGE_API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(batch),
            )
            response = self._send_request(request)
            response.raise_for_status()

    def import_events(self, values: List[dict]):
        """
        Imports batch of values to Mixpanel.
        :param values: List of events to be sent. Each value should have keys event(str) and properties(dict).
        :return: Import API response.
        """
        url = IMPORT_API_URL.format(project_id=self.project_id)
        request = requests.Request(
            "POST",
            url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            auth=self.connection.get_service_account_credentials(),
            data=json.dumps(values),
        )
        response = self._send_request(request)
        response.raise_for_status()
        return response

    def list_lookup_tables(self):
        """
        Lists available lookup tables in the project.
        :return: List of lookup table ids and names.
        """
        url = GET_LOOKUP_TABLES.format(project_id=self.project_id)
        request = requests.Request(
            "GET",
            url,
            headers={"Accept": "application/json"},
            auth=self.connection.get_service_account_credentials(),
        )
        response = self._send_request(request)
        response.raise_for_status()
        response_json = response.json()
        return response_json["results"]

    def replace_lookup_table(self, table_id: str, data: str):
        """
        Replaces existing lookup table with new data.
        :param table_id: Target lookup table id.
        :param data: Csv content of new data. First row must always be the header row. Also, first column is the id column.
        :return: Lookup API response.
        """
        url = REPLACE_LOOKUP_TABLE.format(table_id=table_id, project_id=self.project_id)
        request = requests.Request(
            "PUT",
            url,
            headers={"Accept": "application/json", "Content-Type": "text/csv"},
            auth=self.connection.get_service_account_credentials(),
            data=data,
        )
        response = self._send_request(request)
        response.raise_for_status()
        return response

    def _send_request(self, request: requests.Request):
        prep = request.prepare()
        return self.session.send(prep, timeout=self.timeout)
