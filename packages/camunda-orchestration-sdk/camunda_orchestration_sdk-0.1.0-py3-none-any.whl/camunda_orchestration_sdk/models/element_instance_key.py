# Minimal model to satisfy references to ElementInstanceKey in generated code
from pydantic import RootModel, StrictStr


class ElementInstanceKey(RootModel[StrictStr]):
    pass
