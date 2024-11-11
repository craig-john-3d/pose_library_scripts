from maya import cmds

def showUI():
    """Display UI of the tool"""
    window = cmds.window(title="Pose Transfer Tool", width = 350)
    cmds.columnLayout(adjustableColumn = True)
    cmds.text(label = "Pose Transfer", align = "center", height = 40,
              annotation = "Transfer pose from first selected rig to other selected rigs")
    cmds.button(label="Transfer Selected", 
                height=40, 
                annotation="Select 2 or more rigs", 
                command = transferSelected)
    cmds.showWindow(window)


def transferSelected(*args):
    """Transfer pose form first selected rig to rest of selected rigs.

    Args:
        *args: catch-all arguments passed in by Maya
    """
    # get selected namespaces
    namespaces = getSelectedNamespaces()
    # validate selection
    if len(namespaces) == 0:
        cmds.warning("Please select something!")
        return
    if len(namespaces) == 1:
        cmds.warning("Please select more than 1 rig!")
        return
    sourceNamespace = namespaces[0]

    # using [num:num] allows you to get back a list of all of the items at the starting index from the left (inclusive) to the ending index on the right (non inclusive)
    # in this case, we are telling it to get the 2nd index up until the end
    # this allows us to transfer poses to multiple rigs
    targetNamespace = namespaces[1:]

    # get pose dictionary from first source
    poseDict = getPoseDict(sourceNamespace)
    # apply pose to targets
    for target in targetNamespace:
        applyPose(poseDict, target)

def getSelectedNamespaces():
    """ Get list of namespaces for selected rigs.

    Returns:
        list

    """
    # get user selection
    selection = cmds.ls(selection = True)

    # if no selection, return empty list
    if len(selection) == 0:
        return []
    
    namespaceList = []
    for ctrl in selection:
        # split to get namespace from control
        namespace = ctrl.split(":")[0]
        # add namespace to list if its not there
        if namespace not in namespaceList:
            namespaceList.append(namespace)

    return namespaceList

def getAttrsFromNode(ctrlNode):
    """Get attribute names from node
    
    Args:
        ctrlNode(str): Name of the node
    
    Returns:
        list: List of short attribute names
    """
    # obtaining all attributes from selected node
    attributes = cmds.listAnimatable(ctrlNode)

    # if nothing is selected, return empty list
    if not attributes:
        return []
    
    attrNames = []
    for fullAttr in attributes:
        # split attributes at period
        parts = fullAttr.split(".")
        # get last index
        attrName = parts[-1]
        # add index to list of attributes
        attrNames.append(attrName)
    
    return attrNames

def getPoseDict(namespace):
    """ Get the pose dictionary without namespaces.
    Args:
        namespace(str): Filter selection by this namespace
    Returns:
        dict: Dictionary of controls with attributes and their values
    
    """
    # get selection
    selection = cmds.ls(selection = True)
    if not selection:
        return {}
    
    # create dictionary
    poseDict = {}
    for ctrl in selection:
        # filter out the selection by the namespace provided
        if not ctrl.startswith(namespace):
            continue

        # get attributes
        animatableAttrs = getAttrsFromNode(ctrl)
        if not animatableAttrs:
            continue
        
        # ctrl -> 'morpheus:rig_elbow_r_skin_Bendy_anim'
        #build dictionary
        for attr in animatableAttrs:
            ctrlName = ctrl.split(":")[-1]
            fullAttr = '{}.{}'.format(ctrlName, attr)
            ctrlWithAttr = '{}.{}'.format(ctrl,attr)
            attrValue = cmds.getAttr(ctrlWithAttr)
            #{'ctrl.attr': attrValue}
            poseDict[fullAttr] = attrValue
    
    # return dictionary
    return poseDict

def applyPose(poseDict, targetNamespace):
    """Apply provided pose to targetNamespace.
    
    Args:
        poseDict(dict): dictionary with pose data.
        targetNamespace(str): target namespace to apply pose to 

    """
    # get attribute names
    for attrName in poseDict.keys():
        # add namespace
        attrValue = poseDict[attrName]
        fullAttrName = '{}:{}'.format(targetNamespace, attrName)

        node, attrShortName = fullAttrName.split('.')
        # check if attribute exists, and if it is settable
        if not cmds.objExists(node) or not cmds.attributeQuery(attrShortName, node = node, exists=True) or not cmds.getAttr(fullAttrName, settable = True):
            continue
        
        # set attribute
        cmds.setAttr(fullAttrName, attrValue)
    
    # error checks (if rig is not the same)
    