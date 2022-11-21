import math

F_SAM_YM2413 = 50000
F_NUM_REC_MIN = 181
F_NUM_REC_MAX = 485

# check whether specific bit is on
def bit(value, position):
    return (value & (1 << position)) != 0

# unit changer
def dB2vel(x, _round=False):
    if type(x) == int:
        y = 4 * math.exp((x+45)/13)
        if _round:
            y = round(y)
    else:
        y = np.zeros_like(x)
        for i in range(y.size):
            y[i] = 4 * math.exp((x[i]+45)/13)
            if _round:
                y[i] = round(y[i])
    return y

def bit2dB(x):
    ret = 0
    if bit(x, 3):
        ret += 24
    if bit(x, 2):
        ret += 12
    if bit(x, 1):
        ret += 6
    if bit(x, 0):
        ret += 3
    ret = -ret # the dB is minus value
    return ret

def freq2key(freq, _round=True):
    if freq == 0:
        return 0
    key = 12.0 * math.log(freq/440, 2.0) + 69.0
    if _round:
        key = round(key)

    return key

# If Block = 0 And FNum = 0 Then Hz_YM2413 = 0 Else Hz_YM2413 = FNum * fsam2413 * 2 ^ (Block - 19)
def fnum2freq(f_number, block):
    freq = 0.0
    if f_number != 0:
        freq = int(f_number * F_SAM_YM2413 * math.pow(2.0, block - 19)) # block starts from 0 (A4's fnum is 288 and b is 3 )
    
    return freq