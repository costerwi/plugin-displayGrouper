""" Abaqus CAE functions to modify displayed elements

Latest version: https://github.com/costerwi/plugin-displayGrouper

Carl Osterwisch, September 2017
"""

from __future__ import print_function
from time import time
from abaqus import session, milestone, getInput, getWarningReply, YES, NO, CANCEL
import displayGroupOdbToolset as dgo
import os

DEBUG = os.environ.get('DEBUG')

def addAdjacent():
    "Add elements touching displayed elements"
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return

    activeNodes = vp.getActiveNodeLabels(printResults=False)
    activeElements = vp.getActiveElementLabels(printResults=False)
    adjacentElements = [] # elements adjacent to activeElements to add to display group

    # TODO: Check for odb.rootAssembly elements
    # TODO: Check for odb.rootAssembly.rigidBodies

    for instName, nodeLabels in activeNodes.items():
        inst = odb.rootAssembly.instances[instName]
        nodeSet = set(nodeLabels)
        elemSet = set(activeElements.get(instName, [])) # active intance elements
        elements = []
        progressTime = 0
        for eIndex, element in enumerate(inst.elements):
            if 0 == eIndex%1000 and time() > progressTime:
                progressTime = time() + 2.5 # update every 2.5 seconds
                milestone(message='Checking {}'.format(instName),
                        object='element', done=eIndex, total=len(inst.elements))
            if element.label in elemSet:
                continue # already displayed
            if not nodeSet.isdisjoint(element.connectivity):
                elements.append(element.label)
        if elements:
            adjacentElements.append([instName, elements])
    if adjacentElements:
        leaf=dgo.LeafFromModelElemLabels(elementLabels=adjacentElements)
        vp.odbDisplay.displayGroup.add(leaf=leaf)
    print('Added {} adjacent elements.'.format(
        sum( [len(elementLabels) for instName, elementLabels in adjacentElements] )))


def addAttached():
    "Add all elements attached to displayed elements"
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return

    activeElements = vp.getActiveElementLabels(printResults=False)
    attachedElements = [] # elements attached to activeElements to add to display group

    for instName, elementLabels in activeElements.items():
        inst = odb.rootAssembly.instances[instName]
        elemLabelsSet = set(activeElements.get(instName, [])) # active intance elements

        elemIndex = set() # index of attached elements
        nodeToElemIndex = {} # map nodeId to element index
        progressTime = 0
        for eIndex, element in enumerate(inst.elements):
            if 0 == eIndex%1000 and time() > progressTime:
                progressTime = time() + 2.5 # update every 2.5 seconds
                milestone(message='Checking {}'.format(instName),
                        object='element', done=eIndex, total=len(inst.elements))
            if element.label in elemLabelsSet:
                elemIndex.add(eIndex)
            for nid in element.connectivity:
                nodeToElemIndex.setdefault(nid, []).append(eIndex)

        elemIndexNew = set(elemIndex)
        while len(elemIndexNew):
            nodes = set() # collect node labels for all elemIndexNew elements
            for eIndex in elemIndexNew:
                nodes.update(inst.elements[eIndex].connectivity)
            for nid in nodes: # add elements using node labels
                elemIndexNew.update(nodeToElemIndex[nid])
            elemIndexNew.difference_update(elemIndex) # just the freshest elements
            elemIndex.update(elemIndexNew)

        if elemIndex:
            addElements = set([inst.elements[eIndex].label
                for eIndex in elemIndex]).difference(elementLabels)
            attachedElements.append([instName, list(addElements)])

    if attachedElements:
        vp.odbDisplay.displayGroup.add(
            leaf=dgo.LeafFromModelElemLabels(elementLabels=attachedElements))


def addIncompleteSections():
    """Add entire sections for active elements"""
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return
    ra = odb.rootAssembly
    elementSections = set()
    activeElements = vp.getActiveElementLabels(printResults=False)
    for instanceName, elementLabels in activeElements.items():
        instance = ra.instances[instanceName]
        for sa in instance.sectionAssignments:
            saRegion = {element.label for element in sa.region.elements}
            if saRegion.isdisjoint(elementLabels):
                continue # no match
            elementSections.add('.'.join([instance.name, sa.region.name, sa.sectionName]))
    leaf = dgo.LeafFromOdbElementSections(elementSections=list(elementSections))
    vp.odbDisplay.displayGroup.add(leaf=leaf)


def addNearby(r=None):
    "Add elements with undeformed nodes close to active undeformed nodes"
    # TODO: consider deformation
    import numpy as np
    try:
        from scipy.spatial import KDTree
    except ImportError:
        getWarningReply('"Add nearby" requires Abaqus CAE 2020 or greater', (CANCEL,))
        return
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return

    activeNodes = vp.getActiveNodeLabels(printResults=False)
    n = sum( [len(nodeLabels) for nodeLabels in aciveNodes.values()] )
    if n > 5000:
        reply = getWarningReply('Search may take a long time with {} active nodes.\n'
            'Okay to continue?'.format(n), (YES, NO))
        if NO == reply:
            return

    if r is None:
        r = getInput('Enter search radius:', '2')
        if r is None:  # cancelled
            return
        r = float(r)

    activePoints = []
    t0 = time()
    if DEBUG: print(time() - t0, 'Collect active points')
    for instName, nodeLabels in activeNodes.items():
        inst = odb.rootAssembly.instances[instName]
        activePoints.extend([inst.getNodeFromLabel(n).coordinates for n in nodeLabels])
    if DEBUG: print(time() - t0, 'Make active KDTree', len(activePoints))
    activeTree = KDTree(activePoints)

    activeElements = vp.getActiveElementLabels(printResults=False)
    nearbyElements = []
    for inst in odb.rootAssembly.instances.values():
        if DEBUG: print(time() - t0, 'Collect', inst.name, 'points')
        points = [node.coordinates for node in inst.nodes]
        if DEBUG: print(time() - t0, 'Make inst KDTree', len(points))
        instTree = KDTree(points)
        if DEBUG: print(time() - t0, 'Compare trees')
        nIndex = set()
        nIndex.update(*activeTree.query_ball_tree(instTree, r))
        nodeLabels = {inst.nodes[i].label for i in nIndex}
        if DEBUG: print(time() - t0, 'Find attached elements', len(nodeLabels))

        elemSet = set(activeElements.get(instName, [])) # active intance elements
        elements = []
        progressTime = 0
        for eIndex, element in enumerate(inst.elements):
            if 0 == eIndex%1000 and time() > progressTime:
                progressTime = time() + 2.5 # update every 2.5 seconds
                milestone(message='Checking {}'.format(inst.name),
                        object='element', done=eIndex, total=len(inst.elements))
            if element.label in elemSet:
                continue # already displayed
            if not nodeLabels.isdisjoint(element.connectivity):
                elements.append(element.label)
        if elements:
            nearbyElements.append([instName, elements])
    if nearbyElements:
        leaf = dgo.LeafFromModelElemLabels(elementLabels=nearbyElements)
        vp.odbDisplay.displayGroup.add(leaf=leaf)
    if DEBUG: print(time() - t0, 'Done')
    print('Added {} nearby elements.'.format(
        sum( [len(elementLabels) for instName, elementLabels in nearbyElements] )))


def createFromSections():
    """Create named display groups based on section definitions"""
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return
    ra = odb.rootAssembly
    sections = {}
    for instance in ra.instances.values():
        for sa in instance.sectionAssignments:
            elementLabels = [element.label for element in sa.region.elements]
            sections.setdefault(sa.sectionName, []).append(
                    [instance.name, elementLabels] )
    for sectionName, elementLabels in sections.items():
        if session.displayGroups.has_key(sectionName):
            del session.displayGroups[sectionName] # remove existing displayGroup
        session.DisplayGroup(
            leaf=dgo.LeafFromModelElemLabels(elementLabels=elementLabels),
            name=sectionName)
    print('Created {} display groups.'.format(len(sections)))


def listActiveSections():
    """List active sections, materials, and elements"""
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return
    ra = odb.rootAssembly

    activeElements = vp.getActiveElementLabels(printResults=False)
    sections = []
    for instanceName, elementLabels in activeElements.items():
        instance = ra.instances[instanceName]
        for sa in instance.sectionAssignments:
            saRegion = {element.label for element in sa.region.elements}
            common = saRegion.intersection(elementLabels)
            if not common:
                continue # no match
            material = ''
            if sa.sectionName in odb.sections:
                section = odb.sections[sa.sectionName]
                if hasattr(section, 'material') and section.material:
                    material = section.material
            sections.append([sa.sectionName, material, len(common)])
    for section, material, nElements in sorted(sections):
        print('{:40s} {:30s} {} elements'.format(section, material, nElements))


def removeElement(element):
    """Hide selected element"""
    vp = session.viewports[session.currentViewportName]
    leaf = dgo.LeafFromElementLabels(element.instanceName, [element.label])
    vp.odbDisplay.displayGroup.remove(leaf=leaf)


def removeElements(elements):
    """Hide selected elements"""
    vp = session.viewports[session.currentViewportName]
    instElements = {}
    for element in elements:  # group elements by instanceName
        instElements.setdefault(element.instanceName, []).append(element.label)
    leaf=dgo.LeafFromModelElemLabels(elementLabels=list(instElements.items()))
    vp.odbDisplay.displayGroup.remove(leaf=leaf)


def removeSection(element):
    """Hide all elements of the selected section"""
    vp = session.viewports[session.currentViewportName]
    odb = vp.displayedObject
    if not hasattr(odb, 'rootAssembly'):
        getWarningReply('Must have odb displayed in viewport', (CANCEL,))
        return
    ra = odb.rootAssembly
    instance = ra.instances[element.instanceName]
    for sa in instance.sectionAssignments: # find section for this element
        if element in sa.region.elements:
            break
    else:
        getWarningReply('No section assignment found for selected element', (CANCEL,))
        return
    elementSection = '.'.join([instance.name, sa.region.name, sa.sectionName])
    print(elementSection)
    leaf = dgo.LeafFromOdbElementSections(elementSections=(elementSection, ))
    vp.odbDisplay.displayGroup.remove(leaf=leaf)
