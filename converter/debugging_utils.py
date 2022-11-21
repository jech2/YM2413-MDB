import os
import pandas as pd
import numpy as np
import glob
from tqdm import tqdm

from pathlib import Path
from tqdm.auto import tqdm
import pickle
import itertools

from datetime import datetime

DEBUG_FILES = ['22 Boss 9', '01 Last Attack', '01 Compile', '01_Title', 'After Burner (FM) - 03 - After Burner', 'Alex Kidd - The Lost Stars (FM) - 04 - Machine World _ Giant_s Body', 
                   '08 Travelers Inn (Disappearance of the King_s Scepter)', '13 Mission 5', '06 Cemetery', '04 Chance BGM', 
                   'Dynamite Dux (FM) - 03 - Pseudo Japan', '01 Hyper Def|ending Force (Title)', '04 The March of Heroes', '04 Main BGM', '05 Demon War', '05 Town' ,'01 Prologue', '02 Technotris',
                   'BMX Trial - Alex Kidd - 02 - South Seas _ Pyramid River', 'Space Harrier 3-D (FM) - 13 - Goderni']

def generate_dir(dir_name, dir_subname='vgmplay_log_to_midi', use_date=False):
    now = datetime.now() # current date and time
    date_time = now.strftime("%Y%m%d-%H%M%S")

    if use_date:
        out_dir = Path(dir_name + f'/{dir_subname}_{date_time}/')        
    else:
        out_dir = Path(dir_name + f'/{dir_subname}/')
    os.makedirs(out_dir, exist_ok=True)

    print(f"Generate directory {out_dir}")
    return out_dir

def get_debug_fp(ydr_dir, debug_dir, debug_idx):
    in_fp = ydr_dir / (DEBUG_FILES[debug_idx] + '.ydr')
    out_fp = debug_dir / f'{DEBUG_FILES[debug_idx]}.mid'
    return in_fp, out_fp

def get_input(ydr_fp, _len=-1):

    with open(ydr_fp, "rb") as f:
        cmds = pickle.load(f)
    
    if _len > 0:
        cmds = cmds[:_len]
    
    return cmds