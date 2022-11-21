import os
from tabnanny import verbose
import pandas as pd
import numpy as np
import glob
from tqdm import tqdm

from pathlib import Path
from tqdm.auto import tqdm
import pickle
import itertools
import argparse

from debugging_utils import *
from midi_utils import *
from ym2413 import *

#### CONSTANTS
YM2413_CLOCK = [3579540, 3579545]

#### CONVERTER
class Converter():
    def __init__(self, verbose=False):
        self.passed_samples = 0
        self.ym2413 = YM2413()
        self.all_events = []

        self.drum_padding = 1
        
        
        #### DEBUG VAR
        self.key_on_count = 0
        self.key_off_count = 0
        self.verbose = verbose
                
    def logging(self, x):
        if self.verbose:
            print(x)
        else:
            return

    def process_one_cmd(self, cmd):
        if cmd[0] == 'clock':
            assert cmd[1] in YM2413_CLOCK, f'Invalid YM2413 clock value {cmd[1]}, it should be {YM2413_CLOCK}'
        elif cmd[0] == 'wait':
            vgm_wait = cmd[1]
            self.passed_samples += vgm_wait
        elif cmd[0] == 'apu':
            reg = cmd[1]; val = cmd[2]
            self.logging(f'[{hex(reg)}, {hex(val)} at sample time {self.passed_samples}]')
            interpret = self.ym2413.write(reg, val)
            if type(interpret) == list:
                for item in interpret:
                    if type(item) == Item:
                        if 'drum note on' in item.name:
                            item.start = self.passed_samples
                            item.end = self.passed_samples + self.drum_padding
                        else:
                            item.start = self.passed_samples
                            item.end = self.passed_samples
                            if "key on" in item.name:
                                self.key_on_count += 1
                            if "key off" in item.name:
                                self.key_off_count += 1
                    if type(item) == Event:
                        item.time = self.passed_samples
                self.logging(interpret)              
                self.all_events += interpret

    def handle_last_notes(self):
        for ins in self.ym2413.instruments:
            if ins.key_on:
                interpret = ins.set_key_off()
                for item in interpret:
                    if type(item) == Item:
                        item.start = self.passed_samples
                        item.end = self.passed_samples
                # print(interpret)
                self.key_off_count += 1
                self.all_events += interpret

    def process_one_file(self, ydr, out_midi_fp):
        for cmd in ydr:    
            self.process_one_cmd(cmd)

        self.handle_last_notes()

        assert self.key_off_count == self.key_on_count, f'note off count{self.key_off_count} should be equal to note on count{self.key_on_count}'

        midi_instruments = separate_channels_mido([self.all_events], use_note_on_pitch=True)

        midi = separate2midi_mido(midi_instruments, out_midi_fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run VGM2MIDI converter')
    parser.add_argument('--in_ydr_dir', type=str, default='../../YM2413-MDB-v1.0.0/ydr/',
                        help='location of the vgm disassembly raw files')
    parser.add_argument('--out_midi_dir', type=str, default='../../YM2413-MDB-v1.0.0/midi/',
                        help='location of the converted midi files, if debug mode, ../debug/')
    parser.add_argument('--debug', action='store_true',
                        help='debug mode: only convert one vgm file')
    parser.add_argument('--debug_idx', type=int, default=0,
                        help='debug input index')
    parser.add_argument('--debug_len', type=int, default=-1,
                        help='maximum debug input command length')
    parser.add_argument('--verbose', action='store_true',
                        help='print all output of converter')
    args = parser.parse_args()

    ydr_dir = Path(args.in_ydr_dir)

    if args.debug:
        args.out_midi_dir = '../debug/'
        print("Debug mode! only check one debug file")
        debug_dir = generate_dir(dir_name=args.out_midi_dir)
        in_fp, out_midi_fp = get_debug_fp(ydr_dir, debug_dir, args.debug_idx, use_date=True)
        cmds = get_input(in_fp, args.debug_len)

        c = Converter(verbose=args.verbose)
        c.process_one_file(ydr=cmds, out_midi_fp=out_midi_fp)
        print(f"Finished conversion: output file is {str(out_midi_fp)}")

    else:
        # Get vgm txt files
        in_fps = list(sorted(ydr_dir.glob('*.ydr'))) 
        print(f'{len(in_fps)} files were detected.')
        if len(in_fps) == 0:
            exit()
        
        out_dir = generate_dir(dir_name=args.out_midi_dir)
        
        for in_fp in tqdm(in_fps):
            out_midi_fp = out_dir / (in_fp.stem + '.mid') 
            cmds = get_input(in_fp, args.debug_len)

            c = Converter(verbose=args.verbose)
            c.process_one_file(ydr=cmds, out_midi_fp=out_midi_fp)

        print(f'Finished converting {len(in_fps)} vgm files.')
        