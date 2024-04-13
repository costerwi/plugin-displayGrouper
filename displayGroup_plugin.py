"""Abaqus/CAE plugins to modify the display group.

Carl Osterwisch, September 2017
"""

__version__ = "0.2.0"

from abaqusGui import *


class ElementSelectProcedure(AFXProcedure):
    """Class to allow user to select elements and run an assemblyMod command"""

    def __init__(self, owner, prompt, method, number=MANY):
        AFXProcedure.__init__(self, owner) # Construct the base class.
        self._prompt = prompt
        self._number = number

        # Command
        command = AFXGuiCommand(mode=self,
                method=method,
                objectName='displayGroup',
                registerQuery=FALSE)

        # Keywords
        name = 'element'
        if MANY == number:
            name += 's'
        self.elementsKw = AFXObjectKeyword(
                command=command,
                name=name,
                isRequired=TRUE)

        self.step1 = AFXPickStep(
                owner=self,
                keyword=self.elementsKw,
                prompt='Select ' + self._prompt,
                entitiesToPick=ELEMENTS,
                numberToPick=self._number,
                sequenceStyle=TUPLE)    # TUPLE or ARRAY

    def getFirstStep(self):
        return self.step1

    def getLoopStep(self):
        return self.step1 # repeat until cancelled

###############################################################################
# Register the plugins

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='addAdjacent()',
        buttonText='Display Group|Add ad&jacent elements',
        author='Carl Osterwisch',
        description='Add elements that are attached to active nodes.',
        version=__version__,
        applicableModules=['Visualization'],
    )


toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='addAttached()',
        buttonText='Display Group|Add a&ttached elements',
        author='Carl Osterwisch',
        description='Add elements that are attached to active elements.',
        version=__version__,
        applicableModules=['Visualization'],
    )


toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='addNearby()',
        buttonText='Display Group|Add &nearby elements...',
        author='Carl Osterwisch',
        description='Add elements with nodes close to active nodes.',
        version=__version__,
        applicableModules=['Visualization'],
    )


toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='addIncompleteSections()',
        buttonText='Display Group|Add &same section elements',
        author='Carl Osterwisch',
        description='Add elements with same section assignment as active elements.',
        version=__version__,
        applicableModules=['Visualization'],
    )


toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='createFromSections()',
        buttonText='Display Group|Create &named from section assignments',
        author='Carl Osterwisch',
        description='Create a named display group for each section definition.',
        version=__version__,
        applicableModules=['Visualization'],
    )


toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='listActiveSections()',
        buttonText='Display Group|&List active sections',
        author='Carl Osterwisch',
        description='List sections for displayed elements.',
        version=__version__,
        applicableModules=['Visualization'],
    )


class RemoveElementsPicked(ElementSelectProcedure):
    """CAE seems to register this class with the GuiMenuButton, not the instance of the class"""
    pass

toolset.registerGuiMenuButton(
        buttonText='Display Group|Remove picked &elements',
        object=RemoveElementsPicked(toolset, 'elements to remove', 'removeElements', MANY),
        kernelInitString='import displayGroup',
        author='Carl Osterwisch',
        version=__version__,
        helpUrl='https://github.com/costerwi',
        applicableModules=['Visualization', ],
        description='Hide elements selected in viewport and repeat.'
    )


class RemoveSectionPicked(ElementSelectProcedure):
    """CAE seems to register this class with the GuiMenuButton, not the instance of the class"""
    pass

toolset.registerGuiMenuButton(
        buttonText='Display Group|Remove picked &section assignment',
        object=RemoveSectionPicked(toolset, 'section to remove', 'removeSection', ONE),
        kernelInitString='import displayGroup',
        author='Carl Osterwisch',
        version=__version__,
        helpUrl='https://github.com/costerwi',
        applicableModules=['Visualization', ],
        description='Hide all elements of the selected section and repeat.'
    )
