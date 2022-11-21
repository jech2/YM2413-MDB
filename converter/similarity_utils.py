import numpy as np

INF = 987654321

TICKS_PER_SEC = 44100 # 735 * 60

def onset_similarity(seq1, seq2):
    min_len = min(len(seq1),len(seq2))
    if min_len == len(seq1):
        pivot = seq1
    else:
        pivot = seq2
    diffs = []
    # naive approach
    for i in range(min_len):
        diffs.append((seq1[i]-seq2[i]))
    diffs = np.array(diffs)
    return diffs.mean()

def pitch_similarity(seq1, seq2):
    min_len = min(len(seq1),len(seq2))
    if min_len == len(seq1):
        pivot = seq1
    else:
        pivot = seq2
    cnt = 0
    # naive approach
    for i in range(min_len):
        if seq1[i] == seq2[i]:
            cnt += 1
    return float(cnt) / float(min_len)

def cross_correlation(seq1, seq2):
    one_is_short = False
    
    if len(seq1) < len(seq2):
        one_is_short = True
    min_len = min(len(seq1),len(seq2))
    max_len = max(len(seq1),len(seq2))
    
    diffs = []
    for i in range(max_len - min_len + 1):
        diff_sum = 0
        for j in range(min_len):
            if one_is_short:
                diff = (seq1[j]-seq2[i+j])
            else:
                diff = (seq1[i+j]-seq2[j])
            diff_sum += abs(diff)
        diffs.append(diff_sum)

    closest = min(diffs, key=lambda x:abs(x)) # get value
    min_val = diffs[diffs.index(closest)]
        
    
    return min_val / min_len

def get_metrics(p_seq1, p_seq2, o_seq1, o_seq2):
    psim = pitch_similarity(p_seq1, p_seq2)
    osim = onset_similarity(o_seq1, o_seq2)
    pc = cross_correlation(p_seq1, p_seq2)
    oc = cross_correlation(o_seq1, o_seq2)
    return psim, osim, pc, oc

def get_segments(note_seq, seg_time = TICKS_PER_SEC * 5):
    last_note_end = 0
    segment_start = 0
    segment_end = 1
    segments = []
    for i, note in enumerate(note_seq):
        if i == 0:
            last_note_end = note.end
            continue
            
        if note.start - last_note_end < seg_time: #assuming monophonic, 
            segment_end = i + 1
        else:
            segments.append([segment_start, segment_end])
            segment_start = i
            segment_end = i + 1
        last_note_end = note.end

    # last segment
    if len(segments) == 0 or (segments[-1][0] != segment_start and segments[-1][1] != segment_end):
        segments.append([segment_start, segment_end])
    # print(segments)
    return segments

def similarity_rigor(note_seq1, note_seq2, last_searched_idx):
    assert len(note_seq1) >= len(note_seq2)
    # print(len(note_seq1), len(note_seq2))
    p_seq1, o_seq1 = get_pitch_onset_seq(note_seq1)
    p_seq2, o_seq2 = get_pitch_onset_seq(note_seq2)
    
    for i, note in enumerate(note_seq1):
        note_dur = note.end - note.start
        note_seq2_dur = note_seq2[0].end - note_seq2[0].start
        if note.pitch == note_seq2[0].pitch and abs(note.start - note_seq2[0].start) <= 735 * 20 and abs(note_dur - note_seq2_dur) <= 735 * 20:
            psim, osim, pc, oc = get_metrics(p_seq1[i:], p_seq2, o_seq1[i:], o_seq2)
            if pc <= 1.0:
                sim = [psim, osim, pc, oc]
                last_searched_idx = i + len(note_seq2)
                return sim, last_searched_idx
    
    return -1, last_searched_idx

def get_pitch_onset_seq(notes):
    pitch_seq = []
    onset_seq = []
    for note in notes:
        pitch_seq.append(note.pitch)
        onset_seq.append(note.start)
        
    return pitch_seq, onset_seq


def get_pitch_onset_seq_all_inst(midi_obj):
    pitch_seqs = [] 
    onset_seqs = []
    for ins in midi_obj.instruments:
        if ins.is_drum:
            continue
        else:
            pitch_seq, onset_seq = get_pitch_onset_seq(ins.notes)
            
        pitch_seqs.append(pitch_seq)
        onset_seqs.append(onset_seq)

    return pitch_seqs, onset_seqs