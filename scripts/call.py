from chromatin import chromatin
import sys

fileName = sys.argv[1]
name = [fileName]
# For parsing with single dictionary:
#chromatin(name).sentenceParser("A_protein.dat")
# For parsing for more complicated grammar:
chromatin(name).sentenceParser(0)