# Wav2Karaoke
 A Pipeline to Align Notes and Lyrics from a Song downloaded from YouTube
### Installation

Clone this repository to your local machine:

```bash
git clone git@github.com:NyokoKei/Wav2Karaoke.git
cd Wav2Karaoke
```
You're all set! 🎉

### Using Wav2Karaoke

This package includes a command line utility `./wav2karaoke`. Run:

```bash
./wav2karaoke --youtube [url or id] --text [lyrics.txt] [--output [output dir]] [-s [result.csv]]
```

For help:
```bash
./wav2karaoke --help # OR ./wav2karaoke --h
```

#### Demo:
```bash
./wav2karaoke -i WTCryF1J54Y -o ./demo -t ./demo/lyrics.txt  
```
`WTCryF1J54Y`: "Auld Lang Syne"
