_B=False
_A=None
import logging,fnmatch
from scilens.components.compare_floats import CompareFloats
from scilens.components.compare_models import SEVERITY_ERROR,Compare2ValuesResults
from scilens.config.models.reader_format_trees import ReaderTreeBaseConfig
NumericPathValues=list[tuple[str,float]]
def find_numeric_values_and_keys(k,v):
	A=[]
	if isinstance(v,dict):
		for(B,C)in v.items():A.extend(find_numeric_values_and_keys(f"{k}/{B}",C))
	elif isinstance(v,list):
		for(B,C)in enumerate(v):A.extend(find_numeric_values_and_keys(f"{k}[{B}]",C))
	elif isinstance(v,(int,float)):A.append((k,v))
	elif isinstance(v,str):
		try:D=float(v);A.append((k,D))
		except ValueError:pass
	return A
def find_numeric_values(v):
	A=[]
	if isinstance(v,dict):
		for B in v.values():A.extend(find_numeric_values(B))
	elif isinstance(v,list):
		for C in v:A.extend(find_numeric_values(C))
	elif isinstance(v,(int,float)):A.append(v)
	elif isinstance(v,str):
		try:D=float(v);A.append(D)
		except ValueError:pass
	return A
def filter_numeric_values_by_patterns(numeric_values_with_keys,include_patterns=_A,exclude_patterns=_A):
	E=exclude_patterns;D=include_patterns;F=[]
	for(B,G)in numeric_values_with_keys:
		A=True
		if E:
			for C in E:
				if fnmatch.fnmatch(B,C):A=_B;break
		if A and D:
			A=_B
			for C in D:
				if fnmatch.fnmatch(B,C):A=True;break
		if A:F.append((B,G))
	return F
class Tree:
	def __init__(A,config):A.config=config
	def data_to_numeric_values(D,data):
		E=D.config.path_include_patterns;F=D.config.path_exclude_patterns;logging.debug(f"Extracting numeric values from tree data");A=find_numeric_values_and_keys('',data);logging.debug(f"Found {len(A)} numeric values in tree data, 10 first:")
		for(B,C)in A[:10]:logging.debug(f"  {B}: {C}")
		if E or F:
			logging.debug(f"Applying include/exclude patterns");A=filter_numeric_values_by_patterns(A,include_patterns=E,exclude_patterns=F);logging.debug(f"After filtering, {len(A)} numeric values remain, 10 first:")
			for(B,C)in A[:10]:logging.debug(f"  {B}: {C}")
		return A
	@classmethod
	def compare(V,compare_floats,test_floats_data,ref_floats_data):
		Q='diff';P='tree';C=ref_floats_data;B=test_floats_data;A=compare_floats;R,S=A.compare_errors.add_group('node','json');R,D=A.compare_errors.add_group(P,P,parent=S);B=sorted(B,key=lambda x:x[0]);C=sorted(C,key=lambda x:x[0]);E=_B;K=len(B);L=len(C);T=max(K,L);F=0;G=0
		for W in range(T):
			H,M=B[F]if F<K else(_A,_A);J,N=C[G]if G<L else(_A,_A)
			if H!=J:
				D.incr(Q)
				if not E:
					if J>H:F+=1;I=f"Test: {H}"
					else:G+=1;I=f"Ref.: {J}"
					E=A.compare_errors.add(D,Compare2ValuesResults(SEVERITY_ERROR,'Different keys for numeric values'),info=I)
				continue
			F+=1;G+=1;I=H;U=M-N
			if U==0:continue
			else:
				D.incr(Q)
				if not E:
					O=A.compare_2_values(M,N)
					if O:E=A.compare_errors.add(D,O,info=I)