from __main__ import vtk, qt, ctk, slicer

#
# VDD
#

#global MRML for linear transform and deformation map data
outTransform=slicer.vtkMRMLLinearTransformNode()
outTransform.SetName('Linear Transform')

outDisplacementMap=slicer.vtkMRMLGridTransformNode()
outDisplacementMap.SetName('Displacement Field')

#global nodes for output volumes
outModelVolume1=slicer.vtkMRMLScalarVolumeNode()
outModelVolume1.SetName('Linearly Registered Volume')

outModelVolume2=slicer.vtkMRMLScalarVolumeNode()
outModelVolume2.SetName('Non-linearly registered Volume')

#Linear Registration using General Registration module
def linearModel(volumeNode1,volumeNode2):
    parameters={}
    slicer.mrmlScene.AddNode(outModelVolume1)
    slicer.mrmlScene.AddNode(outTransform)
    parameters["fixedVolume"]=volumeNode1.GetID()
    parameters["movingVolume"]=volumeNode2.GetID()
    parameters["outputVolume"]=outModelVolume1.GetID()
    parameters["linearTransform"]=outTransform.GetID()
    parameters["transformType"] = "Affine"
    linearRego = slicer.modules.brainsfit

    return(slicer.cli.run(linearRego, None, parameters))
  
#Non Linear Registration using Demon Registration module
def nonlinearModel(volumeNode1,volumeNode2):
    parameters={}
    slicer.mrmlScene.AddNode(outModelVolume2)
    slicer.mrmlScene.AddNode(outDisplacementMap)
    parameters["fixedVolume"] = volumeNode1.GetID()
    parameters["movingVolume"]=volumeNode2.GetID()
    parameters["outputVolume"]=outModelVolume2.GetID()
    parameters["outputDisplacementFieldVolume"]=outDisplacementMap.GetID()
    parameters["registrationFilterType"]="Diffeomorphic"
    parameters["initializeWithTransform"]=outTransform.GetID()
    nonlinearRego = slicer.modules.brainsdemonwarp
    slicer.app.processEvents()
    return(slicer.cli.run(nonlinearRego,None,parameters))
def displayTransform():
    parameters={}
    parameters["activeTransform"] = outDisplacementMap.GetID()
    parameters["visibleinsliceview"] = 1
    transform = slicer.modules.transforms
    return(slicer.cli.run(transform,None,parameters))

class VDD:
  def __init__(self, parent):
    parent.title = "Voxel Displacement Detector (VDD)"
    parent.categories = ["COMP5424"]
    parent.dependencies = []
    parent.contributors = ["Shajith Dissanayake (USYD)"]
    parent.helpText = """
    COMP5424 Assignment creating a Slicer module for VDD.
    """
    parent.acknowledgementText = """
    Python program to calculate voxel displacement of two images and display it in 3D Space"""
    self.parent = parent

#
# qVDD Widget
#

class VDDWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Collapsible button
    self.laplaceCollapsibleButton = ctk.ctkCollapsibleButton()
    self.laplaceCollapsibleButton.text = "Voxel Displacement Detector"
    self.layout.addWidget(self.laplaceCollapsibleButton)

    # Layout within the collapsible button
    self.laplaceFormLayout = qt.QFormLayout(self.laplaceCollapsibleButton)

    # buttons for volume selectors
    self.inputFrame1 = qt.QFrame(self.laplaceCollapsibleButton)
    self.inputFrame1.setLayout(qt.QHBoxLayout())
    self.laplaceFormLayout.addWidget(self.inputFrame1)
    self.inputSelector1 = qt.QLabel("Input Baseline Scan Volume #1: ", self.inputFrame1)
    self.inputFrame1.layout().addWidget(self.inputSelector1)
    self.inputSelector1 = slicer.qMRMLNodeComboBox(self.inputFrame1)
    self.inputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector1.addEnabled = False
    self.inputSelector1.removeEnabled = False
    self.inputSelector1.setMRMLScene( slicer.mrmlScene )
    self.inputFrame1.layout().addWidget(self.inputSelector1)


    self.inputFrame = qt.QFrame(self.laplaceCollapsibleButton)
    self.inputFrame.setLayout(qt.QHBoxLayout())
    self.laplaceFormLayout.addWidget(self.inputFrame)
    self.inputSelector2 = qt.QLabel("Input Follow Up Scan Volume #2: ", self.inputFrame)
    self.inputFrame.layout().addWidget(self.inputSelector2)
    self.inputSelector2 = slicer.qMRMLNodeComboBox(self.inputFrame)
    self.inputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputFrame.layout().addWidget(self.inputSelector2)

    # Apply button
    laplaceButton = qt.QPushButton("Calculate Voxel Displacement")
    laplaceButton.toolTip = "Run the VDD."
    self.laplaceFormLayout.addWidget(laplaceButton)
    laplaceButton.connect('clicked(bool)', self.onApply)

    # Add a reload button for debug
    reloadButton = qt.QPushButton("Reload")
    reloadButton.toolTip = "Reload this Module"
    reloadButton.name = "VDD Reload"
    reloadButton.connect('clicked()', self.onReload)
    self.reloadButton = reloadButton
    self.laplaceFormLayout.addWidget(reloadButton)
    ########################

    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    self.laplaceButton = laplaceButton

  def onApply(self):
    #set I/O
    inputVolume1 = self.inputSelector1.currentNode()
    inputVolume2 = self.inputSelector2.currentNode()

    if not (inputVolume1 and inputVolume2):
      qt.QMessageBox.critical(
          slicer.util.mainWindow(),
          'VDD', 'Input volumes are required for VDD')
      return


    #parse input volumes into linear and nonlinear registration methods

    linear = linearModel(inputVolume1,inputVolume2)
    nonlinear = nonlinearModel(inputVolume1,inputVolume2)

    pd=qt.QProgressBar()
    pd.setMaximum(0)
    pd.setMinimum(0)
    pd.show()
    while (nonlinear.GetStatus()==1 or linear.GetStatus()==1):
        slicer.app.processEvents()
    pd.hide()


    # make the output volume appear in all the slice views
    slicer.app.applicationLogic().PropagateVolumeSelection(0)
    displayTransform()

  # Add a reload button
  def onReload(self, moduleName = "VDD"):
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source f path
    # - load the module to the global space
    fPath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(fPath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(fPath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, fPath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    print "the module name to be reloaded,", moduleName
    # find the Button with a name 'moduleName Reload'
    # then find its parent (e.g., a collasp button) and grand parent (moduleNameWidget)
    parent = slicer.util.findChildren(name = '%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)
    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
  ########################