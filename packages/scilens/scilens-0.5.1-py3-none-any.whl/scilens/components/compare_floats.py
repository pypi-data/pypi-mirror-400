_D='amplitude'
_C='diff'
_B=False
_A=None
import logging
from scilens.components.compare_models import SEVERITY_ERROR,SEVERITY_WARNING,CompareGroup,CompareFloatsErr,Compare2ValuesResults
from scilens.components.compare_errors import CompareErrors
from scilens.config.models import CompareFloatThresholdsConfig
from scilens.components.num import vectors as CheckVectors
def vector_get_amplitude(vector):A=vector;B=min(A);C=max(A);return{'min':B,'max':C,_D:abs(C-B)}
class CompareFloats:
	def __init__(A,compare_errors,config):A.compare_errors=compare_errors;A.thresholds=config
	def compare_2_values(G,test,reference):
		D=test;B=reference;A=G.thresholds;F=-1 if D-B<0 else 1
		if abs(D)>A.relative_vs_absolute_min and B!=0:
			C=abs(D-B)/abs(B);E=CompareFloatsErr(is_relative=True,value=F*C,test=D,reference=B)
			if C<A.relative_error_max:
				if C>A.relative_error_min:return Compare2ValuesResults(SEVERITY_WARNING,f"Rel. err. > {A.relative_error_min} and < {A.relative_error_max}",E)
			else:return Compare2ValuesResults(SEVERITY_ERROR,f"Rel. err. > {A.relative_error_max}",E)
		else:
			C=abs(D-B);E=CompareFloatsErr(is_relative=_B,value=F*C,test=D,reference=B)
			if C<A.absolute_error_max:
				if C>A.absolute_error_min:return Compare2ValuesResults(SEVERITY_WARNING,f"Abs. err. > {A.absolute_error_min} and < {A.absolute_error_max}",E)
			else:return Compare2ValuesResults(SEVERITY_ERROR,f"Abs. err. > {A.absolute_error_max}",E)
	def compare_dicts(D,test_dict,reference_dict,group):
		F=group;E=reference_dict;A=test_dict;G=0;B=_B
		if set(A.keys())!=set(E.keys()):raise Exception('Dictionaries have different keys')
		for C in A:
			I=A[C];J=E[C];H=D.compare_2_values(I,J)
			if H:B=D.compare_errors.add(F,H,info={'key':C});G+=1;F.incr(_C)
			if B:break
		return B,G
	def compare_vectors(A,test_vector,reference_vector,group,info_vector=_A):
		R='ignore';M=info_vector;L='RIAE_trapezoid';H=group;F=reference_vector;B=test_vector
		if len(B)!=len(F):raise Exception('Vectors have different lengths')
		N=0;G=_B;E=A.thresholds.vectors.ponderation_method if A.thresholds.vectors else _A
		if E=='RIAE':E=L
		if E:logging.debug(f"Using ponderation method: {E} with reduction_method {A.thresholds.vectors.reduction_method}")
		I=_A
		if A.thresholds.vectors and E=='amplitude_moderation':S=vector_get_amplitude(B)[_D];I=S*A.thresholds.vectors.amplitude_moderation_multiplier;O=A.thresholds.vectors.reduction_method
		J=_A
		if A.thresholds.vectors and E in[L,'RIAE_midpoint']:
			K=CheckVectors.relative_integral_absolute_error_trapezoid(F,B,range(len(B)))if E==L else CheckVectors.relative_integral_absolute_error_midpoint(F,B,range(len(B)))
			if K is _A:logging.warning('RIAE calculation returned None. This may indicate an issue with the vectors.')
			else:
				J=A.thresholds.vectors.reduction_method
				if K>A.thresholds.vectors.riae_threshold:T=CompareFloatsErr(is_relative=_B,value=K);D=Compare2ValuesResults(SEVERITY_ERROR,f"RIAE ({E}) > {A.thresholds.vectors.riae_threshold}",T);G=A.compare_errors.add(H,D)
		U=len(B)
		for C in range(U):
			if B[C]is _A and F[C]is _A:continue
			P=B[C]-F[C]
			if P==0:continue
			else:N+=1;H.incr(_C)
			if G:continue
			if J==R:continue
			if I is not _A and abs(P)<I:
				if O==R:continue
				elif O=='soften':
					D=A.compare_2_values(B[C],F[C])
					if D:D.severity=SEVERITY_WARNING
			else:
				D=A.compare_2_values(B[C],F[C])
				if D and J:D.severity=SEVERITY_WARNING
			if D:
				Q={'index':C}
				if M:Q['info']=M[C]
				G=A.compare_errors.add(H,D,info=Q)
		return G,N
	def add_group_and_compare_vectors(A,group_name,parent_group,group_data,test_vector,reference_vector,info_vector=_A):C,B=A.compare_errors.add_group('vectors',group_name,parent=parent_group,data=group_data);return(B,)+A.compare_vectors(test_vector,reference_vector,B,info_vector=info_vector)
	def compare_matrices(H,test_mat,ref_mat,group,x_vector=_A,y_vector=_A):
		K=y_vector;J=x_vector;I=group;D=ref_mat;C=test_mat;L=0;E=_B;F=len(C);M=len(C[0])if F>0 else 0;N=len(D);P=len(D[0])if N>0 else 0
		if F!=N or M!=P:raise Exception('Matrices have different dimensions')
		for A in range(F):
			for B in range(M):
				Q=C[A][B]-D[A][B]
				if Q==0:continue
				else:L+=1;I.incr(_C)
				if E:continue
				O=H.compare_2_values(C[A][B],D[A][B])
				if O:
					G={'i':A+1,'j':B+1}
					if J:G['x']=J[B]
					if K:G['y']=K[A]
					E=H.compare_errors.add(I,O,info=G)
		return E,L
	def add_group_and_compare_matrices(A,group_name,parent_group,group_data,test_mat,ref_mat,x_vector=_A,y_vector=_A):C,B=A.compare_errors.add_group('matrix',group_name,parent=parent_group,data=group_data);return(B,)+A.compare_matrices(test_mat,ref_mat,B,x_vector=x_vector,y_vector=y_vector)