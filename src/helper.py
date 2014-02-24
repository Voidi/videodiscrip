import os

class rippingJob:
	"""contains all Information for ONE ripping job"""

	def __init__(self, jobStack_Part=None):
		if jobStack_Part is None:
			self.SOURCE_PATH = ""
			self.OUTPUT_PATH = ""
			self.TRACKNUMBER = 0
			self.OPTIONS = {}
			self.METADATA = {}
			self.CHAPTERDATA = {}
		elif isinstance(jobStack_Part, dict):
			self.SOURCE_PATH = jobStack_Part.get('SOURCE_PATH','')
			self.OUTPUT_PATH = jobStack_Part.get('OUTPUT_PATH','')
			self.TRACKNUMBER = jobStack_Part.get('TRACKNUMBER',0)
			self.OPTIONS = jobStack_Part.get('OPTIONS','')
			self.METADATA = jobStack_Part.get('METADATA','')
			self.CHAPTERDATA = jobStack_Part.get('CHAPTERDATA','')

	def __str__(self):
		return self.SOURCE_PATH + ":" + str(self.TRACKNUMBER) + " -> "+ self.OUTPUT_PATH + "\n" + "OPTIONS:" + str(self.OPTIONS) + "\n" + "METADATA:" + str(self.METADATA) + "\n" + "CHAPTERDATA:" + str(self.CHAPTERDATA)

	def __add__(self, other):
		if isinstance(other, rippingJob):
			result = rippingJob()
			result.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.SOURCE_PATH)
			result.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.OUTPUT_PATH)
			result.TRACKNUMBER = other.TRACKNUMBER
			result.OPTIONS.update(self.OPTIONS)
			result.OPTIONS.update(other.OPTIONS)
			result.METADATA.update(self.METADATA)
			result.METADATA.update(other.METADATA)
			result.CHAPTERDATA.update(self.CHAPTERDATA)
			result.CHAPTERDATA.update(other.CHAPTERDATA)
			return result
		elif isinstance(other, dict):
			result = batchJob()
			result.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.get('SOURCE_PATH', ''))
			result.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.get('OUTPUT_PATH', ''))
			result.TRACKNUMBER = other.get('TRACKNUMBER')
			result.OPTIONS.update(self.get('OPTIONS'))
			result.OPTIONS.update(other.get('OPTIONS'))
			result.METADATA.update(self.get('METADATA'))
			result.METADATA.update(other.get('METADATA'))
			result.CHAPTERDATA.update(self.get('CHAPTERDATA'))
			result.CHAPTERDATA.update(other.get('CHAPTERDATA'))
			return result

	def __iadd__(self, other):
		if isinstance(other, rippingJob):
			self.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.SOURCE_PATH)
			self.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.OUTPUT_PATH)
			self.TRACKNUMBER = other.TRACKNUMBER
			self.OPTIONS.update(other.OPTIONS)
			self.METADATA.update(other.METADATA)
			self.CHAPTERDATA.update(other.CHAPTERDATA)
			return self
		elif isinstance(other, dict):
			self.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.get('SOURCE_PATH', ''))
			self.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.get('OUTPUT_PATH', ''))
			self.TRACKNUMBER = other.get('TRACKNUMBER')
			self.OPTIONS.update(other.get('OPTIONS'))
			self.METADATA.update(other.get('METADATA'))
			self.CHAPTERDATA.update(other.get('CHAPTERDATA'))
			return self

from datetime import timedelta
import xml.dom.minidom

def generateChaptersXML(chapters_timecode, chapters_display):
	#chapterstime_code must be the content of 'chapter' from the lsdvd info
	implementation = xml.dom.minidom.getDOMImplementation()
	doctype = implementation.createDocumentType('Chapters', '', 'matroskachapters.dtd')
	xmlDocument = implementation.createDocument(None,'Chapters', doctype=doctype)

	xmlDocument.lastChild.appendChild(xmlDocument.createElement("EditionEntry"))
	chapterEdition = xmlDocument.lastChild.lastChild
	chapterEdition.appendChild(xmlDocument.createElement("EditionFlagHidden")).appendChild(xmlDocument.createTextNode('0'))
	chapterEdition.appendChild(xmlDocument.createElement("EditionFlagDefault")).appendChild(xmlDocument.createTextNode('0'))

	chapterStarttime = 0
	for chapter_index, chapter in enumerate(chapters_timecode):
		chapterAtom = chapterEdition.appendChild(xmlDocument.createElement("ChapterAtom"))
		chapterAtom.appendChild(xmlDocument.createElement("ChapterTimeStart")).appendChild(xmlDocument.createTextNode(str(timedelta(seconds=chapterStarttime))))
		chapterStarttime += chapter['length']
		chapterAtom.appendChild(xmlDocument.createElement("ChapterFlagHidden")).appendChild(xmlDocument.createTextNode('0'))
		chapterAtom.appendChild(xmlDocument.createElement("ChapterFlagEnabled")).appendChild(xmlDocument.createTextNode('1'))

		if chapter_index >= len(chapters_display):
			continue

		for chapter_langTitle in sorted(chapters_display[chapter_index], key=lambda k: k['title']):
			chapterDisplay = chapterAtom.appendChild(xmlDocument.createElement("ChapterDisplay"))
			chapterDisplay.appendChild(xmlDocument.createElement("ChapterString")).appendChild(xmlDocument.createTextNode(chapter_langTitle['title']))
			chapterDisplay.appendChild(xmlDocument.createElement("ChapterLanguage")).appendChild(xmlDocument.createTextNode(chapter_langTitle['language']))

	return xmlDocument

def chapter_formatRestructure(structInput):
	#reformat from.
	#{'eng': ['Chapter 1', 'Chapter 2', 'Chapter 3'], 'ger': ['Kapitel 1', 'Kapitel 2', 'Kapitel 3']}
	#to:
	#[{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}], [{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}], [{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}]

	structOutput = []
	for language in structInput.keys():
		for index, title in enumerate(structInput[language]):
			if len(structOutput) <= index:
				structOutput.append([])
			structOutput[index].append({'language': language, 'title': title})
	return structOutput

import string, re

def getTracksInThreshold(diskSourceInfo, *PARAM_thresholds):
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

	for index in diskSourceInfo['track']:
		if round(index['length']) in range( int(thresholds[0]), int(thresholds[1]) ):
			tracksInThreshold += [index['ix']]
	return tracksInThreshold
