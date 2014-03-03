videodiscrip
============
Rip tracks from a DVD Strukture into .mkv containers without reencoding.
There a two modes:
- Single mode: rip a single Track, specifying options on the commandline
- Batch mode: Using a mapfile, it is capable to rip automatical Media from different Sources applying indvidual Metadata and filenames to each file.

Dependencies
------------
- **python3** - minnimum version 3.3
- **mplayer** - extraction of video/audio data from DVD structure
- **mencoder** - extraction of Vobsub subtitlestream from DVD structure
- **mkvmerge** - from [mkvtoolnix](http://www.bunkus.org/videotools/mkvtoolnix/), merging all extracted data into one .mkv file with proper metadata


Installation
------------

Usage
-----
**Attention**
Usage of Batch-Mode is currently extremly buggy, didnt support tags, chapter or conversion

TODO
----

