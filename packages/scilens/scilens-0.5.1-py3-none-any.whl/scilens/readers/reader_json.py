import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.config.models import ReaderJsonConfig,ReaderTreeBaseConfig
from scilens.components.compare_floats import CompareFloats
import json
from.tree import Tree
class ReaderJson(ReaderInterface):
	configuration_type_code='json';category='datalines';extensions=['JSON']
	def read(A,config):C=None;B=config;A.reader_options=B;D=open(A.origin.path,'r',encoding=A.encoding);E=json.load(D);D.close();F=Tree(ReaderTreeBaseConfig(path_include_patterns=B.path_include_patterns if B else C,path_exclude_patterns=B.path_exclude_patterns if B else C));A.floats_data=F.data_to_numeric_values(E);A.metrics=C
	def compare(A,compare_floats,param_reader,param_is_ref=True):C=param_is_ref;B=param_reader;D=A if C else B;E=A if not C else B;Tree.compare(compare_floats,test_floats_data=D.floats_data,ref_floats_data=E.floats_data)
	def class_info(A):return{'metrics':A.metrics}