import pydub
from pathlib import Path
from tqdm import tqdm


audio_dir = Path("audio_dataset/")
audio_fps = audio_dir.glob("*.wav")

for audio_fp in tqdm(audio_fps):
    out_fp = str(audio_fp).replace(".wav", ".mp3")
    sound = pydub.AudioSegment.from_wav(audio_fp)
    sound.export(out_fp, format="mp3")