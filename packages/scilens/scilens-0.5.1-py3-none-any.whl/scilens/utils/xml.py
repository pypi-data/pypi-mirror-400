import xml.etree.ElementTree as ET
def etree_to_dict(t):
	C={t.tag:{}if t.attrib else None};D=list(t)
	if D:
		A={}
		for G in map(etree_to_dict,D):
			for(B,E)in G.items():
				if B in A:
					if isinstance(A[B],list):A[B].append(E)
					else:A[B]=[A[B],E]
				else:A[B]=E
		C={t.tag:A}
	if t.attrib:C[t.tag].update(('@'+A,B)for(A,B)in t.attrib.items())
	if t.text:
		F=t.text.strip()
		if D or t.attrib:
			if F:C[t.tag]['#text']=F
		else:C[t.tag]=F
	return C