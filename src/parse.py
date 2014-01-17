import re, argparse, dvdtrackrip, os, string

dvdsource = "/home/tobias/Videos/Serien/Ein Käfig voller Helden"

def getTracksInThreshold(dvdSourceInfo, thresholds):
	#threshold must be an array, but at the moment only the two first values are used
	tracksInThreshold = []
	#if only one threshold is passed, the value is used for both borders
	if len(thresholds) is 1:
		thresholds.append(str(int(thresholds[0].strip(string.ascii_letters)) + 1)+thresholds[0].strip(string.digits))
	#if the threshold contains a 'm', 'h' suffixes the values are counted as minutes or hours
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

def parseMapFile(mapfile):
	source_dest_file = open(mapfile, "r")
	source_dest_data = source_dest_file.readlines()
	source_dest_file.close()
	source_dest_map = []
	entryCounter = 0

	for i, line in enumerate(source_dest_data):
		if not re.search(r"^\ *#", line):

			#DVD Source Infos
			match = re.search(r"^([^\t@]*)@([^@]*)@(.*)$", line)
			if match:
				source_dest_map += [{'source_part': match.group(1), 'options': match.group(2), 'dest_part': match.group(3), 'tracks': []}]
				entryCounter = 0

				parser = argparse.ArgumentParser()
				parser.add_argument('-t', '--threshold', nargs='*')
				args = parser.parse_args(source_dest_map[-1]['options'].split())

				dvdSourceInfo = dvdtrackrip.getDvdTrackInfo(os.path.join(dvdsource, source_dest_map[-1]['source_part'].strip('/')), 0)
				for index, absolutetrack in enumerate(getTracksInThreshold(dvdSourceInfo, args.threshold)):
					source_dest_map[-1]['tracks'] += [{'absolutetrack': absolutetrack, 'basename': str(absolutetrack)}]
				#print(source_dest_map[-1]['tracks'])

			#detailed per Trackinfos
			match = re.search(r"^\t([^@]*)@([^@]*)@(.*)$", line)
			if match:
				try:
					source_dest_map[-1]['tracks'] += [{'absolutetrack': match.group(1), 'options': match.group(2), 'basename': match.group(3)}]
				except (IndexError, TypeError):
					raise MapParseError(i, line)

			#simple per Trackinfos
			match = re.search(r"^\t([^@\n]*)$", line)
			if match:
				try:
					source_dest_map[-1]['tracks'][entryCounter]['basename'] = match.group(1).strip()
					entryCounter += 1
				except (IndexError, TypeError):
					raise MapParseError(i, line)

			#Blanklines define the end of a dvdsource
			match = re.search(r"^\s$", line)
			if match:
				source_dest_map += [None]

	for dvdstructure in source_dest_map:
		if dvdstructure is None:
			source_dest_map.remove(dvdstructure)
	return source_dest_map

def parseBatchFile(batchFile):
	batchFile_handle = open(batchFile, "rt")
	batchFile_lines = batchFile_handle.readlines()
	batchFile_handle.close()

	batchJobs = []
	stack = []
	mappingOrder = []
	for lineNumber, lineOfFile in enumerate(batchFile_lines):
		#print("line: "+ str(lineNumber))
		if not lineOfFile.lstrip().startswith('#') and not lineOfFile.startswith('\n'):
			depth = lineOfFile.rstrip().count('\t')
			if lineOfFile.lstrip().startswith('%'):
				#Parse order of mapping variables

				#find all templatestring with sorrounding delimiters
				match = re.findall(r'([^(?<!\\)%]*)((?<!\\)%.*?(?<!\\)%)([^(?<!\\)%]*)', lineOfFile.strip())
				#generate the RegEx pattern, for Datamatching
				pattern = r''+''.join([re.escape(match[i][0])+'(.*?)'+re.escape(match[i][2]) for i in range(len(match))])+'$'
				#save pattern in correct structurdepth
				mappingOrder.insert( depth, {'pattern': pattern,'template_strings': re.findall(r'(?<!\\)%(.*?)(?<!\\)%', lineOfFile.strip())} )
			else:
				#Parse the mapping data
				if depth < len(stack):
					del(stack[depth:len(stack)])
				#TODO
				#chapter Startcode ausnahme?
				#werte optional machen fallls weniger angeben
				#print(mappingOrder[depth]['template_strings'])
				#print(mappingOrder[depth])
				match = re.search(mappingOrder[depth]['pattern'], lineOfFile.strip())
				#print(match.groups())
				temp_stack = {}
				for index,template_string in enumerate(mappingOrder[depth]['template_strings']):
					temp_stack[template_string] = match.group(index+1)
				stack.append(temp_stack)
				print(stack)

	return mappingOrder
