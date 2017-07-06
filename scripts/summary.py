import os
import csv
import collections
import sys
import operator

master = sys.argv[1]
slave = sys.argv[2]
articleType = sys.argv[3]

# this summary is based on sentence level, which means relation is based on article

def reverse_numeric(x, y):
        return y - x
    
def buildInvertedTable(_file):
    lookup = collections.defaultdict(int)
    direct = []
    with open(_file, 'r') as F:
        Freader = csv.reader(F)
        for row in Freader:
            entity = row[0].replace('\n', '')
            entity = entity.replace('\r', '')
            lookup[entity] = len(direct)
            direct.append(entity)
    return direct, lookup

        
def checkSimilarity(master, slave):
    sentenceIdSlave = collections.defaultdict(set)
    if os.path.exists(slave):
        with open(slave, 'r') as S:
            Sreader = csv.reader(S, delimiter = '\t')
            for row in Sreader:
                sentenceId = row[2]
                entity = row[3].split("|")[0]
                if entity in slaveLookup:
                    sentenceIdSlave[sentenceId].add(slaveLookup[entity])
    #sentenceIdSlave is with structure {'12': set(A, B...)}
    sentenceIdMaster = collections.defaultdict(set)
    with open(master, 'r') as M:
        Mreader = csv.reader(M, delimiter = '\t')
        for row in Mreader:
            sentenceId = row[2]
            entity = row[3].split("|")[0]
            if entity in masterLookup:
                sentenceIdMaster[sentenceId].add(masterLookup[entity])
    if level == 'sentence':
        for sentenceId, entitiesIds in sentenceIdMaster.items():
            for entityId in entitiesIds:
                masterCountList[entityId] += 1
                if sentenceId in sentenceIdSlave:
                    slavesIds = sentenceIdSlave[sentenceId]
                    for slaveId in slavesIds:
                        resultTable[entityId][slaveId] += 1
    if level == 'article':
        tmp_masterCountList = [0] * len(masterList)
        tmp_resultTable = collections.defaultdict(lambda : collections.defaultdict(int))
        for sentenceId, entitiesIds in sentenceIdMaster.items():
            for entityId in entitiesIds:
                tmp_masterCountList[entityId] = 1
                if sentenceId in sentenceIdSlave:
                    slavesIds = sentenceIdSlave[sentenceId]
                    for slaveId in slavesIds:
                        tmp_resultTable[entityId][slaveId] = 1
        for i in range(len(masterList)):
            masterCountList[i] += tmp_masterCountList[i]
            for slaveId in tmp_resultTable[i]:
                resultTable[i][slaveId] += tmp_resultTable[i][slaveId]

def writeDictToFile(filename):
    with open(filename, 'a+') as savefile:
        fileWriter = csv.writer(savefile, delimiter= '\t')
        for i, entity in enumerate(masterList):
            row = []
            row.append(entity + '|' + str(masterCountList[i]))
            result = resultTable[i]
            sorted_result = sorted(result.items(), key=operator.itemgetter(1), cmp = reverse_numeric)
            row.append(';'.join('{}:{}'.format(slaveList[k], v) for k, v in sorted_result))
            if row[1] != '':
                fileWriter.writerow(row)
    
if __name__ == '__main__':
    masterFolder = './' + master
    slaveFolder = './' + slave
    global masterList
    global masterLookup
    global slaveList
    global slaveLookup
    global resultTable
    global masterCountList
    global level
    level = 'sentence'
    masterList, masterLookup = buildInvertedTable(masterFolder + '.csv')
    slaveList, slaveLookup = buildInvertedTable(slaveFolder + '.csv')
    articleList, articleLookup = buildInvertedTable(articleType + '.csv')
    pmidList = os.listdir(masterFolder)
    resultTable = collections.defaultdict(lambda : collections.defaultdict(int))
    masterCountList = [0] * len(masterList)
    for pmid in pmidList:
        if pmid[:-4] not in articleLookup:
            continue
        _master = os.path.join(masterFolder, pmid)
        _slave = os.path.join(slaveFolder, pmid)
        checkSimilarity(_master, _slave)
    filename = './'+master+'-'+slave+ '-'+ articleType +'.csv'
    writeDictToFile(filename)

    
    
    
                