import subprocess, json
from subprocess import PIPE

modePath = "gameModes/duos.json"
branch = "main"

result = subprocess.check_output(["git", "rev-list", branch])
resultStr = result.decode("utf-8")
# print(result)
lastElos={}
dateEloChanges={}
commitHashes = resultStr.split()
commitHashes.reverse()
# commitHashes = commitHashes[0:50] # limit commit hashes for testing
previousData=None
for commitHash in commitHashes:
    # print(commitHash)
    date=subprocess.check_output(["git", "show", "-s", "--format=%ci", commitHash]).decode("utf-8").strip()
    # print(date)
    try:
        fileAtCommitBytes=subprocess.check_output(["git", "show", commitHash + ":" + modePath])
        fileAtCommit=fileAtCommitBytes.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print("error with getting file, probably missing at this commit: " + str(e))
        continue
    # print(len(fileAtCommit))
    modeData=json.loads(fileAtCommit)
    # print(modeData)

    if (previousData == None):
        previousData = modeData
        continue

    if (date not in dateEloChanges.keys()):
        dateEloChanges[date] = []
    # print(modeData)
    if (type(modeData) is not dict or 'leaderboard' not in modeData):
        print("modeData wasn't a dict or didn't have leaderboard key, skipping")
        print(modeData)
        continue
    for team in modeData['leaderboard']:
        # print(team)
        # {'name': 'ДЕДОВЫ ТРАНКИ', 'rank': 224, 'level_score': 9070, 'duos_persona_min': 'aquata'}
        teamName = team['name']
        
        if teamName in lastElos.keys():
            historicalTeam = lastElos[teamName]
            if historicalTeam['level_score'] != team['level_score']:
                teamDiff = team
                teamDiff['rank_diff'] = team['rank'] - historicalTeam['rank']
                teamDiff['level_score_diff'] = team['level_score'] - historicalTeam['level_score']
                dateEloChanges[date].append(teamDiff)
        else:
            teamDiff = team
            teamDiff['rank_diff'] = 0
            teamDiff['level_score_diff'] = 0
            dateEloChanges[date].append(teamDiff)
        lastElos[teamName] = team
    # print(dateEloChanges)

    previousData = modeData
# print(dateEloChanges)
heatMapDataFile = "heatmap.csv"
with open(heatMapDataFile, 'a') as fo:
    for date, teamDiffs in dateEloChanges.items():
        line = date + ", " + str(len(teamDiffs))
        print(line)
        fo.write(line+"\n")
