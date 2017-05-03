from chromatin import chromatin
import os
import csv
import sys
from multiprocessing import Pool
import subprocess

listPath = "../list"
listId = sys.argv[1]
listFile = os.path.join(listPath, listId+".csv")
toProcess = []

with open(listFile, 'r') as l:
	files = csv.reader(l, delimiter = '\t')
	for file in files:
		toProcess.append(file[0])
		

def processFile(file):
	subprocess.call(["python", "./call.py", file])
	
if __name__=='__main__':

	pool = Pool(processes = 24)
	pool.map(processFile, toProcess)
