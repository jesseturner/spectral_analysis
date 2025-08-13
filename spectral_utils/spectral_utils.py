import pandas as pd
import re
from io import StringIO


#--- MODTRAN utils
def open_tp7_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    #--- Find the header line index
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("FREQ"):
            header_idx = i
            break
    
    if header_idx is None:
        raise ValueError("No header line starting with 'FREQ' found.")
    
    headers = lines[header_idx].split()
    lines = lines[header_idx+1:]
    

    processed_lines = []
    for line in lines[:50]:

        line = line.rstrip("\n")
        line = line.lstrip()
        line_og = line

        line = line_og[:50] + "  " + line_og[72:83] + " " + line_og[94:105] + "  " + line_og[124:138] + " " + line_og[152:]
        
        line = re.sub(" ", "|", line)
        processed_lines.append(line)
        print(line)

    df = pd.read_csv(
        StringIO("\n".join(processed_lines)),
        sep='|',
        engine='python',
        on_bad_lines="warn",
        names=headers, 
        header=None
    )
        
    return df