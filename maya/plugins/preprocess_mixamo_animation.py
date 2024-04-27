"""
Removes mixamorig: prefix from joints, replaces Left/Right preffixes with L_/R_ and adds a Root bone to the rig.
"""
import maya.api.OpenMaya as om
import maya.cmds as cmds
from typing import Callable
import re

maya_useNewAPI = True

SHELF_BUTTONS = []

class PreprocessMixamoAnimation(om.MPxCommand):

    def __init__(self):
        super().__init__()
        self.preffix_mapping = {
            'Left_?|L(?!_)': 'L_',
            'Right_?|R(?!_)': 'R_'
        }

        self.renamed = {}

    def isUndoable(self): return True
    def redoIt(self): self.doIt(None)


    def doIt(self, args):
        self.rename_bones()
        self.add_root_bone()

    def undoIt(self):
        for new_name, old_name in self.renamed.items():
            mdep_node = om.MFnDependencyNode(om.MGlobal.getSelectionListByName(new_name).getDependNode(0))
            mdep_node.setName(old_name)

    def rename_bones(self):
        joints = [o for o in cmds.ls() if cmds.objectType(o, isa='joint')]

        for joint_name in joints:
            msel = om.MGlobal.getSelectionListByName(joint_name)
            mobj = msel.getDependNode(0)

            mdep_node = om.MFnDependencyNode(mobj)
            old_name = mdep_node.name()
            new_name = old_name.replace('mixamorig:', '')
            for regex_preffix, new_preffix in self.preffix_mapping.items():
                m: re.Match[str] = re.match(regex_preffix, new_name)
                if m is None: 
                    continue

                new_name = new_name.replace(m.group(0), new_preffix)
            
            mdep_node.setName(new_name)
            self.renamed[new_name] = old_name

    def add_root_bone(self):
        joints, root_joint = [o for o in cmds.ls() if cmds.objectType(o, isa='joint')], None
        while len(joints) > 0 and root_joint is None:
            joint = joints.pop(0)
            if cmds.listRelatives(joint, parent=True) is None:
                root_joint = joint
                break
        
        if root_joint is None:
            raise ValueError("Couldn't find root bone.")

        cmds.select(clear=True)
        cmds.joint(name="Root", p=(0.0,0.0,0.0))
        cmds.parent(root_joint, "Root")

    @classmethod
    def creator(cls):
        return PreprocessMixamoAnimation()

def add_cmd_to_shelf(label:str, cmd: Callable[[None], None], icon:str = None, tgt_tab: str = 'Rigging'):
    return cmds.shelfButton(label=label, command=cmd, parent=tgt_tab, image=icon)


def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin, 'Me', '0.1')
    plugin_fn.registerCommand("mixamo_rename", PreprocessMixamoAnimation.creator)
    SHELF_BUTTONS.append(add_cmd_to_shelf("Format Joint Names", cmds.mixamo_rename, icon='kinJoint.png', tgt_tab='Rigging'))


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    plugin_fn.deregisterCommand("mixamo_rename")

    while len(SHELF_BUTTONS) > 0:
        cmds.deleteUI(SHELF_BUTTONS.pop())
