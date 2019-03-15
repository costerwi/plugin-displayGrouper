"""displayGroup.py - Abaqus CAE functions to modify displayed elements

Carl Osterwisch, September 2017
"""

from __future__ import print_function
from time import time
from abaqus import session, milestone
import displayGroupOdbToolset as dgo

def addAdjacent():
    vp = session.viewports[session.currentViewportName]
    odb = session.odbs[vp.odbDisplay.name]

    activeNodes = vp.getActiveNodeLabels(printResults=False)
    nActiveElements = len(vp.getActiveElementLabels(printResults=False))
    nElements = 0 # Count number of elements added

    # TODO: Check for odb.rootAssembly elements
    # TODO: Check for odb.rootAssembly.rigidBodies

    for instName, nodeLabels in activeNodes.items():
        inst = odb.rootAssembly.instances[instName]
        nodeSet = set(nodeLabels)
        elements = []
        N = len(inst.elements)
        statusUpdate = 0
        for n, element in enumerate(inst.elements):
            if time() > statusUpdate:
                statusUpdate = time() + 2.5 # update every 2.5 seconds
                milestone(message='Checking {}'.format(instName),
                        percent=100*n/N)
            for node in element.connectivity:
                if node in nodeSet:
                    elements.append(element.label)
                    break
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelElemLabels(elementLabels=(
                (instName, elements), )))
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelNodeLabels(nodeLabels=(
                (instName, nodeLabels), )))
        nElements += len(elements)

    print('Added {} adjacent elements.'.format(nElements - nActiveElements))

if "__main__" == __name__:
    addAdjacent()
