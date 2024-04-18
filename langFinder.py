from langdetect import detect

lyrics = "Jemmapel Claude"
try:
    language = detect(lyrics)
    print(f"The language of the song is: {language}")
except Exception as e:
    print("Could not detect language:", e)