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
"""Wellbore Intervalset delete record command"""
import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import (
    WELLBORE_DDMS_WELLBORE_INTERVAL_SET_PATH,
)


# click entry point
@click.command(cls=CustomClickCommand, help="Delete record from wellbore ddms by id. The API performs a soft delete.")
@click.option("-id", "--id", "_id", help="Wellbore Intervalset id to delete", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str):
    return delete_record(state, _id)


def delete_record(state: State, identifier: str):
    """Delete record from wellbore ddms by id. The API performs a soft delete."""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_WELLBORE_INTERVAL_SET_PATH)
    response = wellbore_client.delete_wbddms_record(identifier)
    client.check_status_code(response)
    return response.json()
