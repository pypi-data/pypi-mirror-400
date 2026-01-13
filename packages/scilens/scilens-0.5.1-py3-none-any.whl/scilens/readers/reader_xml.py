import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.config.models import ReaderXmlConfig,ReaderTreeBaseConfig
from scilens.components.compare_floats import CompareFloats
from.tree import Tree
from scilens.utils.xml import etree_to_dict
import xml.etree.ElementTree as ET
class ReaderXml(ReaderInterface):
	configuration_type_code='xml';category='datalines';extensions=['XML']
	def read(A,config):D=None;B=config;A.reader_options=B;E=open(A.origin.path,'r',encoding=A.encoding);C=ET.parse(E);F=C.getroot();G=etree_to_dict(F);E.close();C=Tree(ReaderTreeBaseConfig(path_include_patterns=B.path_include_patterns if B else D,path_exclude_patterns=B.path_exclude_patterns if B else D));A.floats_data=C.data_to_numeric_values(G);A.metrics=D
	def compare(A,compare_floats,param_reader,param_is_ref=True):C=param_is_ref;B=param_reader;D=A if C else B;E=A if not C else B;Tree.compare(compare_floats,test_floats_data=D.floats_data,ref_floats_data=E.floats_data)
	def class_info(A):return{'metrics':A.metrics}