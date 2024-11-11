import os
import json

ROOT_DIR = r'E:\Documents\\code\\python\\pose_library'
EXT = '.json'

def getPosesDict():
    """Get dictionary with available poses

    Returns:
        dict: dictionary with {'poseName':'fileToPath'}
    """

    posesDict = {}
    # getting all files in directory
    for fileName in os.listdir(ROOT_DIR):
        # if it doesn't end with .json, ignore
        if not fileName.endswith(EXT):
            continue
        # getting pose name by splitting file name
        poseName = fileName.split('.')[0]
        # creating full file path by joining root directory and file name
        filePath = os.path.join(ROOT_DIR, fileName)
        #add to dictionary
        posesDict[poseName] = filePath

    return posesDict

def writePoseToFile(poseName,poseDict):
    """Write pose data to a file

    Args:
        poseName (str): name of the resulting file
        poseDict (dict): contents of the pose
    """
    fileName = '{}{}'.format(poseName, EXT)
    filePath = os.path.join(ROOT_DIR, fileName)

    with open(filePath, 'w') as f:
        json.dump(poseDict,f,indent=4)

def readPoseFromFile(filePath):
    """Read pose data from file.

    Args:
        filePath (str): path to file to read

    Returns:
        dict: pose dictionary
    """
    with open(filePath, 'r') as f:
        poseDict = json.load(f)
    return poseDict