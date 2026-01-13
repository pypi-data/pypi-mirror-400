def get_strong_binding_RVDs(gspec=False):
    strong_binding_RVDs = {"A": "NI", "C": "HD", "G": "NN", "T": "NG"}
    if gspec:
        strong_binding_RVDs["G"] = "NH"
    return strong_binding_RVDs


def get_RVD_seq(sequence, gspec=False):
    strong_binding_RVDs = get_strong_binding_RVDs(gspec)
    RVD_seq = ""
    sequence = sequence.upper()
    for i in range(len(sequence)):
        if sequence[i] not in strong_binding_RVDs:
            return None
        RVD_seq += strong_binding_RVDs[sequence[i]]
    return RVD_seq
