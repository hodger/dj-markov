# dj-markov
Generate Markov chains in the style of your favorite artists!

DJMarkov works by querying the MusicBrainz metadata database. It finds albums by the artist you specify, and creates a Markov
chain with as many songs as it can find the lyrics to. Lyrics are found via LyricsWikia, using the PyLyrics library.

#Dependencies
You can install DJMarkov's dependencies through pip:
```
pip install musicbrainzngs
pip install PyLyrics
```

#Usage

Run `python djmarkov.py "your-artist"`

You can optionally specify a limit to the number of songs used. Otherwise, all available songs are used.

```
usage: djmarkov.py [-h] artist [song_limit]

Let DJMarkov spit fire in the style of your favorite artist.

positional arguments:
  artist      artist whose style DJMarkov will attempt to imitate
  song_limit  how many songs to use. Defaults to all available songs.

optional arguments:
  -h, --help  show this help message and exit
```
