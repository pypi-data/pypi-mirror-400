from .enums.StiDatabaseType import StiDatabaseType
from .enums.StiDataType import StiDataType
from .StiFileAdapter import StiFileAdapter


class StiCsvAdapter(StiFileAdapter):
    
### Properties

    version = '2026.1.2'
    """Current version of the data adapter."""

    checkVersion = True
    """Sets the version matching check on the server and client sides."""

    type = StiDatabaseType.CSV
    dataType = StiDataType.CSV
