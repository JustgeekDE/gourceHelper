#!/usr/bin/env python
import argparse
import subprocess
from glob import glob

try:
  from subprocess import DEVNULL # py3k
except ImportError:
  import os
  DEVNULL = open(os.devnull, 'wb')


def isGitDir(directory):
  gitStatus = subprocess.call(["git", "status"], cwd=directory, stdout=DEVNULL, stderr=subprocess.STDOUT)
  return gitStatus == 0

def getCommitCount(directory):
  commitString = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=directory, stderr=DEVNULL)
  return int(commitString)

def getGourceLog(directory):
  result = []
  try:
    log = subprocess.check_output(["gource", "--output-custom-log", "-"], cwd=directory, stderr=DEVNULL)
    repoName = directory.split("/")[-2]
    for line in log.splitlines():
      timestamp, commiter, modification, filename = line.split("|")
      filename = repoName+filename
      result.append("|".join([timestamp, commiter, modification, filename]))
  except subprocess.CalledProcessError:
    print("Got gource error in " + directory)
    pass
  return result

def getGourceUsers(log):
  allUsers = map(lambda x: x.split("|")[1], log)
  return set(allUsers)

parser = argparse.ArgumentParser(description='Create gource log from multiple rpos')
parser.add_argument('-c', dest="minCommits", metavar='n', type=int, help='minimum ammount of git commits to consider a repository', default=20)
parser.add_argument('targetDirs', help='the directories containing the git repos', nargs='+', default='.')
parser.add_argument('--users', dest="outputUsers", action='store_true', default=False, help="Output list of users instead of gource log")
args = parser.parse_args()

aggregateLog = []
for baseDir in args.targetDirs:
  baseDir = baseDir.rstrip('/') + '/'
  subDirs = glob(baseDir+'/*/')
  for subDirectory in subDirs:
    if isGitDir(subDirectory):
      if getCommitCount(subDirectory) > args.minCommits:
        log = getGourceLog(subDirectory)
        aggregateLog = aggregateLog + log

if args.outputUsers:
  users = getGourceUsers(aggregateLog)
  for user in users:
    print(user)
else:
  aggregateLog.sort()
  for line in aggregateLog:
    print(line)

