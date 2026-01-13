_A=None
import os,sys
from importlib.metadata import entry_points
from scilens.readers.exceptions import NoReaderFound
from scilens.readers.reader_interface import ReaderOrigin
from scilens.config.models import FileReaderConfig
from scilens.config.models.readers import ReadersConfig
def extension_format(extension):
	A=extension
	if A.startswith('.'):A=A[1:]
	return A.upper()
from scilens.readers.reader_txt import ReaderTxt
from scilens.readers.reader_csv import ReaderCsv
from scilens.readers.reader_txt_fixed_cols import ReaderTxtFixedCols
from scilens.readers.reader_json import ReaderJson
from scilens.readers.reader_yaml import ReaderYaml
from scilens.readers.reader_xml import ReaderXml
BUILTIN_PLUGINS=[ReaderTxt,ReaderCsv,ReaderTxtFixedCols,ReaderJson,ReaderYaml,ReaderXml]
LIB_PLUGINS_ENTRY_POINT='scilens.reader_plugins'
class ReaderManager:
	def __init__(A):
		A.plugins=[]+BUILTIN_PLUGINS;B=entry_points(group=LIB_PLUGINS_ENTRY_POINT)if sys.version_info.minor>=12 else entry_points().get(LIB_PLUGINS_ENTRY_POINT,[])
		for C in B:A.plugins+=C.load()()
	def _get_plugin_names(A):return[A.__name__ for A in A.plugins]
	def _get_plugin_info(A):return[{'class':A.__name__,'configuration_type_code':A.configuration_type_code}for A in A.plugins]
	def __str__(A):return f"plugins: {A._get_plugin_names()}"
	def _get_reader_from_extension(B,extension):
		for A in B.plugins:
			if extension_format(extension)in A.extensions:return A
	def _get_reader_from_configuration_type_code(B,code):
		for A in B.plugins:
			if code==A.configuration_type_code:return A
	def get_reader_from_file(F,path,name='',config=_A,readers_config=_A,curve_parser=_A):
		I=curve_parser;G=path;C=readers_config;B=config;J=ReaderOrigin(type='file',path=G,short_name=os.path.basename(G));K=B.encoding if B else'utf-8';Q,E=os.path.splitext(G);E=extension_format(E)
		if B and B.extension_readers_catalog:
			for(M,L)in B.extension_readers_catalog.items():
				if extension_format(M)==E:
					if not C.catalog or L not in C.catalog.keys():raise NoReaderFound(f"Reader config not found for {E}")
					H=C.catalog[L];A=F._get_reader_from_configuration_type_code(H.type)
					if not A:raise Exception(f"Reader not found for contiguration type code {H.type}")
					N=H.parameters;return A(J,name=name,encoding=K,curve_parser=I),N
		if B and B.extension_mapping:
			for(O,P)in B.extension_mapping.items():
				if extension_format(O)==E:E=extension_format(P);break
		A=F._get_reader_from_extension(E)
		if not A and B and B.extension_fallback:A=F._get_reader_from_extension(B.extension_fallback)
		if not A:raise NoReaderFound(f"Reader cound not be derived")
		D=_A
		if A.__name__=='ReaderTxt':D=C.txt
		elif A.__name__=='ReaderCsv':D=C.csv
		elif A.__name__=='ReaderTxtFixedCols':D=C.txt_fixed_cols
		elif A.__name__=='ReaderJson':D=C.default_config_json
		elif A.__name__=='ReaderXml':D=C.default_config_xml
		elif A.__name__=='ReaderYaml':D=C.default_config_yaml
		elif A.__name__=='ReaderNetcdf':D=C.netcdf
		return A(J,name=name,encoding=K,curve_parser=I),D