from pydantic import ConfigDict, Field, AliasChoices
import numpy as np
from ..  import base_model as bm
from typing_extensions import Literal, Annotated, Union

class ReadoutBoardCommunicationV0(bm.ConstructionBase):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "version": "v0",
                "name": "readout_board_communication",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "master_lpgbt_read": True,
                "master_lpgbt_write": True,
                "mux64_read": True,
                "mux64_write": False,
                "servant_lpgbt_read": False,
                "servant_lpgbt_write": False
            },   
        ],
        'table': 'test',
        'component_types': [],
        'module_types': ['Production', 'PreProduction', 'Digital', 'Prototype', 'Fake Production'],
        'description': 'Checks the ability of read and write to the Master lpGBT, MUX64 and the Servant lpGBT on the RB.'
    })
    name: Literal['readout_board_communication'] = 'readout_board_communication'
    version: Literal["v0"] = "v0"
    module: str

    master_lpgbt_read: bool
    master_lpgbt_write: bool
    mux64_read: bool
    mux64_write: bool
    servant_lpgbt_read: bool
    servant_lpgbt_write: bool

    def plot(self):
        """Plot"""
        ...
    
    def html_display(self):
        return f"""
        <table class="table table-striped">
            <thead>
                <tr>
                    <th scope="col">Chip</th>
                    <th scope="col">Read</th>
                    <th scope="col">Write</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Master lpGBT</td>
                    <td>{self.master_lpgbt_read}</td>
                    <td>{self.master_lpgbt_write}</td>
                </tr>
                <tr>
                    <td>MUX64</td>
                    <td>{self.mux64_read}</td>
                    <td>{self.mux64_write}</td>
                </tr>
                <tr>
                    <td>Servant lpGBT</td>
                    <td>{self.servant_lpgbt_read}</td>
                    <td>{self.servant_lpgbt_write}</td>
                </tr>
            </tbody>
        </table>
        """

ReadoutBoardCommunicationType = Annotated[Union[ReadoutBoardCommunicationV0], Field(discriminator="version")]