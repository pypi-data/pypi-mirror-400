#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Client for Wellbore DDMS API in the template of osdu-api clients"""

import requests
from osdu_api.auth.authorization import TokenRefresher
from osdu_api.clients.base_client import BaseClient
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.model.http_method import HttpMethod

from osducli.log import get_logger

logger = get_logger(__name__)


class WellboreDdmsClient(BaseClient):
    """
    Client for interacting with Wellbore DDMS
    """

    def __init__(
        self,
        wellbore_ddms_url: str = None,
        config_manager: BaseConfigManager = None,
        provider: str = None,
        data_partition_id: str = None,
        token_refresher: TokenRefresher = None,
        user_id: str = None,
    ):
        super().__init__(
            config_manager,
            provider,
            data_partition_id,
            token_refresher,
            logger,
            user_id,
        )
        self.wellbore_ddms_url = wellbore_ddms_url or self.config_manager.get(
            "environment", "wellbore_ddms_url"
        )

    def get_wbddms_record(self, record_id: str = None) -> requests.Response:
        """Get record from wellbore ddms by id"""
        return self.make_request(
            method=HttpMethod.GET, url=f"{self.wellbore_ddms_url}/{record_id}"
        )

    def get_wbddms_record_versions(self, record_id: str = None) -> requests.Response:
        """Get all versions of the record from wellbore ddms by id"""
        return self.make_request(
            method=HttpMethod.GET, url=f"{self.wellbore_ddms_url}/{record_id}/versions"
        )

    def get_wbddms_record_version(
        self, record_id: str = None, version: str = None
    ) -> requests.Response:
        """Get given version of the record from wellbore ddms by id"""
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/versions/{version}",
        )

    def delete_wbddms_record(self, record_id: str = None) -> requests.Response:
        """Delete record from wellbore ddms by id. The API performs a soft delete."""
        return self.make_request(
            method=HttpMethod.DELETE, url=f"{self.wellbore_ddms_url}/{record_id}"
        )

    def create_wbddms_record(self, record_data_list: str = None) -> requests.Response:
        """Create record with wellbore ddms"""
        return self.make_request(
            method=HttpMethod.POST, url=self.wellbore_ddms_url, data=record_data_list
        )

    def get_wbddms_data(self, record_id: str) -> requests.Response:
        """Get parquet from wellbore ddms"""
        return self.make_request(
            method=HttpMethod.GET, url=f"{self.wellbore_ddms_url}/{record_id}/data"
        )

    def create_wbddms_data(self, record_id: str, data: bytes = "") -> requests.Response:
        """Writes data as a whole bulk, creates a new version"""
        additional_header = {"Content-Type": "application/x-parquet"}
        return self.make_request(
            method=HttpMethod.POST,
            url=f"{self.wellbore_ddms_url}/{record_id}/data",
            add_headers=additional_header,
            data=data,
        )

    def get_wbddms_data_statistics(self, record_id: str, curves: str) -> requests.Response:
        """Get statistics of records data"""
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/data/statistics",
            params={"curves": curves}
        )

    def list_wbddms_session(self, record_id: str) -> requests.Response:
        """List session of the given record"""
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/sessions")

    def create_wbddms_session(self, record_id: str) -> requests.Response:
        """Create a new session on the given record for writing bulk data"""
        return self.make_request(
            method=HttpMethod.POST,
            url=f"{self.wellbore_ddms_url}/{record_id}/sessions"
        )

    def get_wbddms_session(self, record_id: str, session_id: str) -> requests.Response:
        """Get session"""
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/sessions/{session_id}"
        )

    def update_wbddms_session(self, record_id: str, session_id: str, abandon: bool = False) -> requests.Response:
        """Update a session, either commit or abandon"""
        data = {"state": ("abandon" if abandon else "commit")}
        return self.make_request(
            method=HttpMethod.PATCH,
            url=f"{self.wellbore_ddms_url}/{record_id}/sessions/{session_id}",
            data=data
        )

    def add_wbddms_data_chunk(self, record_id: str, session_id: str, data_chunk: bytes) -> requests.Response:
        """Send a data chunk. Session must be completed/commited once all chunks are sent"""
        additional_header = {"Content-Type": "application/x-parquet"}
        return self.make_request(
            method=HttpMethod.POST,
            url=f"{self.wellbore_ddms_url}/{record_id}/sessions/{session_id}/data",
            add_headers=additional_header,
            data=data_chunk
        )

    def get_wbddms_version_data(self, record_id: str, version: str) -> requests.Response:
        """Get data of the specified version"""
        additional_header = {"Content-Type": "application/x-parquet"}
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/versions/{version}/data",
            add_headers = additional_header
        )

    def get_wbddms_version_statistics(self, record_id: str, version: str, curves: str) -> requests.Response:
        """Get statistics of records data for selected version"""
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.wellbore_ddms_url}/{record_id}/versions/{version}/data/statistics",
            params={"curves": curves}
        )

    def compute_wbddms_version_statistics(self, record_id: str, version: str) -> requests.Response:
        """Trigger computations of records data statistics for selected version"""
        return self.make_request(
            method=HttpMethod.POST,
            url=f"{self.wellbore_ddms_url}/{record_id}/versions/{version}/data/statistics"
        )

    def get_log_recognition_family(self, schema: str) -> requests.Response:
        """Find the most probable family and unit using family assignment rule based catalogs.
        User defined catalog will have the priority."""
        return self.make_request(
            method=HttpMethod.POST,
            url=f"{self.wellbore_ddms_url}/family",
            data=schema
        )

    def upload_log_recognition_catalog(self, catalog: str) -> requests.Response:
        """Upload user-defined catalog with family assignment rules.
        If there is an existing catalog, it will be replaced.
        It takes maximum of 5 mins to replace the existing catalog.
        Hence, any call to retrieve the family should be made after 5 mins of uploading the catalog.
        Required roles: 'users.datalake.editors' or 'users.datalake.admins"""
        return self.make_request(
            method=HttpMethod.PUT,
            url=f"{self.wellbore_ddms_url}/upload-catalog",
            data=catalog
        )
