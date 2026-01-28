# Wav2Karaoke
 A Pipeline to Align Notes and Lyrics from a Song downloaded from YouTube
### Installation

Clone this repository to your local machine:

```bash
git clone git@github.com:NyokoKei/Wav2Karaoke.git
cd Wav2Karaoke
```

### Using Wav2Karaoke

Run the following command:

```bash
./wav2karaoke --youtube <url or id> --text <lyrics.txt> [--output <output dir>] [-s <result.csv>]
```

For help:
```bash
./wav2karaoke --help # OR ./wav2karaoke --h
```

#### Demo:
```bash
./wav2karaoke -i WTCryF1J54Y -o ./demo -t ./demo/lyrics.txt  
```
where `WTCryF1J54Y` is YouTube ID for "Auld Lang Syne" song.
