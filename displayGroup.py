"""displayGroup.py - Abaqus CAE functions to modify displayed elements

Carl Osterwisch, September 2017
"""

from __future__ import print_function
from time import time
from abaqus import session, milestone, getInput, getWarningReply, CANCEL
import displayGroupOdbToolset as dgo
from functools import reduce

def addAdjacent():
    "Add elements touching displayed elements"
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return

    activeNodes = vp.getActiveNodeLabels(printResults=False)
    activeElements = vp.getActiveElementLabels(printResults=False)
    nElements = 0 # Count number of elements added

    # TODO: Check for odb.rootAssembly elements
    # TODO: Check for odb.rootAssembly.rigidBodies

    for instName, nodeLabels in activeNodes.items():
        inst = odb.rootAssembly.instances[instName]
        nodeSet = set(nodeLabels)
        elemSet = set(activeElements.get(instName, [])) # active intance elements
        elements = []
        N = max(1, len(inst.elements)/100)
        progressUpdate = 0
        for n, element in enumerate(inst.elements):
            if 0 == n%200 and time() > progressUpdate:
                progressUpdate = time() + 2.5 # update every 2.5 seconds
                milestone(message='Checking {}'.format(instName),
                        percent=n/N)
            if element.label in elemSet:
                continue # already displayed
            if not nodeSet.isdisjoint(element.connectivity):
                elements.append(element.label)
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelElemLabels(elementLabels=(
                (instName, elements), )))
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelNodeLabels(nodeLabels=(
                (instName, nodeLabels), )))
        nElements += len(elements)

    print('Added {} adjacent elements.'.format(nElements))

if "__main__" == __name__:
    addAdjacent()
