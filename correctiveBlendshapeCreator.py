"""
--------------------------------------------------------------------------------------------------------------------
correctiveBlendshapeCreator.py - Python Script
--------------------------------------------------------------------------------------------------------------------
Copyright 2012 Carlos Chacon L. All rights reserved.

DESCRIPTION:
Eases the creation of corrective blendshapes and their connection to the original mesh.

USAGE:
*Run the script
*Second, Select, in the following order, the master mesh, the first blendshape,the second blendshape. Click the "Create Corrective Blendshape" button.
*Remodel the created blendshape.
*Second, click the "Connect blendshape to master" button.
*Done.

AUTHOR:
Carlos Chacon L. (caedo.00 at gmail dot com)
--------------------------------------------------------------------------------------------------------------------
"""

from maya.cmds import blendShape, setAttr, ls, duplicate, rename, move, expression, select, getAttr, listRelatives, listConnections, window, columnLayout, button,text, separator, showWindow, deleteUI, delete, attributeQuery, pointPosition


#UI Elements
bsWin = "correctiveBSWin"
bsLayout = "correctiveBSLayout"
btnCreateCorrectiveBS = "btnCreateCorrectiveBS"
btnConnectCorrectiveBS = "btnConnectCorrectiveBS"
btnRestart = "btnRestart"
lblMsgBS ="lblMsgBS"
#End UI Elements

#BS variables
master =""
blendshape1 =""
blendshape2 =""
corrective_blendshape ="" #name of the corrective blendshape
dummy_blendshape ="" #name of the dummy blendshape who have the combination of the two original blendshapes and the corrective blendshape
#End BS variables

def showSuccessMsg(msg):
	global lblMsgBS
	text(lblMsgBS , e=True, l=msg, bgc=(0,0.54,0))

def showFailMsg(msg):
	global lblMsgBS
	text(lblMsgBS, e=True, l=msg, bgc=(0.92,0.08,0.19))

def showInfoMsg(msg):
	global lblMsgBS
	text(lblMsgBS, e=True, l=msg, bgc=(0.8,0.8,0.6))

def correctiveBlendshapeExists(obj, blendshape1, blendshape2):
	"""
	Checks to see if a corrective blendshape for the given bs1 and bs2 exists on the master mesh
	"""
	blendshape_node = getBlendshapesFromMaster(obj)[0]
	#Now we need to check if the two possible name combinations exists in the blendshape node.
	corrective_blendshape_name1 = "%s_%s_dummy" % (blendshape1, blendshape2)
	corrective_blendshape_name2 = "%s_%s_dummy" % (blendshape2, blendshape1)
	return (attributeQuery(corrective_blendshape_name1, node=blendshape_node, ex=True) or attributeQuery(corrective_blendshape_name2, node=blendshape_node, ex=True))

def clearHistory(obj):
	"""
	Clears the construction history of specified obj.
	"""
	delete(obj, ch=True)

def getSkinClusterNode(obj):
	"""
	Gets the skin cluster nodes of an object. If there isn't any
	return None.
	"""
	shape_node = listRelatives(obj, shapes=True)
	skincluster_node = listConnections(shape_node[0],d=False,s=True, type="skinCluster")
	return skincluster_node

def hasSkinCluster(obj):
	"""
	Checks if the object is binded to a skin cluster.
	"""
	skincluster_node = getSkinClusterNode(obj)
	if(skincluster_node is not None):
		return True
	else:
		return False

def getShapeNode(obj):
	"""
	Returns the shape node of an object.
	"""
	return listRelatives(obj, shapes=True)

def getBlendshapesFromMaster(obj):
	"""
	Returns the blendshape nodes of target obj.
	"""
	#Blendshape nodes are connected to the shape node, not the transform!	
	if(hasSkinCluster(obj)):
		skin_cluster = getSkinClusterNode(obj)
		blendshape_nodes = getBlendshapeNodes(skin_cluster[0])	
	else:
		shape_node = listRelatives(obj, shapes=True)	
		blendshape_nodes = getBlendshapeNodes(shape_node[0])
	return blendshape_nodes 

def getBlendshapeNodes(node):
	return listConnections(node,d=False,s=True, type="blendShape")

def getBlendshapeWeightCount(obj):
	"""
	Returns the total number of weights in a blendshape node.
	"""
	return blendShape(obj, q=True, wc=True)

def setBlendshapeWeight(obj,weight ,value):
	"""
	Turn on blenshape of a object
	"""
	blendshape_node = getBlendshapesFromMaster(obj)[0]
	setAttr(blendshape_node + "." + weight, value )

def getBlendshapeWeight(obj, weight):
	"""
	Get the weight value of blendshape
	"""
	blendshape_node = getBlendshapesFromMaster(obj)[0]
	return getAttr(blendshape_node + "." + weight)

def getVertices(obj):
	vertices = list()
	for v in getAttr(obj+".vrts", multiIndices=True):
		vertices.append(pointPosition(obj+".vtx["+str(v)+"]",w=True))    
	return vertices

def getObjWidth(obj):
	vertices = getVertices(obj)
	return max([v[0] for v in vertices]) - min([v[0] for v in vertices])

def getBlendshapePosFromMaster(master):
	"""
	Returns the blendshape position in X based on the master's X position.	
	"""
	master_pos = getAttr(master + ".tx")
	return master_pos + getObjWidth(master)


def createCorrectiveBlendshape(master, blendshape1, blendshape2):
	"""
	Creates the corrective blendshape to be reshaped,  using the master as template.
	"""
	corrective_blendshape_pos = getBlendshapePosFromMaster(master)
	corrective_blendshape = "%s_%s_corrective" % (blendshape1, blendshape2)
	duplicate(master, name=corrective_blendshape)
	if (getBlendshapeWeight(master, blendshape1) == 0) and  (getBlendshapeWeight(master, blendshape2) == 0):
		blendShape(blendshape1, blendshape2,corrective_blendshape)
		setBlendshapeWeight(corrective_blendshape, blendshape1, 1)
		setBlendshapeWeight(corrective_blendshape, blendshape2, 1)
		clearHistory(corrective_blendshape)
	move(corrective_blendshape_pos,0,0, corrective_blendshape)
	return corrective_blendshape

def applyBlendshapesToDummy(master, blendshape1, blendshape2, corrective_blendshape):
	"""
	Applies the bs1, bs2 and corrective_bs to a copy of the master,
	in order to create the final substraction of the bs1 and bs2 against
	corrective bs.
	"""
	dummy_blendshape = corrective_blendshape.replace("corrective", "dummy")
	dummy_blendshape_pos = getBlendshapePosFromMaster(corrective_blendshape)
	blendshape_node = getBlendshapesFromMaster(master)[0]
	setAttr(blendshape_node + ".envelope", 0)
	duplicate(master, name=dummy_blendshape)
	setAttr(blendshape_node + ".envelope", 1)
	move(dummy_blendshape_pos,0,0, dummy_blendshape)
	blendshape_node = blendShape(blendshape1, blendshape2, corrective_blendshape, dummy_blendshape)[0]
	setAttr(blendshape_node + "." + blendshape1, -1)
	setAttr(blendshape_node + "." + blendshape2, -1)
	setAttr(blendshape_node + "." + corrective_blendshape, 1)
	return dummy_blendshape

def addDummyToMasterBlendshape(master,dummy):
	"""
	Adds the template blendshape with the corrective substraction
	to the master blendshape.
	"""
	blendshape_node = getBlendshapesFromMaster(master)[0]
	weight_count = getBlendshapeWeightCount(master)
	blendShape(master, e=True, t=[master, weight_count+1,dummy,1])


def addCorrectiveExpressionToMaster(master, blendshape_dummy, blendshape1, blendshape2):
	"""
	Add expression to turn on corrective expression when
	bs1 and bs2 are active.
	"""
	master_blendshape = getBlendshapesFromMaster(master)[0]
	expression_name = "exp_" + blendshape_dummy
	expression_string = master_blendshape+"."+blendshape_dummy + "=" + master_blendshape +"."+blendshape1 + " * " + master_blendshape+"."+blendshape2 + ";"
	expression(s=expression_string, n=expression_name)


def createCopy(*args):
	global master, blendshape1, blendshape2, corrective_blendshape	
	blendshapes = ls(sl=True)
	if(len(blendshapes) == 3):
		if(corrective_blendshape is ""):
			master = blendshapes[0]
			if(getBlendshapesFromMaster(master) is not None):
				blendshape1 = blendshapes[1]
				blendshape2 = blendshapes[2]
				if(not correctiveBlendshapeExists(master, blendshape1, blendshape2)):
					corrective_blendshape = createCorrectiveBlendshape(master, blendshape1, blendshape2)
					showSuccessMsg("Corrective blendshape created successfully. Remodel it!")
				else:
					showFailMsg("Corrective blendshape already exists.")
			else:
				showFailMsg("The master mesh doesn't has any blendshape node.")
		else:
			showFailMsg("A corrective blendshape is already on creation process. Hit the restart button if you want to start all over again.")
	else:
		showFailMsg("Incorrect number of blendshapes objs selected! Please select the master, blenshape1 and blendshape2.")

def connectoToMaster(*args):
	global master, blendshape1, blendshape2, corrective_blendshape
	if((master is not "") and (blendshape1 is not "") and (blendshape2 is not "") and (corrective_blendshape is not "")):
		dummy_blendshape = applyBlendshapesToDummy(master, blendshape1, blendshape2, corrective_blendshape)
		addDummyToMasterBlendshape(master, dummy_blendshape)
		addCorrectiveExpressionToMaster(master, dummy_blendshape, blendshape1, blendshape2)
		master = blendshape1 = blendshape2 = corrective_blendshape = dummyblendshape = ""
		showSuccessMsg("Corrective blendshape has been connected successfully.")
	else:
		showFailMsg("The corrective blendshape hasn't been created.")

def restart(*args):
	"""
	Restart the whole corrective blendshape creation process.
	"""
	global master, blendshape1, blendshape2, corrective_blendshape, dummy_blendshape
	master = blendshape1 = blendshape2 = corrective_blendshape = dummy_blendshape = ""
	showInfoMsg("Creation process restarted.")

def showCorrectiveBlendshapeWindow():
	"""
	Shows the GUI for the corrective blendshape creator.
	"""
	global bsWin, bsLayout,btnCreateCorrectiveBS, btnConnectCorrectiveBS,btnRestart,lblMsgBS
	if(window(bsWin, q=True, exists=True)):
		deleteUI(bsWin, window=True)
	window(bsWin,width = 270, title="Corrective BS Creator")
	columnLayout(bsLayout, adjustableColumn = True,p=bsWin,co=("both",10), rs=10)
	separator(p=bsLayout, vis=True)
	button(btnCreateCorrectiveBS,p=bsLayout, l="1. Create Corrective Blendshape",h=50,command=createCopy)
	separator(p=bsLayout)
	button(btnConnectCorrectiveBS,p=bsLayout, l="2. Connect Blendshape to Master", h=50,command=connectoToMaster)
	separator(p=bsLayout)
	separator(p=bsLayout, vis=False)
	button(btnRestart, p=bsLayout, l="Restart", h=50, command=restart)
	separator(p=bsLayout)
	text(lblMsgBS,p=bsLayout,l="Select the master, blendshape1 and blendshape2 to create the corrective BS.",ww=True )
	separator(p=bsLayout, vis=True)
	showWindow()

showCorrectiveBlendshapeWindow()
