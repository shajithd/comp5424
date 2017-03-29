from __main__ import vtk, qt, ctk, slicer

#
# HelloPython
#

class HelloPython:
  def __init__(self, parent):
    parent.title = "Hello Python"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Jean-Christophe Fillion-Robin (Kitware)",
                           "Steve Pieper (Isomics)",
                           "Sonia Pujol (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Example of scripted loadable extension for the HelloPython tutorial.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.,
Steve Pieper, Isomics, Inc., and Sonia Pujol, Brigham and Women's Hospital and was 
partially funded by NIH grant 3P41RR013218-12S1 (NAC) and is part of the National Alliance 
for Medical Image Computing (NA-MIC), funded by the National Institutes of Health through the 
NIH Roadmap for Medical Research, Grant U54 EB005149.""" # replace with organization, grant and thanks.
    self.parent = parent

#
# qHelloPythonWidget
#

class HelloPythonWidget:
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
    # Instantiate and connect widgets ...

    # Collapsible button
    sampleCollapsibleButton = ctk.ctkCollapsibleButton()
    sampleCollapsibleButton.text = "A collapsible button"
    self.layout.addWidget(sampleCollapsibleButton)

    # Layout within the sample collapsible button
    sampleFormLayout = qt.QFormLayout(sampleCollapsibleButton)

    ########################
    helloWorldButton = qt.QPushButton("Hello World")
    helloWorldButton.toolTip = "Print 'Hello world' in standard output."
    sampleFormLayout.addWidget(helloWorldButton)
    helloWorldButton.connect('clicked()', self.onHelloWorldButtonClicked)
    # Add tutorial code here
    ########################

    ########################
    # Add a reload button for debug
    reloadButton = qt.QPushButton("Reload")
    reloadButton.toolTip = "Reload this Module"
    reloadButton.name = "HelloPython Reload"
    sampleFormLayout.addWidget(reloadButton)
    reloadButton.connect('clicked()', self.onReload)
    self.reloadButton = reloadButton
    ########################

    
    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    self.helloWorldButton = helloWorldButton

  def onHelloWorldButtonClicked(self):
    print "Hello World !"
    ########################
    qt.QMessageBox.information(\
      slicer.util.mainWindow(), \
      'Slicer Python', 'Hellow World!') 
    # Add tutorial code here
    ########################


  ########################
    # Add a reload button
  def onReload(self, moduleName = "HelloPython"):
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
    # find the Button with a name 'moduleName Reolad', then find its parent (e.g., a collasp button) and grand parent (moduleNameWidget)
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