"""displayGroup.py - Abaqus CAE functions to modify displayed elements

Carl Osterwisch, September 2017
"""

from __future__ import print_function
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
        for n, element in enumerate(inst.elements):
            if 0 == n%10000:
                milestone(message='Checking {}'.format(instName),
                        object='Elements',
                        done=n,
                        total=N)
            for node in element.connectivity:
                if node in nodeSet:
                    elements.append(element.label)
                    break
        milestone(message='Checking {}'.format(instName),
                object='Elements',
                done=N,
                total=N)
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelElemLabels(elementLabels=(
                (instName, elements), )))
        nElements += len(elements)

    print('Added {} adjacent elements.'.format(nElements - nActiveElements))

if "__main__" == __name__:
    addAdjacent()
