"""Abaqus/CAE plugins to modify the display group.

Latest version: https://github.com/costerwi/plugin-displayGrouper

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
                objectName='displayGrouper',
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
        moduleName='displayGrouper',
        functionName='addAdjacent()',
        buttonText='Display Grouper|Add ad&jacent elements',
        author='Carl Osterwisch',
        description='Add elements that are attached to active nodes.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


toolset.registerKernelMenuButton(
        moduleName='displayGrouper',
        functionName='addAttached()',
        buttonText='Display Grouper|Add a&ttached elements',
        author='Carl Osterwisch',
        description='Add elements that are attached to active elements.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


toolset.registerKernelMenuButton(
        moduleName='displayGrouper',
        functionName='addNearby()',
        buttonText='Display Grouper|Add &nearby elements...',
        author='Carl Osterwisch',
        description='Add elements with undeformed nodes close to active undeformed nodes.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


toolset.registerKernelMenuButton(
        moduleName='displayGrouper',
        functionName='addIncompleteSections()',
        buttonText='Display Grouper|Add &same section assignment elements',
        author='Carl Osterwisch',
        description='Add elements with same section assignment as active elements.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


toolset.registerKernelMenuButton(
        moduleName='displayGrouper',
        functionName='createFromSections()',
        buttonText='Display Grouper|Create &named from section assignments',
        author='Carl Osterwisch',
        description='Create a named display group for each section definition.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


toolset.registerKernelMenuButton(
        moduleName='displayGrouper',
        functionName='listActiveSections()',
        buttonText='Display Grouper|&List section assignments of active elements',
        author='Carl Osterwisch',
        description='List sections for displayed elements.',
        version=__version__,
        applicableModules=['Visualization'],
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
    )


class RemoveElementsPicked(ElementSelectProcedure):
    """CAE seems to register this class with the GuiMenuButton, not the instance of the class"""
    pass

toolset.registerGuiMenuButton(
        buttonText='Display Grouper|Remove picked &elements',
        object=RemoveElementsPicked(toolset, 'elements to remove', 'removeElements', MANY),
        kernelInitString='import displayGrouper',
        author='Carl Osterwisch',
        version=__version__,
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
        applicableModules=['Visualization', ],
        description='Hide elements selected in viewport and repeat.'
    )


class RemoveSectionPicked(ElementSelectProcedure):
    """CAE seems to register this class with the GuiMenuButton, not the instance of the class"""
    pass

toolset.registerGuiMenuButton(
        buttonText='Display Grouper|Remove elements with picked &section assignment',
        object=RemoveSectionPicked(toolset, 'section to remove', 'removeSection', ONE),
        kernelInitString='import displayGrouper',
        author='Carl Osterwisch',
        version=__version__,
        helpUrl='https://github.com/costerwi/plugin-displayGrouper',
        applicableModules=['Visualization', ],
        description='Hide all elements of the selected section and repeat.'
    )
