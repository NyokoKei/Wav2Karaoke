# ===================================================================
# File for Lyrics Handling Steps 3.3 and 3.4
# 3.3.2 Lyrics+TimeStamps Syllabification
# 3.4 Aligning Notes with Lyrids
# ===================================================================
import textgrid
import pyphen
import librosa
import argparse
import numpy as np
import pandas as pd
import os

def syllabification(text_grid_path: str, output_csv_path: str):
    """
    Function to Syllabify lyrics
    
    :param txt_grid_path: output from MFA transcription (.textgrid)
    :type txt_grid_path: str
    :param output_csv_path: path to store the output (.csv)
    :type output_csv_path: str
    """

    tg = textgrid.TextGrid.fromFile(text_grid_path)
    phones = tg.getFirst("phones")
    words = tg.getFirst("words")

    rows = []
    for interval in phones:
        rows.append({"phone": interval.mark, "start": round(interval.minTime, 3), "end": round(interval.maxTime,3)})
    phones_df = pd.DataFrame(rows)

    rows = []
    for interval in words:
        rows.append({"word": interval.mark, "start": round(interval.minTime, 3), "end": round(interval.maxTime,3)})
    words_df = pd.DataFrame(rows)

    syllables_rows = []
    for _, row in words_df.iterrows():
        # Get phonemes for the current word
        p_list = phones_df[(phones_df.start >= row.start) & (phones_df.end <= row.end)].to_dict('records')
        current_syllable = []
        # syllabification on the phoneme level
        for i, p in enumerate(p_list):
            current_syllable.append(p)
            phone = p["phone"]

            if phone and phone[-1].isdigit(): #check if the phone is a vowel
                rem = p_list[i+1:]
                next_vowel_id = next((j for j, x in enumerate(rem) if x['phone'][-1:].isdigit()), None)

                #if no more vowels, the rest of the word belongs to the current syllable
                if next_vowel_id is None:
                    current_syllable.extend(rem)
                # If there's a cluster (e.g., "M TH"), grab the first consonant
                elif next_vowel_id > 1:
                    current_syllable.append(rem[0])
                    p_list.pop(i+1) 
                # Save the syllable and reset
                syllables_rows.append({
                    "word": row["word"],
                    "syllable": "".join([x['phone'] for x in current_syllable]),
                    "start": current_syllable[0]["start"],
                    "end": current_syllable[-1]["end"],
                    "word_start": row["start"],
                    "word_end": row["end"]
                })
                if next_vowel_id is None: break
                current_syllable = []
                
    # phoneme level syllabification
    syllables_df = pd.DataFrame(syllables_rows)
    syllables_df["count"] = syllables_df.groupby(["word_start", "word_end"])["word"].transform("count")
    syllables_df["syl_idx"] = (
        syllables_df
        .groupby(["word_start", "word_end"], sort=False)
        .cumcount()
    )
    syllables_df = syllables_df.drop(columns=["word_start", "word_end"])

    # Ortho syllabification
    dic = pyphen.Pyphen(lang="en_US")
    syllables_df["syl"] = syllables_df.apply(lambda row: dic.inserted(row['word']) if row['count'] != 1 else row['word'], axis=1)
    syllables_df["syl"] = syllables_df.apply(lambda row: split_syl(row) if row['count'] != 1 else row['syl'], axis=1)
    syllables_df = syllables_df.drop(columns=['count', 'syl_idx'])

    syllables_df.to_csv(output_csv_path, index=False)
    return output_csv_path

def split_syl(row):
    """
    Function to split syllables on ortho level
    
    :param row: row of a DataFrame
    """
    splitted = row['syl'].split('-') #split pyphen output into list
    
    if row['count'] == len(splitted): # if match with phoneme level
        row['syl'] = splitted[row['syl_idx']]

    elif row['count'] < len(splitted): # elision
        excess = len(splitted) - row['count']
        merged = []
        for i, s in enumerate(splitted):
            if i < row['count']:
                merged.append(s)
            else:
                merged[-1] += s
        row['syl'] = merged[row['syl_idx']]

    else:
        pieces = split_more_phon_than_ortho(row['word'], row['count'])
        row['syl'] = pieces[row['syl_idx']]


    return row['syl']

def split_more_phon_than_ortho(word: str, count: int):
    """
    Function for syllabification when phoneme counts more than ortho
    e.g. about ['AH', 'BAWT'] about -> a-bout
    
    :param word: str
    :param count: (int) number of syllables
    """
    chars = list(word)
    L = len(chars)

    # special rule: word starts with 'a'
    if chars[0].lower() == 'a' and count > 1:
        # first syllable = 'a'
        pieces = ['a']
        remaining_letters = "".join(chars[1:])
        remaining_count = count - 1

        # proportional split of the remaining letters
        base = len(remaining_letters) // remaining_count
        rem = len(remaining_letters) % remaining_count
        pos = 0
        for i in range(remaining_count):
            take = base + (1 if i < rem else 0)
            pieces.append(remaining_letters[pos:pos+take])
            pos += take
        return pieces

    # default proportional split
    base = L // count
    rem = L % count
    sizes = [base + (1 if i < rem else 0) for i in range(count)]
    
    pieces = []
    pos = 0
    for s in sizes:
        pieces.append("".join(chars[pos:pos+s]))
        pos += s
    return pieces

#=====================================================Alighnment=====================================================
def pitch_to_midi(p: str):
    """
    Docstring for pitch_to_midi
    
    :param p: pitch
    :type p: str

    :return midi (number notation of a music note)
    """
    try:
        return librosa.note_to_midi(p)
    except:
        return np.nan

def freq_to_pitch(freq: float):
    '''
    https://en.wikipedia.org/wiki/Piano_key_frequencies
    https://stackoverflow.com/questions/64505024/turning-frequencies-into-notes-in-python
    Converts frequency to pitch

    :param freq: frequency value at the specific timestamp
    :type freq: float

    :return pitch: str
    '''
    A4 = 440.0
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                  'F#', 'G', 'G#', 'A', 'A#', 'B']
    n = round(12 * np.log2(freq / A4))
    note = note_names[(n + 9) % 12]
    octave = 4 + (n + 9) // 12
    return f"{note}{octave}"

def note_lyrics_alignment(freq_path: str, syllables_path:str):
    """
    Aligns notes with lyrics in karaoke style notation
    
    :param freq_path: path to melody transcription
    :type freq_path: str (.f0.csv)
    :param syllables_path: path to syllabified lyrics (.csv)
    :type syllables_path: str
    :param output_path: output path (.csv) 
    :type output_path: str | None. If None uses the same path as output_path
    """
    freq = pd.read_csv(freq_path)
    lyrics = pd.read_csv(syllables_path)

    lyrics['f0_freq'] = lyrics.apply(
        lambda row: (
                lambda sub: sub.loc[
                    sub['confidence'] >= sub['confidence'].quantile(0.99),
                    'frequency'
                ].median()
            )(
                freq.loc[
                    (freq['time'] >= row['start']) &
                    (freq['time'] < row['end'])
                ]
            ),
            axis=1
        )

    lyrics['pitch'] = lyrics['f0_freq'].map(freq_to_pitch)
    lyrics["midi"] = lyrics["pitch"].apply(pitch_to_midi)
    lyrics.to_csv(syllables_path, index=False)

# note_lyrics_alignment("/Users/ngohonghai/Desktop/M2/research/wav2karaoke/audio_processing/output/vocals.f0.csv", "/Users/ngohonghai/Desktop/M2/research/wav2karaoke/audio_processing/output/syllables.csv")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-f", "--frequency", 
        required=True,
        help="Melody Frequency Information (.f0.csv)"
    )
    parser.add_argument(
        "-s", "--syllables",
        required=True,
        help="Syllables with timestamps data (.csv)"
    )
    parser.add_argument(
        "-g", "--grid", 
        required=True,
        help="Phone and word level lyrics alignment with timestamps. MFA output. (.textgrid)"
    )
    args = parser.parse_args()
    syllables = syllabification(args.grid, args.syllables)
    note_lyrics_alignment(args.frequency, syllables)

    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

    print(f"{BOLD}{GREEN}{'='*50}DONE{'='*50}{RESET}")