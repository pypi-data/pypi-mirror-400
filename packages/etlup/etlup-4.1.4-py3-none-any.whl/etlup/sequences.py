from typing import List
import re
from pydantic import BaseModel, AwareDatetime, PastDatetime, computed_field, field_validator, Field
from typing_extensions import Union, Literal, Annotated, Tuple
from etlup import TestType

class BaseSequence(BaseModel):
    register_location: str
    git_commit: str
    start_time: Union[PastDatetime, AwareDatetime]
    end_time: Union[PastDatetime, AwareDatetime]
    sequence: Tuple[TestType]
    name: str
    version: str

    @field_validator('*')
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == '':
            return None
        return v

    @field_validator('sequence')
    @classmethod
    def validate_sequence_length(cls, v: Tuple[TestType]) -> Tuple[TestType]:
        if len(v) < 2:
            raise ValueError('Sequence must have more than 1 item')
        return v

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not re.match(r'^v\d+$', v):
            raise ValueError('Version must be in the format "v<integer>" (e.g., "v0", "v1")')
        return v

    @computed_field
    @property
    def module(self) -> str:
        modules = {test.module for test in self.sequence}
        if len(modules) !=  1:
            raise ValueError(f"All tests in the sequence must belong to the same module. Found: {modules}")
        return list(modules)[0]

    def report(self):
        raise NotImplementedError("Not implemented for this sequence...")

###############################################################################
 
from etlup.tamalero.ReadoutBoardCommunication import ReadoutBoardCommunicationV0
from etlup.tamalero.Mux64Values import Mux64ValuesV0

############### READ THIS NOTE #################
#### IF YOU CHANGE ANY VALUE IN QUICK TEST #####
####### MAKE NEW CLASS AND BUMP VERSION ########
################################################

class QuickTestSeqV0(BaseSequence):
    name: Literal["quick_test_sequence"] = "quick_test_sequence"
    version: Literal["v0"] = "v0"
    sequence: Tuple[ReadoutBoardCommunicationV0, Mux64ValuesV0]

    def report(self):
        ...

QuickTestSeqType = Annotated[Union[QuickTestSeqV0], Field(discriminator="version")]

###############################################################################
