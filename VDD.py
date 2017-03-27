from __main__ import vtk, qt, ctk, slicer
from vtk.util import numpy_support
import numpy as np

#
# ITBImageFilter
#

class VDD:
  def __init__(self, parent):
    parent.title = "Voxel Dislpacement Detector"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = [ """
    Shajith Dissanayake (USYD) 
    """]
    parent.helpText = """
    COMP5424 VDD Assignment
    """
    parent.acknowledgementText = """
    This python program calculates the voxel displacements of two images using an image registration method,
    and then displays the displacement map in 3D space.
    """ 
    self.parent = parent

#
# The main widget
#

class VDD:
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

  #  Setup the layout
  def setup(self):

    # the volume selectors
    self.inputFrame = qt.QFrame(self.laplaceCollapsibleButton)
    self.inputFrame.setLayout(qt.QHBoxLayout())
    self.filterFormLayout.addWidget(self.inputFrame)
    self.inputSelector = qt.QLabel("Input Volume #1 : ", self.inputFrame)
    self.inputFrame.layout().addWidget(self.inputSelector)
    self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputFrame.layout().addWidget(self.inputSelector)

    # Add a reload button for debug
    reloadButton = qt.QPushButton("Reload")
    reloadButton.toolTip = "Reload this Module"
    reloadButton.name = "ITBImageFilter Reload"
    reloadButton.connect('clicked()', self.onReload)
    self.reloadButton = reloadButton
    self.filterFormLayout.addWidget(self.reloadButton)

    # Add a clear screen button for debug
    clearScreenButton = qt.QPushButton("Clear Screen")
    clearScreenButton.toolTip = "Clear Python Interactor Screen"
    clearScreenButton.name = "ClearScreen"
    clearScreenButton.connect('clicked()', self.onClearScreen)
    self.clearScreenButton = clearScreenButton
    self.filterFormLayout.addWidget(self.clearScreenButton)


    # Apply button
    filterButton = qt.QPushButton("Apply")
    filterButton.toolTip = "Calculate Voxel Displacement."
    self.filterFormLayout.addWidget(filterButton)
    filterButton.connect('clicked(bool)', self.onApply)
    self.filterButton = filterButton

    # Add vertical spacer
    self.layout.addStretch(1)


  # When the apply button is clicked
  def onApply(self):
    # Read in the image node
    inputVolume = self.inputSelector.currentNode()
    # Extract the array
    inputVolumeData = slicer.util.array(inputVolume.GetID())
    # Name the output volume
    outputVolume_name = inputVolume.GetName() + '_VDD'
    # Copy image node, create a new volume node
    volumesLogic = slicer.modules.volumes.logic()
    outputVolume = volumesLogic.CloneVolume(slicer.mrmlScene, inputVolume, outputVolume_name)
    # Find the array that is associated with the label map
    outputVolumeData = slicer.util.array(outputVolume.GetID())
    # the dimensions of the output volume
    dx, dy, dz = outputVolumeData.shape 
    print dx, dy, dz



    ############### Add your code here ######################
    # Define your 3x3x3 kernel, for example, a smoothing kernel
    if self.filter == "Smoothing":
        print "INFO: Applying a smoothing filter ..."
        kernel = np.ones([3, 3, 3])
        kernel = kernel / kernel.sum()

    # Try to implement a sharpening kernel 
    if self.filter == "Sharpening":
        print "INFO: Applying a sharpening filter ..."
        kernel = np.ones([3, 3, 3])
        kernel = kernel / kernel.sum()
        kernel_identity = np.zeros([3, 3, 3]) 
        kernel_identity[1, 1, 1] = 2
        kernel = kernel_identity - kernel

    # Try to implemnt an edge detector
    if self.filter == "Edge":
        print "INFO: Applying an edge detector ..."
        kernel = np.zeros([3, 3, 3])
        kernel[1, 1, :] = -1
        kernel[1, :, 1] = -1
        kernel[:, 1, 1] = -1
        kernel[1, 1, 1] = 6

    #######################################################


    """
    Iterate all positions in the padded image with your kernel,
    where x, y, z are the current coordinates of the central voxel of your kernel.
    This for loop patter can be easily paralleled in practice in both hardware/software, 
    since the processing at each location is independent. We only slect the central part
    of the image to demonstrate the filtering effect. 
    """
    
    for x in np.arange(dx - dx/3) + dx/6:
        for y in np.arange(dy - dy*2/3) + dy/3:
            for z in np.arange(dz - dz*2/3) + dz/3:
                patch = inputVolumeData[x - 1 : x + 2, y - 1: y + 2, z - 1 : z + 2]
                value = (kernel[:]*(patch[:])).sum()
                outputVolumeData[x, y, z] = value if value > 0 else 0


    outputVolume.GetImageData().Modified()
    
    # make the output volume appear in all the slice views
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(outputVolume.GetID())
    slicer.app.applicationLogic().PropagateVolumeSelection(0)


  # 
  # Supporting Functions
  # 

  # Reload the Module
  def onReload(self, moduleName = "ITBImageFilter"):
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"
    fPath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(fPath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(fPath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, fPath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    print "the module name to be reloaded,", moduleName
    # find the Button with a name 'moduleName Reolad', then find its parent (e.g., a collasp button) and grand parent (moduleNameWidget)
    parent = slicer.util.findChildren(name = '%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass

    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()


  # Clear the Python Interacter Screen 
  def onClearScreen(self):
    print "\n" * 50


