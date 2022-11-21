import math
from vgm_conversion_utils import *
from midi_utils import *
#PI = 3.14

# OPLL is triggered by the bit changes ( continuing same bit doesn't have any effect (rhythm mode, note on / off))
def get_trigger(toggle_condition, switch_on):
    # update OE address of register
    trigger = None
    if toggle_condition:
        if not switch_on:
            trigger = "ON"
    else:
        if switch_on:
            trigger = "OFF"

    return trigger

# store the information of rhythm instrument(onset, volume)
class Rhythms():
    def __init__(self, name, channel, program):
        self.on = False
        self.volume = 0
        self.velocity = dB2vel(self.volume, _round=True)

        self.trigger = False

        # additional parameter for managing instruments
        self.ins_name = name
        self.channel = channel
        self.program = program

    def set_switch(self, value):
        self.on = value

    def set_volume(self, value):
        self.volume = bit2dB(value)
        self.velocity = dB2vel(self.volume, _round=True) # log scale
        return Event(f'set volume', '', self.velocity, self.channel, self.program, f'{self.ins_name}: {value}bit/{self.volume}dB/velocity {self.velocity}')

# store the information of melodic instrument channel(f_number, block, key, sustain)
class Instruments():
    def __init__(self, channel):
        # default parameters of register address 1X(f-number LSB) 2X
        self.f_number = 0
        self.block = 0
        self.freq = 0.0
        self.key_on = False
        self.sustain_on = False

        # default parameters of register address 3X
        self.ins_index = 0
        self.volume = 0
        self.velocity = dB2vel(self.volume, _round=True)

        # additional parameter for managing instruments
        self.ins_name = "PIANO"
        self.channel = channel
        self.program = 0

    # Parameter update
    def set_ins_index(self, value):
        self.ins_index = value
        self.ins_name = INSTR_NAME[self.ins_index]
        self.program =  INSNAME2PROGRAM[self.ins_name]
        return Event(f'program change', '', self.ins_index, self.channel, self.program, f'[CH{self.channel}]{self.ins_name} of Channel {self.channel}')
    
    def set_volume(self, value):
        self.volume = bit2dB(value)
        self.velocity = dB2vel(self.volume, _round=True) # log scale
        return Event(f'set volume', '', self.velocity, self.channel, self.program, f'[CH{self.channel}]{INSTR_NAME[self.ins_index]}: {value}bit/{self.volume}dB/velocity {self.velocity}')

    def set_f_number(self, value, is_LSB):
        text = "LSB" if is_LSB else "MSB"
        if is_LSB:
            self.f_number = self.f_number & 0x0100 # clear the lower 8 bits
            cleared = self.f_number
            update_val =  value
            self.f_number = self.f_number | update_val
        else:
            self.f_number = self.f_number & 0x00FF # clear the upper 1 bit
            cleared = self.f_number
            update_val = ((value & 1) << 8)
            self.f_number = self.f_number | update_val

        return Event(f'set F-num', '', self.f_number, self.channel, self.program, f'[CH{self.channel}]{INSTR_NAME[self.ins_index]}: update {text}({update_val}) + {cleared}')
    
    def set_block(self, value):
        self.block = value        
        return Event(f'set block', '', self.block, self.channel, self.program, f'[CH{self.channel}]{INSTR_NAME[self.ins_index]}: update block {value}')

    def set_freq(self):
        # if self.block == 0 and self.f_number > F_NUM_REC_MIN and self.f_number < F_NUM_REC_MAX:
        #     self.block = 4
        #     print("block number adjusting")
        self.freq = fnum2freq(self.f_number, self.block)

        return Event(f'set freq', '', self.freq, self.channel, self.program, f'[CH{self.channel}]{INSTR_NAME[self.ins_index]}: update freq {self.freq} Hz')

    def set_sustain_on(self, value):
        self.sustain_on = value

    def set_key_on(self, value):
        self.key_on = value

    # this is for handling last note.
    def set_key_off(self):
        key_trigger = get_trigger(False, self.key_on)
        self.set_key_on(False)
        
        assert key_trigger == "OFF"
        return [Item('key off', '', '', self.velocity, self.freq, self.channel, self.program, f'[CH{self.channel}]{INSTR_NAME[self.ins_index]}')]

# class which emulates the ym2413 soundchip
class YM2413():
    def __init__(self, opll_clock=3579540.0):
        # init opll channels and rhythm channels
        self.instruments = []
        self.rhythms = []
        self.rhythm_mode = False

        self.n_channels = 9
        self.n_rhythms = 5

        self.opll_clock = opll_clock # ym2413 clock

        self.rhythm_name_map = RHYTHM_NAME_MAP


        for i in range(self.n_channels):
            instr = Instruments(i)
            self.instruments.append(instr)

        for i in range(self.n_rhythms):
            rhythm_instr = Rhythms(self.rhythm_name_map[i], channel=DRUM_CHANNEL, program=MIDI_DRUM_MAP[i])
            self.rhythms.append(rhythm_instr)
    
    def set_rhythm_mode(self, value):
        self.rhythm_mode = value
            

    # Parameter update based on register address
    def update_0E(self, value):
        # update OE address of register
        rhythm_trigger = get_trigger(bit(value, 5), self.rhythm_mode)
        self.set_rhythm_mode(bit(value, 5))

        interpret = []
        for i in range(5):
            note_trigger = get_trigger(bit(value, i), self.rhythms[4-i].on)
            self.rhythms[4-i].set_switch(bit(value, i))

            if note_trigger == "ON":
                interpret += [Item('drum note on', '', '', self.rhythms[4-i].velocity, MIDI_DRUM_MAP[4-i], self.rhythms[4-i].channel, self.rhythms[4-i].program, f'drum note on {self.rhythm_name_map[4-i]}, VOL {self.rhythms[4-i].volume} dB')]
        
        return interpret

    def update_1X(self, X, value):
        # update 1X address of register
        c = self.instruments[X]
        interpret = [c.set_f_number(value, is_LSB=True)] # set the lower 8 bits as value
        interpret += [c.set_freq()]
        return interpret

    def update_2X(self, X, value):
        # update 2X address of register     
        c = self.instruments[X]

        # frequency related
        interpret = []
        interpret += [c.set_f_number(value, is_LSB=False)] # set the lower 8 bits as value
        interpret += [c.set_block((value >> 1) & 0x7)]

        interpret += [c.set_freq()]

        # sustain on / off
        sustain_trigger = get_trigger(bit(value, 5), c.sustain_on)
        c.set_sustain_on(bit(value, 5))
        
        if sustain_trigger == "ON":
            interpret += [Event('sustain on', '', c.sustain_on, c.channel, c.program, f'[CH{X}]{INSTR_NAME[c.ins_index]}')]
        elif sustain_trigger == "OFF":
            interpret += [Event('sustain off', '', c.sustain_on, c.channel, c.program, f'[CH{X}]{INSTR_NAME[c.ins_index]}')]

        # key on / off
        key_trigger = get_trigger(bit(value, 4), c.key_on)
        c.set_key_on(bit(value, 4))
        
        if key_trigger == "ON":
            interpret += [Item('key on', '', '', c.velocity, c.freq, c.channel, c.program, f'[CH{X}]{INSTR_NAME[c.ins_index]}')]
        elif key_trigger == "OFF":
            interpret += [Item('key off', '', '', c.velocity, c.freq, c.channel, c.program, f'[CH{X}]{INSTR_NAME[c.ins_index]}')]

        return interpret

    def update_3X(self, X, value):
        # update 3X address of register
        interpret = []
        # set the instrument and volume
        c = self.instruments[X]
        interpret += [c.set_ins_index((value >> 4) & 0x0F)]
        interpret += [c.set_volume(value & 0x0F)]

        if self.rhythm_mode:
            if X == 0x06:
                interpret += [self.rhythms[0].set_volume(value & 0x0F)]
            if X == 0x07:
                interpret += [self.rhythms[1].set_volume((value >> 4) & 0x0F)]
                interpret += [self.rhythms[2].set_volume(value & 0x0F)]
            if X == 0x08:
                interpret += [self.rhythms[3].set_volume((value >> 4) & 0x0F)]
                interpret += [self.rhythms[4].set_volume(value & 0x0F)]
        
        return interpret

    # write register
    def write(self, register, value):
        upper_channel = register & 0xF0
        lower_channel = register & 0x0F
        interpret = None
        if upper_channel == 0x00:
            # rhythm mode related command
                if lower_channel == 0x0E:
                    interpret = self.update_0E(value)

        elif upper_channel == 0x10:
            # set the LSB of an F-number
            interpret = self.update_1X(lower_channel, value)
        
        elif upper_channel == 0x20:
            # set the F-Number MSB, octave set, Key ON/OFF register, Sustain ON/OFF register
            interpret = self.update_2X(lower_channel, value)

        elif upper_channel == 0x30:
            # set the instrument and volume
            interpret = self.update_3X(lower_channel, value)


        return interpret