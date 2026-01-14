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

"""Storage service version list command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-id", "--id", "_id", help="Record id to search for", required=True)
@handle_cli_exceptions
@command_with_output("versions")
def _click_command(state: State, _id: str):
    """Get record versions for given id"""
    return get(state, _id)


def get(state: State, id: str): # pylint: disable=redefined-builtin
    """Get record versions for given id

    Args:
        state (State): Global state
        id (str): Id of records
    """
    client = CliOsduClient(state.config)
    record_client = client.get_storage_record_client()
    response = record_client.get_record_versions(id)

    client.check_status_code(response)
    return response.json()
