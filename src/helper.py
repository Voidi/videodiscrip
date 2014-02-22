import string, re, os

class rippingJob:
	"""contains all Information for ONE ripping job"""

	def __init__(self, jobStack_Part=None):
		if jobStack_Part is None:
			self.SOURCE_PATH = ""
			self.OUTPUT_PATH = ""
			self.SOURCE_TRACKNUMBER = 0
			self.OPTIONS = {}
			self.METADATA = {}
			self.CHAPTERDATA = {}
		elif isinstance(jobStack_Part, dict):
			self.SOURCE_PATH = jobStack_Part.get('SOURCE_PATH','')
			self.OUTPUT_PATH = jobStack_Part.get('OUTPUT_PATH','')
			self.SOURCE_TRACKNUMBER = jobStack_Part.get('SOURCE_TRACKNUMBER',0)
			self.OPTIONS = jobStack_Part.get('OPTIONS','')
			self.METADATA = jobStack_Part.get('METADATA','')
			self.CHAPTERDATA = jobStack_Part.get('CHAPTERDATA','')

	def __str__(self):
		return self.SOURCE_PATH + ":" + str(self.SOURCE_TRACKNUMBER) + " -> "+ self.OUTPUT_PATH + "\n" + "OPTIONS:" + str(self.OPTIONS) + "\n" + "METADATA:" + str(self.METADATA) + "\n" + "CHAPTERDATA:" + str(self.CHAPTERDATA)

	def __add__(self, other):
		if isinstance(other, rippingJob):
			result = rippingJob()
			result.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.SOURCE_PATH)
			result.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.OUTPUT_PATH)
			result.SOURCE_TRACKNUMBER = other.SOURCE_TRACKNUMBER
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
			result.SOURCE_TRACKNUMBER = other.get('SOURCE_TRACKNUMBER')
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
			self.SOURCE_TRACKNUMBER = other.SOURCE_TRACKNUMBER
			self.OPTIONS.update(other.OPTIONS)
			self.METADATA.update(other.METADATA)
			self.CHAPTERDATA.update(other.CHAPTERDATA)
			return self
		elif isinstance(other, dict):
			self.SOURCE_PATH = os.path.join(self.SOURCE_PATH, other.get('SOURCE_PATH', ''))
			self.OUTPUT_PATH = os.path.join(self.OUTPUT_PATH, other.get('OUTPUT_PATH', ''))
			self.SOURCE_TRACKNUMBER = other.get('SOURCE_TRACKNUMBER')
			self.OPTIONS.update(other.get('OPTIONS'))
			self.METADATA.update(other.get('METADATA'))
			self.CHAPTERDATA.update(other.get('CHAPTERDATA'))
			return self

def chapter_formatRestructure(input):
	output = []
	for language in input.keys():
		for index, title in enumerate(chapters_display[language]):
			if len(output) <= index:
				output.append([])
			output[index].append({'language': language, 'name': title})
	return output

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
