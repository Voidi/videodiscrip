videodiskrip
============
Rip tracks from a DVD Strukture into .mkv containers without reencoding.
There a two modes:
- Direct mode: rip a from a single Source, specifying options on the commandline #TODO: maybe without metadata
- Batch mode: Using a mapfile, it is capable to rip automatical Media from different Sources applying individual Metadata and filenames to each file.

Dependencies
------------
- **python3** - minnimum version 3.3
- **mplayer** - extraction of video/audio data from DVD structure
- **mencoder** - extraction of Vobsub subtitlestream from DVD structure
- **mkvmerge** - from [mkvtoolnix](http://www.bunkus.org/videotools/mkvtoolnix/), merging all extracted data into one .mkv file with proper
metadata

Optional:

- **[vobsub2srt](https://github.com/ruediger/VobSub2SRT)** - convert Vobsub to SubRip subtitles format
- **aspell** - check SubRip file for conversion errors

Tesserat and Aspell need additional packages depending which language you want process

Installation
------------

Usage
-----
**Attention**
Usage of Batch-Mode is currently extremly buggy, didnt support tags, chapter or conversion

TODO
----
- better error handling with subtitle conversion problems
