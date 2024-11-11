from maya import cmds
from pose_library import core
import poseTransfer

# global variable, constant value throughout
WINDOW_NAME = 'poseLibraryUI'

# global variable for scroll list to be used later to add poses
TEXT_LIST_NAME = 'poseNameTextList'

# global variable for the text field that users can input a pose to be saved
TEXT_FIELD_NAME = 'savePoseTextField'

def showUI():
    """SHow pose library UI"""
    # delete window if it already exists
    if cmds.window(WINDOW_NAME, query=True, exists = True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title = "Pose Library")

    # apply pose section
    cmds.columnLayout(adjustableColumn = True, rowSpacing = 5)
    cmds.textScrollList(TEXT_LIST_NAME, allowMultiSelection = False)
    cmds.button(label = "Apply Pose", height = 40, command = applySelectedPose)

    # save pose section
    cmds.frameLayout(label = "Save Pose", collapsable = True, backgroundColor=((54/255.0), (104/255.0), (127/255.0)))
    cmds.columnLayout(adjustableColumn = True)
    # makes second column (text field) resizable)
    cmds.rowLayout(numberOfColumns = 3, adjustableColumn = 2)
    cmds.text(label = "Name")
    cmds.textField(TEXT_FIELD_NAME, width = 400)
    # set column layout as new parent
    cmds.setParent("..")
    cmds.button(label = "Save Pose", height = 30, command = savePose)


    cmds.showWindow(WINDOW_NAME)
    reloadPoses()

def savePose(*args):
    poseName = cmds.textField(TEXT_FIELD_NAME, query = True, text = True)

    # check if user entered name
    if poseName == "":
        cmds.warning("Please enter a pose name!")
        return
    
    # check if user only selected one rig
    selectedNamespaces = poseTransfer.getSelectedNamespaces()
    if len(selectedNamespaces) != 1:
        cmds.warning('Please select ONE rig in the scene!')
        return
    
    #check if pose name already exists
    savedPosesDict = core.getPosesDict()
    if poseName in savedPosesDict:
        cmds.warning("Pose '{}' already exists. Please enter another name").format(poseName)
        return
    
    poseDict = poseTransfer.getPoseDict(selectedNamespaces[0])
    core.writePoseToFile(poseName, poseDict)

    print('Successfully saved pose: {}'.format(poseName))
    
    reloadPoses()


def reloadPoses():
    """Gather poses from files and populate list with them"""

    cmds.textScrollList(TEXT_LIST_NAME, edit = True, removeAll = True)
    posesDict = core.getPosesDict()
    poseNames = posesDict.keys()
    sortedNames = sorted(poseNames)
    for name in sortedNames:
        addPose(name)

def addPose(poseName):
    """Add new pose name to text-scroll list

    Args:
        poseName (str): name of the pose to add to list
    """
    cmds.textScrollList(TEXT_LIST_NAME, edit = True, append = poseName)

def applySelectedPose(*args):
    """Apply selected poses to selected rigs"""

    # if pose is not selected, give warning
    selectedPose = getSelectedPose()
    if selectedPose is None:
        cmds.warning('Please select a pose!')
        return
    
    # if rig is not selected, give warning
    selectedNamespaces = poseTransfer.getSelectedNamespaces()
    if not selectedNamespaces:
        cmds.warning('Please select at least one rig')
        return
    
    # if pose does not exist, give warning
    savedPosesDict = core.getPosesDict()
    if selectedPose not in savedPosesDict:
        cmds.warning("Pose: '{}' does not exist").format(selectedPose)
        return
    
    # get pose file and read it
    poseFile = savedPosesDict[selectedPose]
    poseDict = core.readPoseFromFile(poseFile)

    # for each selected rig, apply the pose
    for namespace in selectedNamespaces:
        poseTransfer.applyPose(poseDict, namespace)

def getSelectedPose():
    """Get selected pose item from list

    Returns:
        str/None: None if nothing is selected, otherwise the selected pose name
    """
    selection = cmds.textScrollList(TEXT_LIST_NAME, query = True, selectItem = True)
    if selection is None:
        return None
    selectedItem = selection[0]

    return selectedItem