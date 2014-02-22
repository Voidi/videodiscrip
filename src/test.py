#!/usr/bin/env python3.3

import xml.dom.pulldom as pulldom
import xml.dom as dom
import os

#chapter data structure
chapters_timecode = [ {'length': 65.37,'display': [{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}]}, {'length': 1326.24,'display': [{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}]}, {'length': 0.09,'display': [{'language': "eng", 'name': "Chapter 1"}, {'language': "ger", 'name': "Kapitel 1"}]} ]

chapters_display = {'eng': ['Chapter 1', 'Chapter 2', 'Chapter 3'], 'ger': ['Kapitel 1', 'Kapitel 2', 'Kapitel 3']}

def createMetadataXML(metadata, template_file):
	doc = pulldom.parse(template_file)
	for event, node in doc:
		if event == pulldom.CHARACTERS:
			if node.nodeValue.startswith('%') and node.nodeValue.endswith('%'):
				print(node.nodeValue)
