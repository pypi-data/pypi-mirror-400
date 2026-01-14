# SPDX-FileCopyrightText: 2024-present Hayden Swanson <hayden_swanson22@yahoo.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, PackageLoader, select_autoescape
from typing_extensions import Any, Union, Annotated, List, get_origin
from pydantic import Field, TypeAdapter

from matplotlib import use as pltuse
pltuse("agg")

jinja_env = Environment(
    loader=PackageLoader(__name__),
    autoescape=select_autoescape()
)

##########################################################################
import pkgutil
import importlib
import inspect

_test_types_list = []

# Dynamically import all *Type classes from submodules
for _, name, _ in pkgutil.walk_packages(__path__, __name__ + "."):
    try:
        module = importlib.import_module(name)
    except Exception as e:
        continue

    for member_name, member in inspect.getmembers(module):
        if member_name.endswith("Type") and not member_name.startswith("_"):
            if get_origin(member) is Annotated:
                # Add to local namespace to mimic "from ... import ..."
                globals()[member_name] = member
                _test_types_list.append(member)

_test_types = tuple(_test_types_list)
##########################################################################

TestType = Annotated[Union[_test_types], Field(discriminator="name")]
TestModel = TypeAdapter(TestType)
TestArrModel = TypeAdapter(List[TestType])


########### SEQUENCES ############
from etlup.sequences import QuickTestSeqType

SequenceType = Annotated[Union[QuickTestSeqType], Field(discriminator="name")]
SequenceModel = TypeAdapter(SequenceType)

##################################

from .upload import Session, get_model, get_sequence_model, now_utc, localize_datetime

prod_session = Session(prod=True)
staging_session = Session(prod=False)

def _get_all_subclasses(cls):
    """Recursively get all subclasses of a class"""
    subclasses = set(cls.__subclasses__())
    for subclass in list(subclasses):
        subclasses.update(_get_all_subclasses(subclass))
    return subclasses

# Get all ConstructionBaseMixin subclasses
from .base_model import ConstructionBase
Tests = _get_all_subclasses(ConstructionBase)



