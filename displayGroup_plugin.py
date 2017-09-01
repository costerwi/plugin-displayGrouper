"""Abaqus/CAE plugins to modify the display group.

Carl Osterwisch, September 2017
"""

__VERSION__ = 0.1

from abaqusGui import *
from abaqusConstants import *

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerKernelMenuButton(
        moduleName='displayGroup',
        functionName='addAttached()',
        buttonText='Display Group|&Add Attached',
        author='Carl Osterwisch',
        description='Add elements attached to active nodes.',
        version=str(__VERSION__),
        applicableModules=['Mesh', 'Visualization'],
    )

