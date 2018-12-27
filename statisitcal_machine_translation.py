import ibmmodel1
from get_data import get_data_from_directory

transcripts = get_data_from_directory("/transcripts_var_replaced/")
pseudocode = get_data_from_directory("/pseudocode_simplified/")
pairs = [x for x in zip(transcripts,pseudocode)]

ibmmodel1.train(pairs,2)
