"""Create displayGroups of instances according to section assignments.

Run from File->Run Script... in Abaqus CAE

Carl Osterwisch, January 2018
"""

from __future__ import print_function
from abaqus import session, milestone

import displayGroupMdbToolset as dgm

def groupSections():
    "Organize instances into displayGroups according to section"
    vp = session.viewports[session.currentViewportName]
    ra = vp.displayedObject # rootAssembly in current viewport

    sectionInsts = {}  # dict of parts referencing each section
    for inst in ra.instances.values(): # iterate over all instances
        for sa in inst.part.sectionAssignments:
            sectionInsts.setdefault(sa.sectionName, []).append(inst)

    for secName, insts in sectionInsts.items():
        if session.displayGroups.has_key(secName):
            del session.displayGroups[secName] # remove existing displayGroup
        session.DisplayGroup(
                leaf=dgm.LeafFromInstance(instances=insts),
                name=secName)
    print('Updated', len(sectionInsts), 'named display groups.')

if '__main__' == __name__:
    groupSections() # run this function by default
