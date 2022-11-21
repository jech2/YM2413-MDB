from mido import bpm2tempo
import miditoolkit
from vgm_conversion_utils import *
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
import math

#### CONSTANTS    
MIDI_NUM_A440 = 69 # midi number of a440
MIDI_MIN = 0
MIDI_MAX = 128

OCTAVE = 12

MIDI_TRIM_MIN = 22
MIDI_TRIM_MAX = 108

TICKS_PER_BEAT = 17640 
TEMPO = 150
# TEMPO = (1.0 / 2.5) * 1000 * 1000 # tempo in microsec : 150 bpm is 400000 us per beat
# TEMPO = bpm2tempo(150)

PITCHBEND_STEPS = 8192.0 / 2.0
PITCHBEND_MAX = 8191.0
PITCHBEND_MIN = -8192.0


#### YM2413 MIDI Constants
INSTR_NAME = ['ElectricPiano', 'Violin', 'AcousticGuitar(steel)', 
                'AcousticGrandPiano', 'Flute', 'Clarinet', 'Oboe', 
                'Trumpet', 'ChurchOrgan', 'FrenchHorn', 'Lead2(sawtooth)', 'Harpsichord',
                'Vibraphone', 'SynthBass1', 'AcousticBass', 'ElectricGuitar(clean)', 'SteelDrum']
program_instr_dict = {4:'ElectricPiano', 40:'Violin', 24:'AcousticGuitar(steel)', 
        0:'AcousticGrandPiano', 73:'Flute', 71:'Clarinet', 68:'Oboe', 
        56:'Trumpet', 19:'ChurchOrgan', 60:'FrenchHorn', 81:'Lead2(sawtooth)', 6:'Harpsichord',
        11:'Vibraphone', 38:'SynthBass1', 32:'AcousticBass', 27:'ElectricGuitar(clean)', 114:'SteelDrum'}
INSNAME2PROGRAM = {'ElectricPiano':4, 'Violin':40, 'AcousticGuitar(steel)':24, 
        'AcousticGrandPiano':0, 'Flute':73, 'Clarinet':71, 'Oboe':68, 
        'Trumpet':56, 'ChurchOrgan':19, 'FrenchHorn':60, 'Lead2(sawtooth)':81, 'Harpsichord':6,
        'Vibraphone':11,'SynthBass1':38,'AcousticBass':32,'ElectricGuitar(clean)':27, 'SteelDrum':114}
RHYTHM_NAME_MAP = ["Bass Drum(BD)", "Snare Drum(SD)", "Tom-tom(TT)", "Top Cymbal(T-CY)", "High Hat(HH)"]
MIDI_DRUM_MAP = [36, 38, 45, 49, 42] # midi key number of bass drum, snare, tom-tom, cymbal, closed high hat
DRUM_INS = 114
DRUM_CHANNEL = 9


VGM_SPECIFIC_CMDS = ['set volume', 'program change', 'set F-num', 'set block', 'set freq', 'sustain on', 'sustain off']

#### MIDI Conversion code
class Item(object):
    """
    define "Item" for general storage
    """
    def __init__(self, name, start, end, velocity, pitch, channel, program, text):
        self.name = name
        self.start = start
        self.end = end
        self.velocity = velocity
        self.pitch = pitch
        self.channel = channel
        self.program = program
        self.text = text

    def __repr__(self):
        return f"Item(name={self.name}, start={self.start}, end={self.end}, velocity={self.velocity}, pitch={self.pitch}, channel={self.channel}, program={self.program}, text={self.text})"

class Event(object):
    """
    define "Event" for event storage
    """
    def __init__(self, name, time, value, channel, program, text):
        self.name = name
        self.time = time
        self.value = value
        self.channel = channel
        self.program = program
        self.text = text

    def __repr__(self):
        return f"Event(name={self.name}, time={self.time}, value={self.value}, channel={self.channel}, program={self.program}, text={self.text})"

class LastCache():
    def __init__(self):
        self.reset()

    def update(self, freq=None, vel=None, time=None, pitch_bend=None, is_on=None, on_pitch=None): # note on
        if freq is not None:
            self.last_freq = freq
        if vel is not None:
            self.last_vel = vel
        if time is not None:
            self.last_sample_time = time
        if pitch_bend is not None:
            self.pitch_wheel = pitch_bend
        if is_on is not None:
            self.is_on = is_on
        if on_pitch is not None:
            self.on_pitch = on_pitch

    def reset(self):
        self.last_freq = 0.0
        self.last_vel = 0
        self.last_sample_time = 0
        self.pitch_bend = 0.0
        self.is_on = False
        self.on_pitch = 0





# change the out of range notes
def change_out_of_range_notes(midi):
    lower_cnt = 0
    higher_cnt = 0
    for i, ins in enumerate(midi.instruments):
        if ins.is_drum:
            continue
        lower = 0
        higher = 0
        lowest = MIDI_MAX
        highest = MIDI_MIN
        for note in ins.notes:
            lowest = min(lowest, note.pitch)
            highest = max(highest, note.pitch)
            
            if note.pitch < MIDI_TRIM_MIN:
                lower = min(lower, note.pitch - MIDI_TRIM_MIN)
        
            if note.pitch >= MIDI_TRIM_MAX:
                higher = max(higher, note.pitch - MIDI_TRIM_MAX)

        if lower < 0 and higher > 0:
            print("Error")

        while(lower < 0):               
            for j, note in enumerate(ins.notes):
                midi.instruments[i].notes[j].pitch += OCTAVE
            lower += OCTAVE
            lower_cnt += 1
        while(higher > 0):            
            for j, note in enumerate(ins.notes):
                midi.instruments[i].notes[j].pitch -= OCTAVE
            higher -= OCTAVE
            higher_cnt += 1
        
    print(f'adjusted the pitch range from [{lowest}, {highest}] to [{MIDI_TRIM_MIN},{MIDI_TRIM_MAX}]: {lower_cnt} times(lower), {higher_cnt} times(higher)')

    return midi, (lower_cnt, higher_cnt)

def separate_channels_mido(items, n_channels=9, use_note_on_pitch=True):
    caches = []
    for i in range(n_channels+1):
        caches.append(dict())

    midi_instruments = []
    for i in range(n_channels+1):
      midi_instruments.append(dict())

    for i, ins_items in enumerate(items):
        for item in ins_items:
            program = item.program
            channel = item.channel
            
            if item.name == 'key on':
                # initialization
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = MidiTrack([Message('program_change', channel=channel, program=program, time=item.start)])
                    caches[channel][program] = LastCache()
                    caches[channel][program].update(time=item.start)

                key = freq2key(item.pitch, _round=False)
                
                if key < 0:
                    continue

                new_pitch_bend = round((key - round(key)) * PITCHBEND_STEPS)
                msg = Message('note_on', channel=channel, note=round(key), velocity=item.velocity, time=item.start-caches[channel][program].last_sample_time)
                midi_instruments[channel][program].append(msg)
                caches[channel][program].update(freq=item.pitch, vel=item.velocity, time=item.start, is_on=True, on_pitch=freq2key(item.pitch, _round=True)) # freq, vel, sample, pitch_wheel 

                msg = Message('pitchwheel', channel=channel, pitch=new_pitch_bend, time=item.start-caches[channel][program].last_sample_time)
                midi_instruments[channel][program].append(msg)
                caches[channel][program].update(pitch_bend=new_pitch_bend)

            elif item.name == 'set freq':
                # initialization
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = MidiTrack([Message('program_change', channel=channel, program=program, time=item.time)])
                    caches[channel][program] = LastCache()
                    caches[channel][program].update(time=item.time) # freq, vel, sample, pitch_wheel
                
                if not caches[channel][program].is_on:
                    continue

                key1 = freq2key(caches[channel][program].last_freq, _round=False) # note on pitch
                key2 = freq2key(item.value, _round=False) # note off pitch

                if key1 == key2 or key2 < 0:
                    continue

                if key1 <= 0:
                    key1 = key2
                
                diff = round((key2 - key1) * PITCHBEND_STEPS)

                # if current and accumulated pitch values are in range, just update the pitch bend value
                if abs(diff) > 0 and abs(caches[channel][program].pitch_bend + diff) < PITCHBEND_MAX:
                    new_pitch_bend = round(caches[channel][program].pitch_bend + diff)
                    msg = Message('pitchwheel', channel=channel, pitch=new_pitch_bend, time=item.time-caches[channel][program].last_sample_time)
                    midi_instruments[channel][program].append(msg)
                    caches[channel][program].update(time=item.time, pitch_bend=new_pitch_bend) # freq, vel, sample, pitch_wheel


                # if not, generate new note event and update the pitch bend value
                else:
                    if caches[channel][program].on_pitch < 0:
                        continue
                    msg = Message('note_off', channel=channel, note=caches[channel][program].on_pitch, time=item.time-caches[channel][program].last_sample_time)
                    midi_instruments[channel][program].append(msg)
                    caches[channel][program].update(freq=item.value, time=item.time) # freq, vel, sample, pitch_wheel 
                    
                    key = round(key1)
                    vel = caches[channel][program].last_vel

                    assert vel >= MIDI_MIN and vel < MIDI_MAX, f'Invalid velocity value {vel}, it should be in [{MIDI_MIN}, {MIDI_MAX}).'
                    if key < MIDI_MIN or key >= MIDI_MAX:
                        # print(f'Invalid midi note value {key}, {item.pitch}, it should be in [{MIDI_MIN}, {MIDI_MAX}).')
                        continue
                    
                    msg = Message('note_on', channel=channel, note=round(key2), velocity=vel, time=item.time-caches[channel][program].last_sample_time)
                    midi_instruments[channel][program].append(msg)
                    new_pitch_bend = round((key2 - round(key2)) * PITCHBEND_STEPS)

                    caches[channel][program].update(freq=item.value, time=item.time, pitch_bend=0, on_pitch=round(key2)) # freq, vel, sample, pitch_wheel 

                    msg = Message('pitchwheel', channel=channel, pitch=new_pitch_bend, time=item.time-caches[channel][program].last_sample_time)
                    midi_instruments[channel][program].append(msg)

                    caches[channel][program].update(pitch_bend=new_pitch_bend)

            elif item.name == 'key off':
                # initialization
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = MidiTrack([Message('program_change', channel=channel, program=program, time=item.start)])
                    caches[channel][program] = LastCache()
                    caches[channel][program].update(time=item.start) # freq, vel, sample, pitch_wheel

                assert item.velocity >= MIDI_MIN and item.velocity < MIDI_MAX, f'Invalid velocity value {item.velocity}, it should be in [{MIDI_MIN}, {MIDI_MAX}).'
                key = caches[channel][program].on_pitch
                if key < MIDI_MIN or key >= MIDI_MAX:
                    # print(f'Invalid midi note value {key}, {item.pitch}, it should be in [{MIDI_MIN}, {MIDI_MAX}).')
                    continue
                msg = Message('note_off', note=key, time=item.start-caches[channel][program].last_sample_time, channel=channel)
                midi_instruments[channel][program].append(msg)
                caches[channel][program].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0, is_on=False, on_pitch=-1) # freq, vel, sample, pitch_wheel
            
            elif item.name == 'drum note on':
                program = DRUM_INS
                channel = DRUM_CHANNEL
                # initialization
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = MidiTrack([Message('program_change', channel=channel, program=program, time=item.start)])
                    caches[channel][program] = LastCache()
                    caches[channel][program].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0) # freq, vel, sample, pitch_wheel
                
                midi_instruments[channel][program].append(Message('note_on', channel=channel, note=item.pitch, velocity=item.velocity, time=item.start-caches[channel][program].last_sample_time))
                caches[channel][program].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0) # freq, vel, sample, pitch_wheel
                msg = Message('note_off', channel=channel, note=item.pitch, velocity=0, time=1)
                midi_instruments[channel][program].append(msg)
                caches[channel][program].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0) # freq, vel, sample, pitch_wheel


    return midi_instruments

### FOR CHANNEL SEPARATION
# midi instrument which contains miditoolkit note
def separate_channels(items, n_channels=9, use_note_on_pitch=True):
    caches = []
    for i in range(n_channels+1):
        cache = LastCache()
        caches.append(cache)

    midi_instruments = []
    for i in range(n_channels+1):
      midi_instruments.append(dict())

    for i, ins_items in enumerate(items):
        for item in ins_items:
            program = item.program
            channel = item.channel
            
            if item.name == 'key on':
                caches[channel].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0)
            
            elif item.name == 'set freq':
                key1 = freq2key(caches[channel].last_freq, _round=False) # note on pitch
                key2 = freq2key(item.value, _round=False) # note off pitch

                if key1 == key2:
                    continue

                if key2 < 0:
                    continue

                if key1 == 0:
                    key1 = key2
                
                diff = round((key2 - key1) * PITCHBEND_STEPS)

                # initialization
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = []

                # if current and accumulated pitch values are in range, just update the pitch bend value
                if abs(diff) > 0 and abs(caches[channel].pitch_bend + diff) < PITCHBEND_MAX:
                    new_pitch_bend = round(caches[channel].pitch_bend + diff)
                    midi_instruments[channel][program].append(miditoolkit.PitchBend(pitch=new_pitch_bend, time=item.time))

                # if not, generate new note event and update the pitch bend value
                else:
                    key = round(key1)
                    vel = caches[channel].last_vel

                    assert vel >= MIDI_MIN and vel < MIDI_MAX, f'Invalid velocity value {vel}, it should be in [{MIDI_MIN}, {MIDI_MAX}).'
                    if key < MIDI_MIN or key >= MIDI_MAX:
                        # print(f'Invalid midi note value {key}, {item.pitch}, it should be in [{MIDI_MIN}, {MIDI_MAX}).')
                        continue
                                        
                    midi_instruments[channel][program].append(miditoolkit.Note(velocity=vel, pitch=key, start=caches[channel].last_sample_time, end=item.time))
                    new_pitch_bend = round((key2 - round(key2)) * PITCHBEND_MAX)
                    midi_instruments[channel][program].append(miditoolkit.PitchBend(pitch=new_pitch_bend, time=item.time))

                    caches[channel].update(freq=item.value, vel=caches[channel].last_vel, time=item.time, pitch_bend=new_pitch_bend)

            elif item.name == 'key off':
                # duration = item.time - caches[item.channel].last_sample_time
                key1 = freq2key(caches[channel].last_freq, _round=False) # note on pitch
                key2 = freq2key(item.pitch, _round=False) # note off pitch

                if use_note_on_pitch:
                    key = round(key1) 
                else:
                    key = round(key2)

                assert item.velocity >= MIDI_MIN and item.velocity < MIDI_MAX, f'Invalid velocity value {item.velocity}, it should be in [{MIDI_MIN}, {MIDI_MAX}).'
                if key < MIDI_MIN or key >= MIDI_MAX:
                    # print(f'Invalid midi note value {key}, {item.pitch}, it should be in [{MIDI_MIN}, {MIDI_MAX}).')
                    continue

                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = []
                midi_instruments[channel][program].append(miditoolkit.Note(velocity=item.velocity, pitch=key, start=caches[item.channel].last_sample_time, end=item.start))
                caches[channel].update(freq=item.pitch, vel=item.velocity, time=item.start, pitch_bend=0) # freq, vel, sample, pitch_wheel
                #caches[item.channel].midi_wheel = 0 # reset the midi_wheel value
                # caches[item.channel].reset()

            elif item.name == 'drum note on':
                program = DRUM_INS
                channel = DRUM_CHANNEL
                if program not in midi_instruments[channel].keys():
                    midi_instruments[channel][program] = []
                midi_instruments[channel][program].append(miditoolkit.Note(velocity=item.velocity, pitch=item.pitch, start=item.start, end=item.end))

    return midi_instruments


def get_events(instrument, filter='note'):
    ret = []
    
    for item in instrument:
        if filter == 'note' and type(item) == miditoolkit.midi.containers.Note:
            ret += [item]
        elif filter == 'pitch_bends' and type(item) == miditoolkit.midi.containers.PitchBend:
            ret += [item]

    return ret

# concatenate separate midi tracks into one file
def separate2midi_mido(midi_instruments, out_path, ticks_per_beat=TICKS_PER_BEAT, tempo=TEMPO, check_out_of_range_notes=False):
    # tempo = (1.0 / 2.5) * 1000 * 1000 # tempo in microsec : 150 bpm is 400000 us per beat
    tempo = bpm2tempo(tempo)

    # Generate File
    midi = MidiFile(type=1, ticks_per_beat=ticks_per_beat)
    
    meta_track = MidiTrack()
    meta_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    midi.tracks.append(meta_track)
      
    save_cnt = 0
    for ch, midi_instrument in enumerate(midi_instruments):
      for i, program in enumerate(midi_instrument.keys()):
        # if save_cnt > 0:
            # break
        if len(midi_instrument[program]) > 1:
          midi.tracks.append(midi_instrument[program])
        #   save_cnt += 1
        

    if check_out_of_range_notes:
        midi, (lower_cnt, higher_cnt) = change_out_of_range_notes(midi)
    else:
        lower_cnt = 0
        higher_cnt = 0

    midi.save(out_path)        
    # try:
    #     midi.dump(out_path)
    # except:
    #     if (lower_cnt + higher_cnt):
    #         print("arranging failed")
        

    return midi, (lower_cnt, higher_cnt)


# concatenate separate midi tracks into one file
def separate2midi(midi_instruments, out_path, ticks_per_beat=TICKS_PER_BEAT, tempo=TEMPO, check_out_of_range_notes=False):
    midi = miditoolkit.midi.parser.MidiFile()
    midi.ticks_per_beat = ticks_per_beat
    midi.tempo_changes.append(miditoolkit.TempoChange(tempo=tempo, time=0))

    for ch, midi_instrument in enumerate(midi_instruments):
      for i, program in enumerate(midi_instrument.keys()):
        if ch == DRUM_CHANNEL:
          instrument = miditoolkit.midi.containers.Instrument(program, is_drum=True)         
        else:
          instrument = miditoolkit.midi.containers.Instrument(program, is_drum=False)

        instrument.notes.extend(get_events(midi_instrument[program], filter='note'))
        instrument.pitch_bends.extend(get_events(midi_instrument[program], filter='pitch_bends'))
        # if ins_idx in self.pitch_bends[ch].keys():
        #   instrument.pitch_bends.extend(self.pitch_bends[ch][ins_idx])

        if len(instrument.notes) != 0:
          midi.instruments.append(instrument)

    if check_out_of_range_notes:
        midi, (lower_cnt, higher_cnt) = change_out_of_range_notes(midi)
    else:
        lower_cnt = 0
        higher_cnt = 0

    midi.dump(out_path)        
    # try:
    #     midi.dump(out_path)
    # except:
    #     if (lower_cnt + higher_cnt):
    #         print("arranging failed")
        

    return midi, (lower_cnt, higher_cnt)


def item2midi(items, out_path, ticks_per_beat=TICKS_PER_BEAT, tempo=TEMPO):
    """
    write midi file based on note items
    input : note items
    output : miditoolkit midi obj 
    """ 
    midi = miditoolkit.midi.parser.MidiFile()
    midi.ticks_per_beat = ticks_per_beat
    midi.tempo_changes.append(miditoolkit.TempoChange(tempo=tempo, time=0))

    for ins_items in items:
        for item in ins_items:
            ###### assuming that each instrument has one program change
            if type(item) == Item:
                program = item.name
                break

        if program == 114:
            is_drum = True
        else:
            is_drum = False
        instrument = miditoolkit.midi.containers.Instrument(program, is_drum=is_drum)
        for item in ins_items:
            if item.name not in VGM_SPECIFIC_CMDS:
                instrument.notes.append(miditoolkit.Note(item.velocity, item.pitch, item.start, item.end))
        midi.instruments.append(instrument)

    # write
    midi.dump(out_path)
    
    return midi