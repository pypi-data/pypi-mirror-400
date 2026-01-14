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
"""WellLog send data chunk command"""
import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_WELL_LOG_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Send a data chunk within a session")
@click.option("-id", "--id", "_id", help="WellLog id to append chunk", required=True)
@click.option("-s", "--session", "_ses", help="WellLog session id to append chunk", required=True)
@click.option("-f", "--file", "_file", help="WellLog chunk file to append", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str, _ses: str, _file: str):
    return send_chunk(state, _id, _ses, _file)


def send_chunk(state: State, record_id: str, session_id: str, data_file: str):
    """Send a data chunk within a session"""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_WELL_LOG_PATH)

    with open(data_file, 'rb') as file:
        file_data = file.read()

    response = wellbore_client.add_wbddms_data_chunk(record_id, session_id, file_data)
    client.check_status_code(response)
    return response.json()
