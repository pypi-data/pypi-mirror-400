_A=None
import logging,re
from itertools import islice
from dataclasses import dataclass
from scilens.readers.transform import string_2_float
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.cols_dataset import ColsDataset,ColsCurves,compare
from scilens.config.models import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_cols import ReaderCurveParserNameConfig
from scilens.components.compare_floats import CompareFloats
@dataclass
class ParsedHeaders:raw:str;cleaned:str;data:list[str];ori_line_idx:int|_A=_A
class ReaderTxtFixedCols(ReaderInterface):
	configuration_type_code='txt_fixed_cols';category='datalines';extensions=[]
	def _ignore_line(A,line):
		if not line.strip():return True
		if A.ignore_lines_patterns:
			for B in A.ignore_lines_patterns:
				if bool(re.match(B,line)):return True
		return False
	def _get_parsed_headers(A,path):
		B=A.reader_options;C=_A
		with open(A.origin.path,'r',encoding=A.encoding)as G:
			D=-1
			if B.has_header_line is not _A:
				for E in G:
					D+=1
					if D+1==B.has_header_line:C=E;break
			else:
				for E in G:
					D+=1
					if not A._ignore_line(E):C=E;break
		if C:
			H=C.strip();F=H
			if B.has_header_ignore:
				for I in B.has_header_ignore:F=F.replace(I,'')
			return ParsedHeaders(raw=H,cleaned=F,data=F.split(),ori_line_idx=D)
	def _get_first_data_line(A,path):
		D=A.reader_options;B=D.has_header
		with open(A.origin.path,'r',encoding=A.encoding)as E:
			for C in E:
				if not A._ignore_line(C):
					if B:B=False;continue
					else:return C
	def _discover_col_idx_ralgin_spaces(G,line):
		A=line;A=A.rstrip();C=[];D=_A;B=0
		for(E,F)in enumerate(A):
			if D is not _A and D!=' 'and F==' ':C.append((B,E));B=E
			D=F
		if B<len(A):C.append((B,len(A)))
		return C
	def _derive_col_indexes(A,header_row=_A):0
	def read(A,reader_options):
		C=reader_options;A.reader_options=C;A.ignore_lines_patterns=_A;I=_A;M=_A;B=C.cols
		if B:
			if B.rows:A.ignore_lines_patterns=B.rows.ignore_patterns;I=B.rows.line_start;M=B.rows.line_end
		G=A._get_parsed_headers(A.origin.path)if C.has_header else _A;N=open(A.origin.path,'r',encoding=A.encoding);E=[]
		if C.column_indexes or C.column_widths:
			if C.column_indexes and C.column_widths:raise Exception('column_indexes and column_widths are exclusive.')
			if C.column_widths:
				logging.debug(f"Using column widths: {C.column_widths}");J=0
				for O in C.column_widths:E+=[(J,J+O)];J+=O
			else:logging.debug(f"Using column indexes: {C.column_indexes}");E=C.column_indexes
		else:logging.debug(f"Using auto derived column indexes.");S=A._get_first_data_line(A.origin.path);E=A._discover_col_idx_ralgin_spaces(S)
		logging.debug(f"Column indexes: {E}")
		if not E:raise Exception('No column indexes or widths provided, and no headers found to derive column indexes.')
		H=len(E);D=ColsDataset(cols_count=H,names=[f"Column {A+1}"for A in range(H)],numeric_col_indexes=[A for A in range(H)],data=[[]for A in range(H)])
		if G:D.names=G.data
		if B and B.ignore_columns:
			if isinstance(B.ignore_columns[0],str):D.numeric_col_indexes=[A for A in D.numeric_col_indexes if D.names[A]not in B.ignore_columns]
			if isinstance(B.ignore_columns[0],int):T=[A-1 for A in B.ignore_columns];D.numeric_col_indexes=[A for A in D.numeric_col_indexes if A not in T]
		if B and B.select_columns:
			if isinstance(B.select_columns[0],str):D.numeric_col_indexes=[A for A in D.numeric_col_indexes if D.names[A]in B.select_columns]
			if isinstance(B.select_columns[0],int):U=[A-1 for A in B.select_columns];D.numeric_col_indexes=[A for A in D.numeric_col_indexes if A in U]
		F=I or 0
		for P in islice(N,I,M):
			F+=1
			if A._ignore_line(P):continue
			if G:
				if G.ori_line_idx==F-1:continue
			for(K,Q)in enumerate(E):
				L=P[Q[0]:Q[1]].strip();R=string_2_float(L)
				if R is _A:
					if not B.nulls_allowed:raise Exception(f"line_nb {F} col_index {K} value is empty not allowed, or not a float")
					elif L and B.nulls_strings:
						if L not in B.nulls_strings:raise Exception(f"line_nb {F} col_index {K} value is not a float")
				D.data[K].append(R)
			D.origin_line_nb.append(F)
		D.rows_count=len(D.origin_line_nb);N.close();A.cols_dataset=D;A.raw_lines_number=F;A.metrics=_A
		if C.metrics:A.metrics=D.compute_metrics(C.metrics)
		A.curves=_A;A.cols_curve=_A
		if C.cols and C.cols.curve_parser:
			if C.cols.curve_parser.name==ReaderCurveParserNameConfig.COL_X:
				A.curves,V=D.get_curves_col_x(C.cols.curve_parser.parameters.x)
				if A.curves:A.cols_curve=ColsCurves(type=ReaderCurveParserNameConfig.COL_X,info=V,curves=A.curves)
			elif C.cols.curve_parser.name==ReaderCurveParserNameConfig.COLS_COUPLE:raise NotImplementedError('cols_couple not implemented')
			else:raise Exception('Curve parser not supported.')
	def compare(A,compare_floats,param_reader,param_is_ref=True):D=param_is_ref;C=param_reader;B=compare_floats;E=A.cols_dataset if D else C.cols_dataset;F=A.cols_dataset if not D else C.cols_dataset;G=A.cols_curve;I,H=B.compare_errors.add_group('node','txt cols');return compare(H,B,E,F,G)
	def class_info(A):return{'cols':A.cols_dataset.names,'raw_lines_number':A.raw_lines_number,'curves':A.curves,'metrics':A.metrics}