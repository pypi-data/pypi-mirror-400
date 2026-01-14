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
"""PPFG Dataset update session command"""
import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_PPFGDATASET_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Update a session, either commit or abandon")
@click.option("-id", "--id", "_id", help="PPFG Dataset id to update", required=True)
@click.option("-s", "--session", "_ses", help="PPFG Dataset session id to update", required=True)
@click.option("-a", "--abandon", "_aba", is_flag=True, help="Abandon session. Will commit session if flag is omitted", required=False)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str, _ses: str, _aba: bool):
    return update_session(state, _id, _ses, _aba)


def update_session(state: State, record_id: str, session_id: str, abandon: bool = False):
    """Update a session, either commit or abandon"""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_PPFGDATASET_PATH)
    response = wellbore_client.update_wbddms_session(record_id, session_id, abandon)
    client.check_status_code(response)
    return response.json()
