from datetime import datetime
from datetime import timedelta

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

    data = []
    for trackerName in range(len(b)):
        data.append([a[trackerName], [], []])
        for entry in range(len(b[trackerName])):
            entryTime = datetime.strptime(b[trackerName][entry][0], '%d/%m/%Y')
            entryTime = entryTime + timedelta(minutes=((int(b[trackerName][entry][1][:2]) * 60) + int(b[trackerName][entry][1][3:])))
            if entry == 0:
                startTime = entryTime
            entryTime = entryTime - startTime
            data[trackerName][1].append(entryTime.total_seconds())
            data[trackerName][2].append(float(b[trackerName][entry][2]))
    return data

data = readCSV("KeepTrack_6_2_2020.csv")
print(data)