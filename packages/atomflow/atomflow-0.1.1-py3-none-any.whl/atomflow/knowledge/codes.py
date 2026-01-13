AA_RES_TO_SYM = {
    "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
    "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L",
    "MET": "M", "ASN": "N", "PRO": "P", "GLN": "Q", "ARG": "R",
    "SER": "S", "THR": "T", "VAL": "V", "TRP": "W", "TYR": "Y",
    "UNK": "X"
}

AA_SYM_TO_RES = {v: k for k, v in AA_RES_TO_SYM.items()}

AA_ONE_LETTER_CODES = set(AA_SYM_TO_RES)

DNA_RES_TO_SYM = {
    "DA": "A", "DG": "G", "DT": "T", "DC": "C"
}

DNA_SYM_TO_RES = {v: k for k, v in DNA_RES_TO_SYM.items()}

DNA_ONE_LETTER_CODES = set(DNA_SYM_TO_RES)

RNA_RES_CODES = {"A", "G", "U", "C"}