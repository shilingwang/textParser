# -*- coding: utf-8 -*-
import sys
sys.path.append("../pyparsing-2.1.10")
import os
import xml.etree.ElementTree as ET
import operator
from pyparsing import *
import csv
import re

class chromatin:
	
	def __init__(self, name, mode):
		self.mapPath = "./maps"
		self.savePath = "../csv"
		self.txtPath = "../txt"
		self.xmlPath = "../xml"
		self.mode = mode
		if self.mode == 0:
                    self.xMap = os.path.join(self.mapPath, "x_map.dat")
                    self.xHat = os.path.join(self.mapPath, "x_hat.dat")
                    self.yMap = os.path.join(self.mapPath, "y_map.dat")
                    self.yHat = os.path.join(self.mapPath, "y_hat.dat")
                    self.zMap = os.path.join(self.mapPath, "z_map.dat")
                    self.zHat = os.path.join(self.mapPath, "z_hat.dat")
                    self.histone = self.buildDict(self.xHat, self.xMap)
                    self.position = self.buildDict(self.yHat, self.yMap)
                    self.modif = self.buildDict(self.zHat, self.zMap)
                else:
                    self.myHat = os.path.join(self.mapPath, mode+"_hat.dat")
                    self.myMap = os.path.join(self.mapPath, mode+"_map.dat")
                    self.myDict = self.buildDict(self.myHat, self.myMap)
                    self.eventHat = os.path.join(self.mapPath, "event_hat.dat")
                    self.eventMap = os.path.join(self.mapPath, "event_map.dat")
                    self.event = self.buildDict(self.eventHat, self.eventMap)
		if len(name) == 1:
			self.pmid = name[0]
		else:
			self.pmid = name[1]
		self.xml = os.path.join(self.xmlPath, name[0]+".txt.xml")
		self.txtFile = os.path.join(self.txtPath, name[0]+".txt")
		f = open(self.txtFile)
		self.txtContent = f.read().lower()
		self.sectionPos = self.sectionList()
		
		
	def sectionList(self):
		sectionDict = {'ABSTRACT':['abstract', 'summary'],
		'INTRO':['introduction', 'background'],
		'RESULTS':['results'],
		'CONCLUSION':['conclusion'],
		'DISCUSSION':['discussion'],
		'METHOD':['method', 'experimental procedures', 'material and methods'],
		'REFERENCES':['references']}
		sectionPos = {}
		sectionPos['HEAD'] = [0]
		for item in sectionDict:
			keywords = sectionDict[item]
			sectionPos[item] = []
			for keyword in keywords:
				pattern1 = keyword + '\n'
				pattern2 = keyword + ' \n'
				start = 0
				while start < len(self.txtContent):
					loc1 = self.txtContent.find(pattern1, start)
					if loc1 == -1:
						loc2 = self.txtContent.find(pattern2,start)
						if loc2 != -1:
							sectionPos[item].append(loc2)
							start = loc2 + 1
						else:
							break
					else:
						sectionPos[item].append(loc1)
						start = loc1 + 1
			if len(sectionPos[item]) == 0:
				sectionPos.pop(item)
		if 'RESULTS' in sectionPos and 'DISCUSSION' in sectionPos:
			if len(sectionPos['RESULTS'])>1:
				if len(sectionPos['DISCUSSION'])>1:
					sectionPos['DISCUSSION'] = [max(sectionPos['DISCUSSION'])]
				i=0
				while i < len(sectionPos['RESULTS']):
					if sectionPos['RESULTS'][i] > sectionPos['DISCUSSION']:
						sectionPos['RESULTS'].pop(i)
					else:
						i += 1
		for item in sectionPos:
			sectionPos[item] = max(sectionPos[item])
		sortedPos = sorted(sectionPos.items(), key = operator.itemgetter(1))
		return sortedPos
		
	def buildDict(self, *args):
		dictionary = []
		hatFile = args[0]
		f1 = open(hatFile, 'r')
		for line in f1:
			line = line.replace("\r\n","")
			line = line.replace("\n", "")
			if line == "":
				continue
			dictionary.append((line.lower(), line))
		if len(args) > 1:
			mapFile = args[1]
			f2 = open(mapFile, 'r')
			for line in f2:
				line = line.replace("\r\n","")
				line = line.replace("\n", "")
				if line == "":
					continue
				values = line.split('\t')
				if values[1] == "":
					continue
				dictionary.append((values[1].lower(), values[0]))
		lists = Or(((CaselessLiteral(s).setName(s)).setParseAction(replaceWith(v))) for s,v in dictionary)
		grammar = lists.leaveWhitespace()
		return grammar

	
	def sentenceParser(self):
		tree = ET.parse(self.xml)
		root = tree.getroot()
		for sentence in root[0][0]:
			sentenceID = sentence.attrib['id']
			toParse = []
			toShow = []
			position = sentence[0][0][2].text
			for token in sentence[0]:
				word = token[0].text
				lemma = token[1].text
				if word=="-LRB-":
					word = "("
					lemma = "("
				elif word=="-RRB-":
					word = ")"
					lemma = ")"
				toParse.append(lemma)
				toShow.append(word)
			toParse = " ".join(toParse).encode("utf-8", "ignore")
			if self.mode == 0:
                            entities = self.chromatinGrammar(toParse)
                        else:
                            entities = self.singleDictParser(self.mode, toParse)
                        if len(entities)>0:
                                section = ""
                                for item in self.sectionPos:
                                        if int(position) >= item[1]:
                                                section = item[0]
                                        else:
                                                break
                                self.save(section, entities, toShow, sentenceID, self.mode)

                            
        
        
        def singleDictParser(self, mode, toParse):
            myGrammar = (WordStart() + self.myDict + WordEnd())
            eventGrammar = (WordStart() + self.event + WordEnd())
            ParserElement.enablePackrat()
            results = myGrammar.searchString(toParse)
            entityList = []
            if len(results) > 0:
                eventResult = eventGrammar.searchString(toParse)
                event = ""
                if len(eventResult)>0:
                    event = "/".join(it[0] for it in eventResult)
                    event = "|" + event
                for item in results:
                    entityList.append(item[0]+event)
            return entityList
        
        
        
	def save(self, section, entityList, sentence, sentenceID, saveMode):
		strSentence = " ".join(sentence).encode("utf-8", "ignore")
		strSentence = strSentence.replace(" .", ".")
		if saveMode == 0:
                    savePath = self.savePath + "/histone"
                else:
                    savePath = self.savePath + "/" + saveMode
                if not os.path.exists(savePath):
                    os.makedirs(savePath)
                saveName = os.path.join(savePath, self.pmid+".csv")
		with open(saveName, 'a+') as csvFile:
			resultWriter = csv.writer(csvFile, delimiter = '\t')
			for entity in entityList:
				resultWriter.writerow([self.pmid,section, sentenceID,entity, strSentence])
	
	def chromatinGrammar(self, toParse):
		chromatin_x = (WordStart() + self.histone + WordEnd())
		chromatin_y = (WordStart() + self.position + WordEnd()).setResultsName('y')
		chromatin_z = (WordStart() + self.modif + WordEnd()).setResultsName('z')
		chromatin_xyz = (WordStart() + self.histone + ZeroOrMore(self.position) + ZeroOrMore(self.modif) + WordEnd())
		chromatin_xyz_space = (chromatin_x + ZeroOrMore(chromatin_y) + ZeroOrMore(chromatin_z))
		chromatin_multi = (WordStart() + self.histone + OneOrMore(self.position+self.modif) + WordEnd()).setResultsName('multi')
		
		chromatin_full = (Or([chromatin_xyz.setResultsName('xyz'), chromatin_xyz_space.setResultsName('xyz')]))
		chromatin_yz = (Or([chromatin_y, chromatin_z]))
		chromatin = Or([chromatin_full, chromatin_yz, chromatin_multi])
		
		ParserElement.enablePackrat()
		pieces = commaSeparatedList.parseString(toParse)
		entityList = []
		for piece in pieces:
			results = chromatin.searchString(piece)
			if len(results) != 0:
				entitiesPiece = self.getEntity(results)
				if len(entitiesPiece) != 0:
					for entity in entitiesPiece:
						strEntity = "".join(entity)
						if entity not in entityList:
							entityList.append(strEntity)
		return entityList
	
	
	def getEntity(self, results):
            entityList = set()
            x_and_y = set()
            x_and_z = set()
            x_alone = set()
            y_alone = set()
            z_alone = set()
            for result in results:
                if result.multi:
                    entityList.add(''.join(result))
                    continue
                if result.xyz:
                    if len(result) >= 3:
                        entityList.add(''.join(result))
                    elif len(result) == 2:
                        if result.yy:
                            x_and_y.add(''.join(result))
                        elif result.zz:
                            x_and_z.add('|'.join(result))
                    elif len(result) == 1:
                        x_alone.add(result[0])
                    continue
                if result.y:
                    y_alone.add(result[0])
                    continue
                if result.z:
                    z_alone.add(result[0])
            for x in x_alone:
                for y in y_alone:
                    x_and_y.add(x+y)
                for z in z_alone:
                    x_and_z.add(x+'|'+z)
            for xy in x_and_y:
                for z in z_alone:
                    entityList.add(xy+z)
                if not z_alone:
                    entityList.add(xy)
            for xz in x_and_z:
                x = xz.split('|')[0]
                z = xz.split('|')[1]
                for y in y_alone:
                    entityList.add(x+y+z)
                if not y_alone:
                    entityList.add(x+z)
            return entityList

