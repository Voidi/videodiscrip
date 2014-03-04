#!/usr/bin/env python3.3

import os, ast, re, subprocess, tempfile

class SubProcessError(Exception):
	"""Exception raised forfor a non valid DVD structure.
	Attributes:
		source -- path to DvdStructure where the Error occurs
	"""
	def __init__(self, command, returncode, subprocess_stderror):
		self.command = command
		self.returncode = returncode
		self.subprocess_stderror = subprocess_stderror

class DvdTrackError(Exception):
	"""Exception raised for errors with nonvalid Track selection.
	Attributes:
		source -- path to DvdStructure where the Error occurs
		track --
	"""
	def __init__(self, source, track, subprocess_stderror):
		self.source = source
		self.track = track
		self.subprocess_stderror = subprocess_stderror

class DvdSourceError(Exception):
	"""Exception raised forfor a non valid DVD structure.
	Attributes:
		source -- path to DvdStructure where the Error occurs
	"""
	def __init__(self, source, subprocess_stderror):
		self.source = source
		self.subprocess_stderror = subprocess_stderror

commands = {'lsdvd': "lsdvd", 'mplayer': "mplayer", 'mencoder': "mencoder", 'mkvmerge' : "mkvmerge"}

#get Infos with lsdvd , returns pythonstructure
def getDvdTrackInfo(dvdsource, absolutetrack=0):
	process = subprocess.Popen( [commands['lsdvd'], "-savcOy", "-t", str(absolutetrack), dvdsource], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process.wait()
	stdout= process.stdout.read()
	stderr= process.stderr.read()
	if process.returncode == 0:
		return ast.literal_eval(stdout[8:])
	elif process.returncode == 5:
		#returncode 5 is used if the dvd didn't contains this tracknumber
		raise DvdTrackError(dvdsource, absolutetrack, stderr)
	elif process.returncode in (1, 2, 3):
		raise DvdSourceError(dvdsource, stderr)
	else:
		raise SubProcessError( " ".join([commands['lsdvd'], "-savcOy", "-t", str(absolutetrack), dvdsource]), process.returncode, stderr )

#get TrackIDs with mkvmerge from temporary ripped file, needed for robust merging, returns pythonstructure
def getVobTracks(vobSource):
	process = subprocess.Popen( [commands['mkvmerge'], "--identify", vobSource ], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process.wait()
	stdout= process.stdout.read()

	if process.returncode == 0:
		stdout = stdout.splitlines()
		vobTracks = { 'video': [], 'audio': []}
		for line in stdout:
			match = re.search("Track ID (\d*): video", line)
			if match:
				vobTracks['video'] += [match.group(1)]
			match = re.search("Track ID (\d*): audio", line)
			if match:
				vobTracks['audio'] += [match.group(1)]
		return vobTracks

	elif process.returncode in (1,2):
		raise FileNotFoundError("getVobTracks:", vobSource)
	else:
		#use stout as argument because mkvmerge don't write to stderr
		raise SubProcessError("getVobTracks", process.returncode, stdout)

#generic function to run all other extern commands
def runSubProcess(command):
	stdoutfile = open("stdout.log", 'a')
	stdoutfile.write( "Running:" + ' '.join(command) + "\n" )
	process = subprocess.Popen(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process.wait()
	stdout= process.stdout.read()
	stderr= process.stderr.read()
	stdoutfile.write(stdout + "\n")
	stdoutfile.close()
	if process.returncode is not 0:
		raise SubProcessError(command, process.returncode, stderr)
	return stdout

def ripTrack(dvdsource_Path, absolutetrack, chaptersData=None, tagsData=None):
	trackinfo = getDvdTrackInfo(dvdsource_Path, absolutetrack)
	workspace = os.path.abspath(os.path.curdir)

	#Rip media data from dvd without any conversion to a vob file
	mplayer_arguments =[ "-dvd-device", dvdsource_Path, "dvd://"+str(absolutetrack), "-dumpstream", "-dumpfile", os.path.join(workspace, "videotrack.vob") ]
	mplayer_stdout = runSubProcess([commands['mplayer']] + mplayer_arguments)

	#for each detected Vobsub stream rip von dvdstructure
	for subtitlestream in trackinfo['track'][0]['subp']:
		mencoder_arguments =["-quiet", "-dvd-device", dvdsource_Path, "dvd://"+str(absolutetrack), "-nosound", "-ovc", "frameno", "-o", "/dev/null"]
		mencoder_arguments +=["-slang", subtitlestream['langcode'], "-vobsuboutindex", "0", "-vobsuboutid", subtitlestream['langcode']]
		mencoder_arguments +=["-vobsubout", os.path.join(workspace, "subtitles_" + subtitlestream['langcode'])]
		mencoder_stdout = runSubProcess([commands['mencoder']] + mencoder_arguments)

	#get track ids from the ripped vob file, used in mkvmerge
	vobtracks = getVobTracks( os.path.join(workspace, "videotrack.vob") )

	mkvmerge_arguments = [ "-o", os.path.join(workspace, "muxedoutput.mkv"), "--forced-track", str(vobtracks['video'][0])+":no", "--display-dimensions", str(vobtracks['video'][0])+":"+str(trackinfo['track'][0]['width'])+"x"+str(trackinfo['track'][0]['height']) ]

	#muxing options for audiostreams
	for index, audiostream in enumerate(trackinfo['track'][0]['audio']):
		mkvmerge_arguments +=["--default-track", str(vobtracks['audio'][index])+":no", "--forced-track", str(vobtracks['audio'][index])+":no", "--language", str(vobtracks['audio'][index])+":"+audiostream['langcode']]
	mkvmerge_arguments +=[ "-a", ','.join(vobtracks['audio']), "-d", "0", "-S", "-T", "--no-global-tags", "--no-chapters", os.path.join(workspace, "videotrack.vob") ]

	for subtitlestream in trackinfo['track'][0]['subp']:
		mkvmerge_arguments +=[ "--language", "0:"+subtitlestream['langcode'], "--default-track", "0:no", "--forced-track", "0:no", "-s", "0", "-D", "-A", "-T", "--no-global-tags", "--no-chapters", os.path.join(workspace, "subtitles_" + subtitlestream['langcode'] + ".idx") ]

	#use the XML data from parameters to write metadata in files
	if chaptersData is not None:
		chaptersXML_file = open(os.path.join(workspace, "chapters.xml"), "w")
		chaptersData.writexml(chaptersXML_file, '\t', '\t', '\n', encoding="UTF-8")
		chaptersXML_file.close()
		mkvmerge_arguments += ["--chapter-charset", "UTF8", "--chapters", os.path.join(workspace, "chapters.xml") ]
	if tagsData is not None:
		tagsXML_file = open(os.path.join(workspace, "tags.xml"), "w")
		tagsData.writexml(tagsXML_file, '\t', '\t', '\n', encoding="UTF-8")
		tagsXML_file.close()
		mkvmerge_arguments += [ "--global-tags", os.path.join(workspace, "tags.xml") ]

	mkvmerge_output =runSubProcess([commands['mkvmerge']] + mkvmerge_arguments)

def dvdtrackrip(dvdsource_Path, absolutetrack, destinationPath, chaptersData=None, tagsData=None):
	if os.environ.get('TEMP'):
		tempfile.tempdir = os.environ.get('TEMP')
	else:
		tempfile.tempdir = os.path.dirname(destinationPath)
	workspace = tempfile.mkdtemp(prefix="dvdtrackrip_", suffix="_" + os.path.basename(destinationPath))

	os.chdir(workspace)
	try:
		ripTrack(dvdsource_Path, absolutetrack, chaptersData=chaptersData, tagsData=tagsData)
	except SubProcessError as error:
		errorlog = open(os.path.join(workspace, "error.log"), 'w')
		errorlog.write( "\nCommand:" + error.args[0])
		errorlog.write( "\nReturncode:" + str(error.args[1]) )
		errorlog.write( "\nSubprocessor stderr: " + error.args[2] )
		errorlog.close()
		raise
	else:
		# if not os.path.join(workspace, "muxedoutput.mkv"):
		# 	raise FileNotFoundError("dvdtrackrip:", os.path.join(workspace, "muxedoutput.mkv"))
		return os.path.join(workspace, "muxedoutput.mkv")
	finally:
		os.chdir("..")
