#!/usr/bin/env python3.3

import dvdtrackrip
from copy import deepcopy
from datetime import timedelta
import xml.dom.minidom as minidom


dvdsource = "/home/tobias/Videos/Serien/Die Mumins/Mumin Box1 Dvd1"
#dvdinfo = dvdtrackrip.getDvdTrackInfo(dvdsource, 1)
dvdinfo = {'device': '/home/tobias/Videos/Serien/Die Mumins/Mumin Box1 Dvd1', 'track': [{'width': 720, 'vts': 1, 'audio': [{'content': 'Undefined', 'langcode': 'de', 'language': 'Deutsch', 'quantization': 'drc', 'channels': 2, 'ix': 1, 'streamid': '0x80', 'frequency': 48000, 'ap_mode': 0, 'format': 'ac3'}], 'fps': 25.0, 'chapter': [{'ix': 1, 'length': 65.37, 'startcell': 1}, {'ix': 2, 'length': 1326.24, 'startcell': 2}, {'ix': 3, 'length': 0.09, 'startcell': 3}], 'ix': 1, 'length': 1392.09, 'vts_id': 'DVDVIDEO-VTS', 'aspect': '4/3', 'height': 576, 'df': '?', 'ttn': 1, 'subp': [], 'format': 'PAL'}], 'provider_id': '', 'vmg_id': 'DVDVIDEO-VMG', 'title': 'unknown'}
chapters = deepcopy(dvdinfo['track'][0]['chapter'])

def getChapters(chapters):
	for index,chapter in enumerate(chapters):
		chapters[index]['display'] = [{'language': "eng", 'name': "Chapter " + str(index)}, {'language': "ger", 'name': "Kapitel " + str(index)}]

	implementation = minidom.getDOMImplementation()
	doctype = implementation.createDocumentType('Chapters', '', 'matroskachapters.dtd')
	xmlDocument = implementation.createDocument(None,'Chapters', doctype=doctype)

	xmlDocument.lastChild.appendChild(xmlDocument.createElement("EditionEntry"))
	chapterEdition = xmlDocument.lastChild.lastChild
	chapterEdition.appendChild(xmlDocument.createElement("EditionFlagHidden")).appendChild(xmlDocument.createTextNode('0'))
	chapterEdition.appendChild(xmlDocument.createElement("EditionFlagDefault")).appendChild(xmlDocument.createTextNode('0'))

	chapterStarttime = 0
	for chapter in chapters:
		chapterAtom = chapterEdition.appendChild(xmlDocument.createElement("ChapterAtom"))
		chapterAtom.appendChild(xmlDocument.createElement("ChapterTimeStart")).appendChild(xmlDocument.createTextNode(str(timedelta(seconds=chapterStarttime))))
		chapterStarttime += chapter['length']
		chapterAtom.appendChild(xmlDocument.createElement("ChapterFlagHidden")).appendChild(xmlDocument.createTextNode('0'))
		chapterAtom.appendChild(xmlDocument.createElement("ChapterFlagEnabled")).appendChild(xmlDocument.createTextNode('1'))

		for chapter_langTitle in chapter['display']:
				chapterDisplay = chapterAtom.appendChild(xmlDocument.createElement("ChapterDisplay"))
				chapterDisplay.appendChild(xmlDocument.createElement("ChapterString")).appendChild(xmlDocument.createTextNode(chapter_langTitle['name']))
				chapterDisplay.appendChild(xmlDocument.createElement("ChapterLanguage")).appendChild(xmlDocument.createTextNode(chapter_langTitle['language']))

	return xmlDocument

chapterXML_file = open("chapters.xml", "w")
getChapters(chapters).writexml(chapterXML_file, '\t', '\t', '\n', encoding="UTF-8")
chapterXML_file.close()
