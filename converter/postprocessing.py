from pathlib import Path
import miditoolkit
from miditoolkit.midi import TempoChange
import os
import argparse
from tqdm import tqdm

from debugging_utils import generate_dir
from similarity_utils import *
from midi_utils import program_instr_dict

def get_downbeats(downbeat_fp):
    with open(downbeat_fp, 'r') as f:
        lines = f.readlines()
    downbeat = []
    for line in lines:
        downbeat.append(float(line.strip()))
        
    return downbeat


def adjust_beat_tracked_data(downbeat_fp, midi_obj):
    downbeat = get_downbeats(downbeat_fp)
    print(downbeat_fp)
        
    tps = 735 * 60
    
    changed_spb = []
    
    prev = downbeat[0]
    bpms = []
    for db in downbeat[1:]:
        bpm = int(1/(db-prev) * 60)
        changed_spb.append(db-prev)

        tick = int(db * tps)
        midi_obj.tempo_changes.append(TempoChange(bpm, tick))
        prev = db
        bpms.append(bpm)
    
    # for first downbeat
    if len(bpms) != 0:
        bpm = max(bpms, key=bpms.count)
    else:
        bpm = 150
    tick = int(downbeat[0] * tps)
    midi_obj.tempo_changes.append(TempoChange(bpm, tick)) 
    
    midi_obj.tempo_changes.sort(key= lambda x:(x.time, x.tempo))

    if len(changed_spb) != 0:
        new_tpb = int(tps * np.median(np.array(changed_spb)))
        if new_tpb > 32767:
            new_tpb /= 2
        new_tpb = int(round(new_tpb, -1))
        if new_tpb < -32768:
            print(downbeat_fp)
        midi_obj.ticks_per_beat = new_tpb
        print(new_tpb)

    return midi_obj
    
# by auto correlation
# default=1/3sec delay and picth similarity is 2
def remove_delayed_inst(midi_obj, pc_threshold=1.0, oc_threshold=735*20):

    n_window = 10 # note window

    del_list = []
    similars = set()
    sim_metrics = []
    nsim_metrics = []
    seg_del_list = []

    pitch_seqs, onset_seqs = get_pitch_onset_seq_all_inst(midi_obj)

    for i in range(len(pitch_seqs)):
        for j in range(i+1, len(pitch_seqs)):
            if i in del_list or j in del_list:
                continue
                
            p_seq1 = pitch_seqs[i]
            p_seq2 = pitch_seqs[j]
            o_seq1 = onset_seqs[i]
            o_seq2 = onset_seqs[j]
            
            # ignore too short instrument
            if len(p_seq1) <= 10 or len(p_seq2) <= 10:
                continue
            
            psim, osim, pc, oc = get_metrics(p_seq1, p_seq2, o_seq1, o_seq2)
            if pc <= pc_threshold and abs(oc) <= oc_threshold:
                similars.update([i, j])
                sim_metrics.append(f"{i}, {j}, {program_instr_dict[midi_obj.instruments[i].program]}, {program_instr_dict[midi_obj.instruments[j].program]}, psim: {psim}, pc: {pc}, osim: {osim}, oc: {oc}")
                if osim >= 0:
                    del_list.append(i)
                else:
                    del_list.append(j)
            else:
                # if two sequences have different length
                if len(p_seq1) < len(p_seq2):
                    smaller = i
                    bigger = j
                else:
                    smaller = j
                    bigger = i

                # do note windowing and calculate simlariry between tracks
                smaller_notes = midi_obj.instruments[smaller].notes
                bigger_notes = midi_obj.instruments[bigger].notes

                segment_idxs = get_segments(smaller_notes)
                last_searched_idx = 0
                for (seg_start, seg_end) in segment_idxs:
                    note_seq1 = bigger_notes
                    note_seq2 = smaller_notes[seg_start:seg_end]
                    last_searched_start = last_searched_idx
                    sim, last_searched_idx = similarity_rigor(note_seq1, note_seq2, last_searched_idx)
                    if sim == -1: # this segment is not similar..
                        continue
                    else:
                        if osim >= 0:
                            seg_del_list.append([bigger, last_searched_start, last_searched_idx])
                        else:
                            seg_del_list.append([smaller, seg_start, seg_end])
    
    # delete overlapped instrument region
    while len(seg_del_list) != 0: 
        k, seg_start, seg_end = seg_del_list.pop()
        del midi_obj.instruments[k].notes[seg_start:seg_end]
    
    # delete the overlapped instruments
    del_list = sorted(set(del_list), reverse=True)
    remove_cnt = 0
    for di in del_list:
        remove_cnt += 1
        del midi_obj.instruments[di]
        
    return midi_obj, remove_cnt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run VGM2MIDI converter')
    parser.add_argument('--in_midi_dir', type=str, default='../../YM2413-MDB-v1.0.0/midi/vgmplay_log_to_midi/',
                        help='location of the vgm disassembly raw files')
    parser.add_argument('--in_downbeat_dir', type=str, default='../../YM2413-MDB-v1.0.0/wav_downbeat/',
                        help='location of the converted midi files, if debug mode, ../debug/')
    parser.add_argument('--adjust_tempo', action='store_true',
                        help='adjust tempo using downbeat tracking')
    parser.add_argument('--remove_delayed_inst', action='store_true',      
                        help='remove delayed instruments')
    args = parser.parse_args()

    if not args.adjust_tempo and not args.remove_delayed_inst:
        print("You should specify at least one of adjust_tempo or remove_delayed_inst")
        exit()
    midi_dir = Path(args.in_midi_dir)
    downbeat_dir = Path(args.in_downbeat_dir)

    midi_list = sorted(list(midi_dir.glob("*.mid")))

    msg = ''
    if args.adjust_tempo:
        msg += "adjust_tempo"
    
    if args.remove_delayed_inst:
        if msg != '':
            msg += '_'
        msg += "remove_delayed_inst"

    out_dir = generate_dir(str(midi_dir.parent), msg)

    total_remove_cnt = 0
    os.makedirs(out_dir, exist_ok=True)
    for midi_fp in tqdm(midi_list):
        fname = midi_fp.stem
        downbeat_fp = downbeat_dir / (fname + ".beats.txt")
        
        midi_obj = miditoolkit.midi.parser.MidiFile(midi_fp)

        if args.adjust_tempo:
            midi_obj = adjust_beat_tracked_data(downbeat_fp, midi_obj)

        if args.remove_delayed_inst:
            midi_obj, remove_cnt = remove_delayed_inst(midi_obj)
            total_remove_cnt += remove_cnt

        midi_obj.dump(out_dir / midi_fp.name)

    if args.adjust_tempo:
        print("Tempo adjustment finished")

    if args.remove_delayed_inst:
        print(f"Remove total {total_remove_cnt} instruments")