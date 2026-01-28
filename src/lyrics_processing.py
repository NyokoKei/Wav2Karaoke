# ===================================================================
# File for Lyrics Handling Steps 3.3, 
# 3.3.1 Lyrics Transcription using Montreal Forced Aligner for English
# ===================================================================
import shutil 
import argparse
import subprocess
from pathlib import Path

def transcription_prep(vocal_path: str, lyrics_path: str):
    """
    Preparation function before transcribing a song
    - Moving vocals and lyrics into one folder, for MFA handling
    
    :param vocal_path: path to vocal audio file (.wav)
    :type vocal_path: str
    :param lyrics_path: path to lyrics text file (.txt)
    :type lyrics_path: str
    """
    vocal_path = Path(vocal_path)
    lyrics_path = Path(lyrics_path) 


    temp_dir = Path("./temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    

    shutil.move(vocal_path, temp_dir / vocal_path.name)
    shutil.move(lyrics_path, temp_dir / lyrics_path.name)
    print(f"{vocal_path.name} and {lyrics_path.name} moved to temporary folder {temp_dir}.")
    return str(temp_dir)

def lyrics_transcription(vocal_path: str, lyrics_path: str):
    """
    lyrics transcription (word/phone levels) using MFA
    
    :param vocal_path: path to vocal audio file (.wav)
    :type vocal_path: str
    :param lyrics_path: path to lyrics text file (.txt)
    :type lyrics_path: str
    """

    input_dir = transcription_prep(vocal_path, lyrics_path)
    input_dir = Path(input_dir)
    files = [f for f in (Path(input_dir)).iterdir() if f.is_file()]
    if len(files) != 2: raise ValueError(f"{input_dir} must contain exactly 2 files")
    wav_files = [f for f in files if f.suffix.lower() == ".wav"]
    txt_files = [f for f in files if f.suffix.lower() == ".txt"]

    if not (len(wav_files) == 1 and len(txt_files) == 1):
        raise ValueError(f"{input_dir} must contain one .wav file and one .txt file")
    else:
        lyrics = txt_files[0]
        vocal = wav_files[0]
    lyrics_old = lyrics
    renamed = False

    if vocal.stem != lyrics.stem:
        temp_txt = lyrics.with_name(vocal.stem + lyrics.suffix)
        lyrics = lyrics.rename(temp_txt)
        print(f"---{lyrics_old.name} temporarily renamed to {lyrics.name}.---")
        renamed = True
        

    cmd = [
        "mfa", "align",
        str(input_dir),
        "english_us_arpa",
        "english_us_arpa",
        str(input_dir),
        "--clean",
        "--num_jobs", "4",
        "--beam", "200",
        "--retry_beam", "800"
    ]

    print(f"Transcribing a song...")
    try:
        subprocess.run(cmd, check=True)
        print("Finished!")
    except subprocess.CalledProcessError as e:
        print(f"Exception: {e}")

    if renamed: 
        lyrics.rename(lyrics_old)
        print("Changing lyrics file name back.")
    
    print(f"Moving files back to their original destination and deleting temporary folders/files.")
    output_dir = (Path(vocal_path)).parent
    for item in input_dir.iterdir():
        shutil.move(str(item), str(output_dir / item.name))
    input_dir.rmdir() 

    return Path(vocal_path).with_suffix(".TextGrid")

# lyrics_transcription("vocal_path.wav", "lyrics_path.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-v", "--vocal",
        required=True,
        help="Singing Voice (.wav)"
    )
    parser.add_argument(
        "-t", "--text",
        required=True,
        help="Lyrics transcription (.txt)"
    )

    args = parser.parse_args()
    lyrics_transcription(args.vocal, args.text)
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RESET = "\033[0m"
    print(f"{BOLD}{GREEN}LYRICS PROCESSING: DONE{RESET}")