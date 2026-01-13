_B=None
_A='forbid'
from pydantic import BaseModel,Field
class ReaderTreeBaseConfig(BaseModel,extra=_A):path_exclude_patterns:list[str]|_B=Field(default=_B,description='Patterns (Unix shell-style wildcards) to exclude certain paths from processing.');path_include_patterns:list[str]|_B=Field(default=_B,description='Patterns (Unix shell-style wildcards) to include certain paths from processing.')
class ReaderJsonConfig(ReaderTreeBaseConfig,extra=_A):0
class ReaderXmlConfig(ReaderTreeBaseConfig,extra=_A):0
class ReaderYamlConfig(ReaderTreeBaseConfig,extra=_A):0