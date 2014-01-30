#!/usr/bin/env python3.3

import re, os, string

class BatchSytanxError(Exception):
	"""Exception raised for nonvalid Batchfile Syntax.

	Attributes:
		linenumber --

	"""
	def __init__(self, linenumber):
		self.linenumber = linenumber

def getTracksInThreshold(dvdSourceInfo, *PARAM_thresholds):
	thresholds = list(PARAM_thresholds)
	for threshold in thresholds:
		if not re.match(r'^\d*[mh]?$', threshold):
			raise ArgumentError("")
	#threshold must be an array, but at the moment only the two first values are used
	tracksInThreshold = []
	#if only one threshold is passed, the value is used for both borders
	if len(thresholds) is 1:
		thresholds.append(str(int(thresholds[0].strip(string.ascii_letters)) + 1)+thresholds[0].strip(string.digits))
	#if the threshold contains a 'm', 'h' suffixes the values are interpreted as minutes or hours
	#for comparing with lsdvd these are converted in seconds
	for i, value in enumerate(thresholds):
		if 'm' in value:
			thresholds[i] = int(value.strip(string.ascii_letters)) * 60
		if 'h' in value:
			thresholds[i] = int(value.strip(string.ascii_letters)) * 3600

	for index in dvdSourceInfo['track']:
		if round(index['length']) in range( int(thresholds[0]), int(thresholds[1]) ):
			tracksInThreshold += [index['ix']]
	return tracksInThreshold

def mergeStack_parts(*stackParts):
	mergedStack = {'metaData': {}}

	for stack in stackParts:
		for key in stack.keys():
			if key == "SOURCE_PATH-PART" or key == "OUTPUT_PATH-PART":
				mergedStack[key] = os.path.normpath(os.path.join(mergedStack.get(key,''),stack.get(key,'')))
			elif key == "OPTIONS":
				mergedStack[key] = " ".join({mergedStack.get(key,''),stack.get(key,'')})
			else:
				mergedStack['metaData'][key] = "".join({str(mergedStack.get(key,'')),str(stack.get(key,''))})
	return mergedStack
"""
	#First variant
	keys = set().union(*stackParts)
	for key in keys:
		if key == "SOURCE_PATH-PART" or key == "OUTPUT_PATH-PART":
			mergedStack[key] = os.path.normpath(os.path.join(*[part.get(key,'') for part in stackParts]))
		elif key == "OPTIONS":
			mergedStack[key] = " ".join(str(part.get(key,'')) for part in stackParts)
		else:
			mergedStack[key] = "".join(str(part.get(key,'')) for part in stackParts)
"""

def parseBatchFile(batchFile_handle):
	#batchFile_handle = open(batchFile, "rt")
	batchFile_lines = batchFile_handle.readlines()
	#batchFile_handle.close()

	jobQueue = []
	jobStack = []
	mappingOrder = []
	trackCounter = 0
	for lineNumber, lineOfFile in enumerate(batchFile_lines):
		#unless the line starts with '#' or is empty there should be data for us
		if not lineOfFile.lstrip().startswith('#') and not lineOfFile.strip() is "":

			#get depth in the mapping tree
			depth = lineOfFile.rstrip().count('\t')
			if lineOfFile.lstrip().startswith('%'):
				#Parse data template

				#find all variable templates with surrounding delimiters
				match = re.findall(r'([^(?<!\\)%]*)((?<!\\)%.*?(?<!\\)%)([^(?<!\\)%]*)', lineOfFile.strip())
				#generate the Datamatching-RegEx pattern foreach variable
				pattern = []
				for i in range(len(match)):
					if re.escape(match[i][2]) is '':
					#special case for the variable at end of line
						pattern += [{'template_string': match[i][1].lstrip('%').rstrip('%'), 'pattern': r''+re.escape(match[i][0])+'(.*?)(\Z)'}]
					else:
						pattern += [{'template_string': match[i][1].lstrip('%').rstrip('%'), 'pattern': r''+re.escape(match[i][0])+'(.*?)('+re.escape(match[i][2])+'|\Z)'}]
				mappingOrder.insert( depth, pattern)

			else:
				#Parse data structure

				#iterate over all variables defined in the template
				startPos = 0
				jobStack_Part = {}
				for index in range(0, len(mappingOrder[depth])):
					pattern = re.compile(mappingOrder[depth][index]['pattern'])
					match = pattern.search(lineOfFile.strip(), startPos)
					startPos = match.end()
					#if some variables are not filled, go to next line
					if startPos == len(lineOfFile):
						break
					#append value of current variable to a dictionary holding all data of the current line
					jobStack_Part[mappingOrder[depth][index]['template_string']] = match.group(1)

				#check if we are on a higher level on the mapping tree then before
				#also immply that lines have parsed before
				if depth < len(jobStack):

					#then delete all parts under the current level on the stack
					del(jobStack[depth:])

					#if the current line contains a "SOURCE_PATH-PART", this must be a new VideoSource
					if "SOURCE_PATH-PART" in jobStack_Part:
						jobQueue.append({'Control': "newVideoSource"})
						trackCounter = 0

				#append data of current line to stack, holding all data of current higher levels
				jobStack.append(jobStack_Part)
				#check if next line isn't on a deeper level
				if lineNumber == len(batchFile_lines)-1 or depth >= batchFile_lines[lineNumber+1].rstrip().count('\t'):
					trackCounter += 1
					mergedStack = mergeStack_parts(*jobStack)
					mergedStack['SOURCE_TRACKNUMBER'] = trackCounter
					jobQueue.append(mergedStack)

	return jobQueue
