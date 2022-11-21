import os
import pandas as pd
import numpy as np
import glob
# from tqdm import tqdm
from tqdm.auto import tqdm
from pathlib import Path
import argparse

def read_vgm_txt(vgm_logs_fps):  
    # Read vgm txt files
    all_vgms = []
    error_vgms = [] # error vgm files
    data_start_idx = -1 # vgm data start index
    loop_start_idx = -1 # loop start index
    loop_end_idx = -1

    for vgm_logs_fp in tqdm(vgm_logs_fps):
        vgm = dict()
        vgm['filename'] = vgm_logs_fp
        with vgm_logs_fp.open() as f: 
            line = f.readlines()
            soundchips = []
            for i, l in enumerate(line):
                sl = l.split('\t')
                if 'Clock' in sl[0]:
                    soundchip = sl[0].split(' ')[0]
                    freq = int(sl[-1].split(' ')[0])
                    if soundchip == 'YM2413':
                        vgm['soundchip'] = soundchip
                        vgm['clock_freq'] = freq
                    if freq != 0:
                        soundchips.append([soundchip, freq])

                elif 'Total Length' in sl[0]:
                    total_sample_length = int(sl[-1].split(' ')[0])
                    vgm['total_sample_length'] = total_sample_length
                elif 'VGMData' in l:
                    data_start_idx = i + 1
                    vgm['data_start_index'] = data_start_idx
                elif 'Loop Point' in l:
                    loop_start_idx = i + 1
                    vgm['loop_start_index'] = loop_start_idx

            # error log
            if len(soundchips) != 1:
                error_vgms.append(['multiple soundchips', str(vgm_logs_fp), soundchips])

            vgm_data = line[data_start_idx:]

        vgm['data'] = vgm_data
        all_vgms.append(vgm)
    return all_vgms

# ydr = YM2413 Disassembly Raw
def save_ydr(vgms):
    for vgm in tqdm(vgms):
        import pickle
        bin_fp = out_dir / (vgm['filename'].stem + '.ydr')

        if not os.path.isfile(bin_fp):        
            fn = vgm['filename'].name
            vgm_data = vgm['data']
            ydr = [('clock', vgm['clock_freq'])]

            # EOF error checking
            if 'End of Data' not in vgm_data[-1].split('\t')[-1]:
                print('error')

            for cmd in vgm_data:
                if 'YM2413' in cmd:
                    cmd = cmd.split('\t')[-1].split(' ')
                    reg = int(cmd[1], 16) # hex to int
                    val = int(cmd[-1].rstrip(), 16)
                    ydr.append(('apu', reg, val))
                    # print(reg, val)
                elif 'Wait' in cmd:
                    cmd_ = cmd.split('\t')[1].strip().split(' ')
                    # y = cmd_.index('sample(s)')
                    wait_amt = int(cmd_[0])
                    ydr.append(('wait', wait_amt))

            ydr_collapsed = []
            # Collapse adjacent waits
            comm_i = 0
            while comm_i < len(ydr):
                comm = ydr[comm_i]
                comm_i += 1

                if comm[0] == 'wait':
                    wait_amt = comm[1]
                    while comm_i < len(ydr) and ydr[comm_i][0] == 'wait':
                        wait_amt += ydr[comm_i][1]
                        comm_i += 1
                    ydr_collapsed.append(('wait', wait_amt))
                else:
                    ydr_collapsed.append(comm)


            with open(bin_fp, "wb") as f:
                pickle.dump(ydr_collapsed, f)

        else:
            with open(bin_fp, "rb") as f:
                ydr_collapsed = pickle.load(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run VGM2MIDI converter')
    parser.add_argument('--in_vgmtxt_dir', type=str, default='../../YM2413-MDB-v1.0.0/vgm_txts/',
                        help='location of the vgm txt files')
    parser.add_argument('--out_ydr_dir', type=str, default='../../YM2413-MDB-v1.0.0/ydr/',
                        help='location of the vgm disassembly raw files')

    args = parser.parse_args()

    ########## Specify the input and output directory ##########
    in_dir = Path(args.in_vgmtxt_dir)
    out_dir = Path(args.out_ydr_dir)
    ############################################################

    out_dir.mkdir(exist_ok=True)

    # Get vgm txt files
    in_fps = list(sorted(in_dir.glob('*.txt'))) 
    print(f'{len(in_fps)} files were detected.')
    if len(in_fps) == 0:
        exit()

    all_vgms = read_vgm_txt(in_fps)
    print(f'Finished reading {len(in_fps)} vgm txt files.')

    save_ydr(all_vgms)
    print(f'Finished saving {len(in_fps)} ydr files.')