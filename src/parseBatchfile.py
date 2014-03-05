#!/usr/bin/env python3

import re, os
from helper import rippingJob

class  SyntaxError(Exception):
	"""Exception raised for nonvalid Batchfile Syntax.

	Attributes:
		linenumber --

	"""
	def __init__(self, linenumber):
		self.linenumber = linenumber

def mergeStack_parts(*stackParts):
	output = rippingJob()
	for part in stackParts:
		output += part
	return output

def parseBatchFile(batchFile_handle):
	batchFile_lines = batchFile_handle.readlines()

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

				#iterate over all variables defined in the template, and check against it's pattern
				startPos = 0
				jobStack_Part = {'OPTIONS':{}, 'METADATA':{}, 'CHAPTERDATA':{}}
				for index in range(0, len(mappingOrder[depth])):
					variablePattern = re.compile(mappingOrder[depth][index]['pattern'])
					match = variablePattern.search(lineOfFile.strip(), startPos)
					startPos = match.end()
					#if some variables are not filled, go to next line
					if startPos == len(lineOfFile):
						break
					#append value of current variable to a dictionary holding all data of the current line
					if mappingOrder[depth][index]['template_string'] in ("SOURCE_PATH", "OUTPUT_PATH"):
						jobStack_Part.update({mappingOrder[depth][index]['template_string']: os.path.join(os.path.dirname(os.path.abspath(batchFile_handle.name)), match.group(1))})
					elif mappingOrder[depth][index]['template_string'] in ("OUTPUT_FILENAME", "THRESHOLD"):
						jobStack_Part['OPTIONS'].update({mappingOrder[depth][index]['template_string']: match.group(1)})
					elif mappingOrder[depth][index]['template_string'] in ("METATAGS_TEMPLATEFILE"):
						jobStack_Part['OPTIONS'].update({mappingOrder[depth][index]['template_string']: os.path.join(os.path.dirname(os.path.abspath(batchFile_handle.name)), match.group(1)) })
					elif mappingOrder[depth][index]['template_string'][:15] == "CHAPTER_TITLES_":
						jobStack_Part['CHAPTERDATA'].update({mappingOrder[depth][index]['template_string'][15:]: match.group(1).split('%')})
					else:
						jobStack_Part['METADATA'][mappingOrder[depth][index]['template_string']] = match.group(1)

				#check if we are on a higher level on the mapping tree then before
				#also immply that lines have parsed before
				if depth < len(jobStack):

					#then delete all parts under the current level on the stack
					del(jobStack[depth:])

					#if the current line contains a "SOURCE_PATH-PART", this must be a new VideoSource
					#TODO: match only a the last level SOURCE_PATH-PART
					if "SOURCE_PATH" in jobStack_Part:
						jobQueue.append({'Control': "newVideoSource"})
						trackCounter = 0

				#append data of current line to stack, holding all data of current higher levels
				jobStack.append(rippingJob(jobStack_Part))
				#check if this is the last line or if next line isn't on a deeper level
				if lineNumber == len(batchFile_lines)-1 or depth >= batchFile_lines[lineNumber+1].rstrip().count('\t'):
					trackCounter += 1
					mergedStack = mergeStack_parts(*jobStack)
					mergedStack.TRACKNUMBER = trackCounter
					jobQueue.append(mergedStack)

	return jobQueue
