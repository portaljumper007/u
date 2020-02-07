import numpy as np
from scipy.interpolate import PchipInterpolator

from datetime import datetime
from datetime import timedelta

from collections import defaultdict

def readCSV(filePath):
    trackerNames = []
    data = []
    currentName = 0

    file = open(filePath,"r")
    file.readline()
    file.readline()
    lineNum = -1
    while True:
        line = file.readline()
        lineNum += 1
        if not line:
            break
        elif "," in line or "/" in line or "." in line:
            data[currentName].append(line.split(","))
            data[currentName][-1][-1] = data[currentName][-1][-1][:-1]
        elif line == "\n":
            data[currentName] = data[currentName][::-1]
            currentName += 1
        else:
            trackerNames.append(line[:-1])
            data.append([])
    a, b = trackerNames, data

    dataNames = []
    dataTimes = []
    dataValues = []
    for trackerName in range(len(b)):
        dataNames.append(a[trackerName])
        dataTimes.append([])
        dataValues.append([])
        for entry in range(len(b[trackerName])):
            entryTime = datetime.strptime(b[trackerName][entry][0], '%d/%m/%Y')
            entryTime = entryTime + timedelta(minutes=((int(b[trackerName][entry][1][:2]) * 60) + int(b[trackerName][entry][1][3:])))
            if entry == 0:
                startTime = entryTime
            entryTime = entryTime - startTime
            dataTimes[trackerName].append(entryTime.total_seconds())
            dataValues[trackerName].append(float(b[trackerName][entry][2]))
    return dataNames, dataTimes, dataValues

FILENAME = "KeepTrack_7_2_2020.csv" #############################################################################################################

dataNames, dataTimes, dataValues = readCSV(FILENAME)

def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return ((key, locs) for key, locs in tally.items()
            if len(locs) > 1)

set = 0
while set < len(dataTimes):
    if len(dataTimes[set]) < 2:
        del dataNames[set]
        del dataTimes[set]
        del dataValues[set]
    else:
        for dup in sorted(list_duplicates(dataTimes[set])):
            for i in range(1, len(dup)):
                del dataTimes[set][dup[1][i]]
                del dataValues[set][dup[1][i]]
    set += 1
#Run paired smoothing to prevent outliers?
#Then change data to pairwise changes.

#data = np.array([[[1, 2, 3, 4], [160, 120, 354, 2]], [[1, 2, 3, 4], [160, 120, 354, 2]]])
combined_x = np.unique(np.concatenate(dataTimes))

unifiedRelativeSets = []
maxValues = []
for set in range(len(dataTimes)):
    pchip = PchipInterpolator(dataTimes[set], dataValues[set])
    unified = pchip(combined_x)
    #interpolSmooth = []
    #for i in range(np.size(unified) - 1):
        #interpolSmooth.append((unified[i] + unified[i + 1]) / 2)
    unifiedRelativeSets.append([])
    for i in range(np.size(unified) - 1):
        change = (unified[i + 1] / unified[i])
        if change < 1:
            change = 1 / change
        change -= 1
        #unifiedRelativeSets[set].append(change)
        k = i
        if k >= len(dataTimes[set]) - 2:
            k = len(dataTimes[set]) - 2

        a0 = pchip.c.item(3, k) * ((combined_x[i]) ** 0) #^0
        b0 = pchip.c.item(2, k) * ((combined_x[i]) ** 1) #^1
        c0 = pchip.c.item(1, k) * ((combined_x[i]) ** 2) #^2
        d0 = pchip.c.item(0, k) * ((combined_x[i]) ** 3) #^3
        a1 = pchip.c.item(3, k) * ((combined_x[i + 1]) ** 0) #^0
        b1 = pchip.c.item(2, k) * ((combined_x[i + 1]) ** 1) #^1
        c1 = pchip.c.item(1, k) * ((combined_x[i + 1]) ** 2) #^2
        d1 = pchip.c.item(0, k) * ((combined_x[i + 1]) ** 3) #^3
        averageGrad = abs(((((a1 + b1 + c1 + d1) - (a0 + b0 + c0 + d0)) / (combined_x[i + 1] - combined_x[i]))) + 1)

        if averageGrad < 1:
            averageGrad = 1 / averageGrad
        averageGrad -= 1
        unifiedRelativeSets[set].append(averageGrad)

diffs = []
standardDevs = []
for set in range(len(unifiedRelativeSets)):
    for otherSet in range(len(unifiedRelativeSets)):
        if otherSet != set:
            subtraction = np.subtract(unifiedRelativeSets[set], unifiedRelativeSets[otherSet])
            standardDev = np.std(subtraction)
            diff = np.mean(np.abs(subtraction))
            diffs.append(diff)
            standardDevs.append(standardDev)
diffsMax = np.amax(diffs)
diffsMin = np.amin(diffs)
standardDevsMax = np.amax(standardDevs)
standardDevsMin = np.amin(standardDevs)
count = -1

print("100% does not mean identical. Similarity is scaled, so the most similar is 100% and least 0%.")
for set in range(len(unifiedRelativeSets)):
    print(" -" * 20)
    for otherSet in range(len(unifiedRelativeSets)):
        if otherSet != set:
            count += 1
            diffs[count] = diffsMax - np.abs(diffs[count])
            standardDevs[count] = standardDevsMax - np.abs(standardDevs[count])
            diffPerc = (diffs[count]) * (100 / (diffsMax - diffsMin))
            standardDevPerc = standardDevs[count] * (100 / (standardDevsMax - standardDevsMin))
            print(str(np.round(diffPerc, 1)) + "%", "    confidence", str(np.round(standardDevPerc, 1)) + "%", "     multiplied", str(np.round(diffPerc * (standardDevPerc / 100), 1)) + "%", "     ", dataNames[set], "-->", dataNames[otherSet])