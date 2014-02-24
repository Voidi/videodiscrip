#!/usr/bin/env python3.3

import re
from datetime import timedelta
import xml.dom.minidom

def generateChaptersXML(chapters_timecode, chapters_display):
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

		for chapter_langTitle in chapters_display[chapter_index]:
				chapterDisplay = chapterAtom.appendChild(xmlDocument.createElement("ChapterDisplay"))
				chapterDisplay.appendChild(xmlDocument.createElement("ChapterString")).appendChild(xmlDocument.createTextNode(chapter_langTitle['name']))
				chapterDisplay.appendChild(xmlDocument.createElement("ChapterLanguage")).appendChild(xmlDocument.createTextNode(chapter_langTitle['language']))

	return xmlDocument

def generateMetatagsXML(tags_data, template_file):
	template_data = template_file.read()
	for item in tags_data:
		replaceString = '%' + item + '%'
		template_data = template_data.replace(replaceString, tags_data[item])
	#everthing else enclosed with '%' are variables where we don't have any values
	tags_xml = re.sub(r'(?<!\\)%.*?(?<!\\)%', "", template_data)

	return tags_xml
