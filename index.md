# YM2413-MDB

This web repository contains musical examples from our paper, "YM2413-MDB: A Multi-Instrumental FM Video Game Music Dataset with Emotion Annotations".

We show baseline generation results of 4 bars using the emotion condition of _cheerful_ and _depressed_. Generated samples are rendered using [VST2413](http://www.keijiro.tokyo/vst2413/).

## Samples from dataset
Our dataset is **multi-labeled with 19 emotion tags**: tense, cheerful, speedy, serious, rhythmic, fluttered, peaceful, creepy, depressed, calm, grand, cold, dreamy, bizarre, cute, touching, comic, frustrating, and boring

** Top tag is _italicized_

|<center>Emotion Tag</center>|<center>Audio</center>|<center>Emotion Tag</center>|<center>Audio</center>|
|---|:---|:---|:---|
|**_Tense_**  <br /> <font size="2">serious</font>|<audio controls><source src='./audio_dataset/01 Last Attack.mp3'></audio>|**_Grand_** <br /><font size="2">peaceful</font>|<audio controls><source src='./audio_dataset/04 The March of Heroes.mp3'></audio>|
|**_Cheerful_** <br /> <font size="2">speedy fluttered</font>|<audio controls><source src='./audio_dataset/01 Is it Domingo Today.mp3'></audio>|**_Cold_** <br /> <font size="2">serious</font>|<audio controls><source src='./audio_dataset/12 Game Over (Namco Logo, The Tower of Druaga).mp3'></audio>
|**_Speedy_** <br /><font size="2">cheerful dreamy rhythmic</font>|<audio controls><source src='./audio_dataset/Out Run (FM) - 01 - Magical Sound Shower.mp3'></audio>|**_Dreamy_** <br /><font size="2">cold</font>|<audio controls><source src='./audio_dataset/Golvellius - Valley of Doom (FM) - 12 - Winkle.mp3'></audio>|
|**_Serious_** <br /><font size="2">tense creepy</font>|<audio controls><source src='./audio_dataset/10 The Devastation (Area 4).mp3'></audio>|**_Bizarre_** <br /><font size="2">creepy serious dreamy cold</font>|<audio controls><source src='./audio_dataset/Kenseiden (FM) - 03 - Map.mp3'></audio>|
|**_Rhythmic_** <br /><font size="2">cheerful peaceful speedy</font>|<audio controls><source src='./audio_dataset/Dynamite Dux (FM) - 03 - Pseudo Japan.mp3'></audio>|**_Cute_** <br /><font size="2">peaceful comic rhythmic</font>|<audio controls><source src='./audio_dataset/Megumi Rescue (FM) - 06 - Bonus Stage.mp3'></audio>|
|**_Fluttered_** <br /><font size="2">serious rhythmic</font>|<audio controls><source src='./audio_dataset/06 Dass XXX.mp3'></audio>|**_Touching_** <br /><font size="2">serious speedy calm</font>|<audio controls><source src='./audio_dataset/12_Credits.mp3'></audio>|
|**_Peaceful_** <br /><font size="2">cheerful</font>|<audio controls><source src='./audio_dataset/03 Utility.mp3'></audio>|**_Comic_** <br /><font size="2">cute</font>|<audio controls><source src='./audio_dataset/Alex Kidd - The Lost Stars (FM) - 09 - Time Up _ The End.mp3'></audio>|
|**_Creepy_** <br /> <font size="2">calm</font>|<audio controls><source src='./audio_dataset/03 Sample 3.mp3'></audio>|**_Frustrating_**<br /><font size="2">depressed</font>|<audio controls><source src='./audio_dataset/Summer Games (FM) - 11 - Unused.mp3'></audio>|
|**_Depressed_** <br /> <font size="2">serious calm</font>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|**_Boring_** <br /><font size="2">peaceful calm</font>|<audio controls><source src='./audio_dataset/Kenseiden (FM) - 14 - Ending.mp3'></audio>|
|**_Calm_** <br /> <font size="2">peaceful</font>|<audio controls><source src='./audio_dataset/Space Harrier 3-D (FM) - 03 - Ending.mp3'></audio>||

## Generated samples
samples from model that was trained with YM2413-MDB songs which has cheerful or depressed tag (not top tag!)

sampled at GPT2 step 20K checkpoint, sampling temperature 0.9

|<center>Cheerful</center>|<center>Depressed</center>|
|---|:---|
|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|
|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|
|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|
|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|
|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|<audio controls><source src='./audio_dataset/06_Over.mp3'></audio>|

