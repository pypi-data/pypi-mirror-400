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
"""Wellbore Trajectory get data command"""
import os

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_TRAJECTORY_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Get Wellbore Trajectory data by id")
@click.option("-id", "--id", "_id", help="Wellbore Trajectory id to search for", required=True)
@click.option("-f", "--file", "_file", help="File to save Wellbore Trajectory data", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str, _file: str):
    return get_data(state, _id, _file)


def get_data(state: State, record_id: str, out_file: str):
    """Get Wellbore Trajectory data by id"""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_TRAJECTORY_PATH)
    response = wellbore_client.get_wbddms_data(record_id)
    client.check_status_code(response)

    with open(out_file, 'wb') as file:
        file.write(response.content)

    filename = os.path.abspath(file.name)
    print("File created: ", filename)
    return filename
