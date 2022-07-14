# YM2413-MDB
This web repository contains musical examples from our paper, "YM2413-MDB: A Multi-Instrumental FM Video Game Music Dataset with Emotion Annotations".

![title_image](./title_img.png)

We show baseline generation results of 4 bars using the emotion condition of _cheerful_ and _depressed_. Generated samples are rendered using [VST2413](http://www.keijiro.tokyo/vst2413/).


## Samples from dataset
Our dataset is **multi-labeled with 19 emotion tags**: tense, cheerful, speedy, serious, rhythmic, fluttered, peaceful, creepy, depressed, calm, grand, cold, dreamy, bizarre, cute, touching, comic, frustrating, and boring

** Top tag is _italicized_

|<center>Emotion Tag</center>|<center>Audio</center>|<center>Emotion Tag</center>|<center>Audio</center>|
|---|:---|:---|:---|
|**_Tense_**  <br /> <font size="2">serious</font>|./audio_dataset/tense.mp3<audio controls><source src='./audio_dataset/tense.mp3'></audio>|**_Grand_** <br /><font size="2">peaceful</font>|./audio_dataset/grand.mp3<audio controls><source src='./audio_dataset/grand.mp3'></audio>|
|**_Cheerful_** <br /> <font size="2">speedy fluttered</font>|./audio_dataset/cheerful.mp3<audio controls><source src='./audio_dataset/cheerful.mp3'></audio>|**_Cold_** <br /> <font size="2">serious</font>|./audio_dataset/cold.mp3<audio controls><source src='./audio_dataset/cold.mp3'></audio>
|**_Speedy_** <br /><font size="2">cheerful dreamy rhythmic</font>|./audio_dataset/speedy.mp3<audio controls><source src='./audio_dataset/speedy.mp3'></audio>|**_Dreamy_** <br /><font size="2">cold</font>|./audio_dataset/dreamy.mp3<audio controls><source src='./audio_dataset/dreamy.mp3'></audio>|
|**_Serious_** <br /><font size="2">tense creepy</font>|./audio_dataset/serious.mp3<audio controls><source src='./audio_dataset/serious.mp3'></audio>|**_Bizarre_** <br /><font size="2">creepy serious dreamy cold</font>|./audio_dataset/bizarre.mp3<audio controls><source src='./audio_dataset/bizarre.mp3'></audio>|
|**_Rhythmic_** <br /><font size="2">cheerful peaceful speedy</font>|./audio_dataset/rhythmic.mp3<audio controls><source src='./audio_dataset/rhythmic.mp3'></audio>|**_Cute_** <br /><font size="2">peaceful comic rhythmic</font>|./audio_dataset/cute.mp3<audio controls><source src='./audio_dataset/cute.mp3'></audio>|
|**_Fluttered_** <br /><font size="2">serious rhythmic</font>|./audio_dataset/fluttered.mp3<audio controls><source src='./audio_dataset/fluttered.mp3'></audio>|**_Touching_** <br /><font size="2">serious speedy calm</font>|./audio_dataset/touching.mp3<audio controls><source src='./audio_dataset/touching.mp3'></audio>|
|**_Peaceful_** <br /><font size="2">cheerful</font>|./audio_dataset/peaceful.mp3<audio controls><source src='./audio_dataset/peaceful.mp3'></audio>|**_Comic_** <br /><font size="2">cute</font>|./audio_dataset/comic.mp3<audio controls><source src='./audio_dataset/comic.mp3'></audio>|
|**_Creepy_** <br /> <font size="2">calm</font>|./audio_dataset/creepy.mp3<audio controls><source src='./audio_dataset/creepy.mp3'></audio>|**_Frustrating_**<br /><font size="2">depressed</font>|./audio_dataset/frustrating.mp3<audio controls><source src='./audio_dataset/frustrating.mp3'></audio>|
|**_Depressed_** <br /> <font size="2">serious calm</font>|./audio_dataset/depressed.mp3<audio controls><source src='./audio_dataset/depressed.mp3'></audio>|**_Boring_** <br /><font size="2">peaceful calm</font>|./audio_dataset/boring.mp3<audio controls><source src='./audio_dataset/boring.mp3'></audio>|
|**_Calm_** <br /> <font size="2">peaceful</font>|./audio_dataset/calm.mp3<audio controls><source src='./audio_dataset/calm.mp3'></audio>||

## Generated samples
samples from model that was trained with YM2413-MDB songs which has cheerful or depressed tag (not top tag!): sampled at GPT2 step 20K checkpoint, sampling temperature 0.9

|<center>Cheerful</center>|<center>Depressed</center>|
|---|:---|
|<center>./audio_generation/cheerful/1.mp3<audio controls><source src='./audio_generation/cheerful/1.mp3'></audio></center>|<center>./audio_generation/depressed/1.mp3<audio controls><source src='./audio_generation/depressed/1.mp3'></audio></center>|
|<center>./audio_generation/cheerful/2.mp3<audio controls><source src='./audio_generation/cheerful/2.mp3'></audio></center>|<center>./audio_generation/depressed/2.mp3<audio controls><source src='./audio_generation/depressed/2.mp3'></audio></center>|
|<center>./audio_generation/cheerful/3.mp3<audio controls><source src='./audio_generation/cheerful/3.mp3'></audio></center>|<center>./audio_generation/depressed/3.mp3<audio controls><source src='./audio_generation/depressed/3.mp3'></audio></center>|
|<center>./audio_generation/cheerful/4.mp3<audio controls><source src='./audio_generation/cheerful/4.mp3'></audio></center>|<center>./audio_generation/depressed/4.mp3<audio controls><source src='./audio_generation/depressed/4.mp3'></audio></center>|
|<center>./audio_generation/cheerful/5.mp3<audio controls><source src='./audio_generation/cheerful/5.mp3'></audio></center>|<center>./audio_generation/depressed/5.mp3<audio controls><source src='./audio_generation/depressed/5.mp3'></audio></center>|

