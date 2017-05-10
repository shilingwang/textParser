from chromatin import chromatin
import sys

fileName = sys.argv[1]
name = [fileName]
# For parsing with single dictionary:
chromatin(name,"B_Drug").sentenceParser()
# For parsing for more complicated grammar:
#chromatin(name, 0).sentenceParser()