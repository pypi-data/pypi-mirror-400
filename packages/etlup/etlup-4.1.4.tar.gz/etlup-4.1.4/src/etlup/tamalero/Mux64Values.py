from pydantic import ConfigDict, Field
from .. import base_model as bm
from typing_extensions import Literal, Annotated, Union, List, Tuple

class Mux64ValuesV0(bm.ConstructionBase):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "version": "v0",
                "name": "mux64_values",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                "mux64_all_passed": True,
                "mux64_values": [1000] * 64,
                "mux64_checks": [True] * 64,
                "mux64_bad_pin_val_pairs": []
            },
        ],
        'table': 'test',
        'component_types': [],
        'module_types': ['Production', 'PreProduction', 'Digital', 'Prototype'],
        'description': 'Mux64 values check.'
    })
    name: Literal['mux64_values'] = 'mux64_values'
    version: Literal["v0"] = "v0"
    
    mux64_all_passed: bool
    mux64_values: List[Union[int, float]]
    mux64_checks: List[bool]
    mux64_bad_pin_val_pairs: List[Tuple[int, float]]


    def plot(self):
        ...

    def html_display(self):
        status_class = "text-success" if self.mux64_all_passed else "text-danger"
        status_text = "PASSED" if self.mux64_all_passed else "FAILED"
        
        html = f"""
        <div class="container-fluid">
            <h4 class="mb-3">Mux64 Test Status: <span class="{status_class} fw-bold">{status_text}</span></h4>
        """

        if self.mux64_bad_pin_val_pairs:
             html += f"""
            <div class="alert alert-danger" role="alert">
                <h5 class="alert-heading">Failures Detected:</h5>
                <ul class="mb-0">
            """
             for pin, val in self.mux64_bad_pin_val_pairs:
                 html += f"<li>Pin <strong>{pin}</strong>: {val}</li>"
             html += """
                </ul>
            </div>
            """

        html += """
            <details>
                <summary class="btn btn-outline-secondary btn-sm mb-2">View all 64 channel values</summary>
                <div class="table-responsive">
                    <table class="table table-striped table-hover table-sm">
                        <thead class="table-light">
                            <tr>
                                <th>Pin</th>
                                <th>Value</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for i, (val, check) in enumerate(zip(self.mux64_values, self.mux64_checks)):
            row_class = 'table-danger text-danger fw-bold' if not check else ""
            status_badge = '<span class="badge bg-danger">FAIL</span>' if not check else '<span class="badge bg-success">OK</span>'
            html += f"""
                        <tr class="{row_class}">
                            <td>{i}</td>
                            <td>{val}</td>
                            <td>{status_badge}</td>
                        </tr>
            """
            
        html += """
                        </tbody>
                    </table>
                </div>
            </details>
        </div>
        """
        return html

Mux64ValuesType = Annotated[Union[Mux64ValuesV0], Field(discriminator="version")]
