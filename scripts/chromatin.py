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
	
	def __init__(self, name):
		self.mapPath = "./maps"
		self.savePath = "../csv"
		self.txtPath = "../txt"
		self.xmlPath = "../xml"
		self.xMap = os.path.join(self.mapPath, "x_map.dat")
		self.xHat = os.path.join(self.mapPath, "x_hat.dat")
		self.yMap = os.path.join(self.mapPath, "y_map.dat")
		self.yHat = os.path.join(self.mapPath, "y_hat.dat")
		self.zMap = os.path.join(self.mapPath, "z_map.dat")
		self.zHat = os.path.join(self.mapPath, "z_hat.dat")
		if len(name) == 1:
			self.pmid = name[0]
		else:
			self.pmid = name[1]
		self.xml = os.path.join(self.xmlPath, name[0]+".txt.xml")
		#self.saveName = os.path.join(self.savePath, self.pmid+".csv")
		self.txtFile = os.path.join(self.txtPath, name[0]+".txt")
		f = open(self.txtFile)
		self.txtContent = f.read().lower()
		self.sectionPos = self.sectionList()
		self.histone = self.buildDict(self.xHat, self.xMap)
		self.position = self.buildDict(self.yHat, self.yMap)
		self.modif = self.buildDict(self.zHat, self.zMap)
		
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
				if line == "":
					continue
				values = line.split('\t')
				if values[1] == "":
					continue
				dictionary.append((values[1].lower(), values[0]))
		lists = Or(((CaselessLiteral(s).setName(s)).setParseAction(replaceWith(v))) for s,v in dictionary)
		grammar = lists.leaveWhitespace()
		return grammar

	
	def sentenceParser(self, mode):
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
			if mode == 0:
                            entities = self.chromatinGrammar(toParse)
                        else:
                            entities = self.singleDictParser(mode, toParse)
                        if len(entities)>0:
                                section = ""
                                for item in self.sectionPos:
                                        if int(position) >= item[1]:
                                                section = item[0]
                                        else:
                                                break
                                self.save(section, entities, toShow, sentenceID, mode)

                            
        
        
        def singleDictParser(self, mode, toParse):
            myMap = os.path.join(self.mapPath, mode)
            myDict = self.buildDict(myMap)
            myGrammar = (WordStart() + myDict + WordEnd())
            ParserElement.enablePackrat()
            results = myGrammar.searchString(toParse)
            entityList = []
            if len(results) > 0:
                for item in results:
                    entityList.append(item[0])
            return entityList
        
        
        
	def save(self, section, entityList, sentence, sentenceID, saveMode):
		strSentence = " ".join(sentence).encode("utf-8", "ignore")
		strSentence = strSentence.replace(" .", ".")
		if saveMode == 0:
                    savePath = self.savePath + "/histone"
                else:
                    saveMode = saveMode.split('.')[0]
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
		entityList, tmpLen2, tmpLen1, tmpY, tmpZ = [], [], [], [], []
		flag = False
		for result in results:
			if result.multi:
				entityList.append(result)
				flag = True
				continue
			if result.xyz:
				flag = True
				if len(result)==3:
					entityList.append(result)
				elif len(result)==2:
					tmpLen2.append(result)
				elif len(result)==1:
					tmpLen1.append(result)
				continue
			if result.y:
				tmpY.append(result)
				continue
			if result.z:
				tmpZ.append(result)
		if flag == False:
			return []
		newTmpLen1 = []
		if len(tmpY) != 0 and len(tmpLen1) != 0:
			for itemLen1 in tmpLen1:
				for itemY in tmpY:
					newTmpLen1.append(itemLen1 + itemY)
		if len(tmpZ) != 0 and len(tmpLen2) != 0:
			for itemLen2 in tmpLen2:
				newTmpLen2 = []
				for itemZ in tmpZ:
					if itemZ[0] not in itemLen2:
						newTmpLen2.append(itemLen2 + itemZ)
				for item in newTmpLen2:
					if item not in entityList:
						entityList.append(item)
		if len(tmpZ) != 0 and len(newTmpLen1) != 0:
			newTmpLen3 = []
			for itemZ in tmpZ:
				for itemLen1 in newTmpLen1:
					newTmpLen3.append(itemLen1 + itemZ)
				for item in newTmpLen3:
					if item not in entityList:
						entityList.append(item)
		if len(tmpZ) == 0 and len(tmpY) == 0:
			entityList += tmpLen2
			entityList += tmpLen1
		if len(tmpY) != 0 and len(tmpZ) == 0:
			if len(newTmpLen1) == 0:
				entityList += tmpLen2
			else:
				entityList += newTmpLen1
				entityList += tmpLen2
			
		return entityList

			
