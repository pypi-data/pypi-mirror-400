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
"""Upload user-defined catalog with family assignment rules for specific partition ID.
If there is an existing catalog, it will be replaced. It takes maximum of 5 mins to replace
the existing catalog. Hence, any call to retrieve the family should be made after 5 mins
of uploading the catalog.
Required roles: 'users.datalake.editors' or 'users.datalake.admins"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_LOG_RECOGNITION_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Upload user-defined catalog with family assignment rules.")
@click.option("-d", "--data", "_data", help="Catalog data", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _data: str):
    return upload_catalog(state, _data)


def upload_catalog(state: State, data: str):
    """Upload user-defined catalog with family assignment rules."""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_LOG_RECOGNITION_PATH)
    response = wellbore_client.upload_log_recognition_catalog(data)
    client.check_status_code(response)
    return response.json()
