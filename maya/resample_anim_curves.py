"""
Gets the animation curve of a joint and resamples all of its animation curves at
a configurable frames per key interval. Useful for simplifying mixamo animations
and editing them.
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, Dict


import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oam
import maya.OpenMayaUI as omui

from PySide6 import QtWidgets, QtCore


maya_useNewAPI = True

SHELF_BUTTON_NAMES = []


# https://forums.autodesk.com/t5/maya-programming/getting-the-frames-per-second-of-a-scene/td-p/6543383
def get_current_fps():
    from maya import mel
    time_unit = cmds.currentUnit(q=1,t=1)
    index = mel.eval(f'getIndexFromCurrentUnitCmdValue("{time_unit}")') - 1
    fps_name = mel.eval(f'getTimeUnitDisplayString({index});')
    return float(fps_name.split(' ')[0])
    

def get_unit_from_fps(fps: float):
    try:
        return { 
            24.0: om.MTime.k24FPS,
            30.0: om.MTime.k30FPS 
        }[fps]
    except KeyError as e:
        print(f'No key available: {fps}. Add it to resample_anim_curves.py. Running resample with 30 FPS.')
        return om.MTime.k30FPS

def _resample_selection(sel: om.MSelectionList, resample_resolution: int = 12) -> oam.MAnimCurveChange:
    fps = get_current_fps()
    time_unit = get_unit_from_fps(fps)
    min_frame = int(cmds.playbackOptions(query=True, ast=True))
    max_frame = int(cmds.playbackOptions(query=True, aet=True))

    curve_change = defaultdict(oam.MAnimCurveChange)

    for i in range(sel.length()):
        mobj = sel.getDependNode(i)
        mdag = sel.getDagPath(i)
        if mobj.apiType() != om.MFn.kJoint:
            print(f'Skipping {mobj} ({mobj.apiType()}, expected: {om.MFn.kJoint})')
            continue

        print(f'Resampling curves for object: {mdag.fullPathName()} at {resample_resolution} frames per key')
        for animated_plug in oam.MAnimUtil.findAnimatedPlugs(mobj):
            anim_curve = oam.MFnAnimCurve(animated_plug)

            print(f'\t{animated_plug}: {anim_curve.numKeys} ({anim_curve.animCurveType}) (Unitless: {anim_curve.isUnitlessInput}, TimeInput: {anim_curve.isTimeInput})')

            times, values = om.MTimeArray(), om.MDoubleArray()
            for f in range(min_frame+1, max_frame-1, resample_resolution):
                times.append(om.MTime(f, time_unit))
                values.append(anim_curve.evaluate(f/fps))

            times.append(om.MTime(max_frame, time_unit))
            values.append(anim_curve.evaluate((max_frame-1)/fps))

            while anim_curve.numKeys > 0:
                anim_curve.remove(0, change=curve_change[mdag.fullPathName()])

            anim_curve.addKeys(times, values, change=curve_change[mdag.fullPathName()])

    return curve_change
        

def _resample_all(resample_resolution: int = 12):
    sel = om.MSelectionList()
    for joint in [o for o in cmds.ls() if cmds.objectType(o, isa='joint')]:
        sel.add(joint)
    return _resample_selection(sel, resample_resolution)


class ResampleAnimCurvesBase(ABC, om.MPxCommand):
    def __init__(self): 
        super().__init__()
        self.change_caches = defaultdict(oam.MAnimCurveChange)

    def hasSyntax(self): return True
    def isUndoable(self): return True # for now
    def redoIt(self): self.doIt(None)

    def syntax(self):
        syntax = om.MSyntax()
        syntax.addFlag("-n", "--n_frames", om.MSyntax.kLong)
        return syntax

    def doIt(self, args): 
        self.argumentParser(args)
        self.change_caches = self.run(self.n_frames)

    def undoIt(self): 
        for change_cache in self.change_caches.values():
            change_cache.undoIt()

    def argumentParser(self, args):
        parser = om.MArgDatabase(self.syntax(), args)

        for flag in ['--n_frames', '-n']:
            if parser.isFlagSet(flag):
                self.n_frames = int(parser.flagArgumentInt(flag, 0))
                break

        if not hasattr(self, 'n_frames'):
            self.n_frames = 12

    def __del__(self):
        for change in self.change_caches.values():
            del change

    @abstractmethod
    def run(self, n_frames: int) -> Dict[str, oam.MAnimCurveChange]:
        pass

    @classmethod
    def creator(cls): 
        return cls()


class ResampleAnimCurves(ResampleAnimCurvesBase):
    def run(self, n_frames: int) -> Dict[str, oam.MAnimCurveChange]:
        return _resample_selection(om.MGlobal.getActiveSelectionList(), n_frames)
    
class ResampleAnimCurvesAll(ResampleAnimCurves):
    def run(self, n_frames: int) -> Dict[str, oam.MAnimCurveChange]:
        return _resample_all(n_frames)


# ================================
#               UI
# ================================


class ResampleAnimCurvesWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.setWindowTitle("Resample Animations")
        self.resize(300, 100)
        
        # Create a vertical layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(text="Number of Frames per Key"))
        
        # Create a slider
        btn_layout = QtWidgets.QHBoxLayout(self)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(30)
        self.slider.setValue(12)
        self.slider.valueChanged.connect(self.hndlr_slider_changed)
        btn_layout.addWidget(self.slider)

        self.lbl_slider = QtWidgets.QLabel(self)
        self.lbl_slider.setText('30')
        btn_layout.addWidget(self.lbl_slider)
        layout.addLayout(btn_layout)

        self.btn_sel = QtWidgets.QPushButton(text="Run For Selection")
        self.btn_sel.clicked.connect(self.hndlr_run_sel)
        layout.addWidget(self.btn_sel)

        self.btn_all = QtWidgets.QPushButton(text="Run For All Joints")
        self.btn_all.clicked.connect(self.hndlr_run_all)
        layout.addWidget(self.btn_all)
        
    def hndlr_slider_changed(self, value):
        self.slider_value = value
        self.lbl_slider.setText(str(value))

    def hndlr_run_sel(self):
        cmds.resample_anim_curves(n=int(self.slider_value))

    def hndlr_run_all(self):
        cmds.resample_anim_curves_all(n=int(self.slider_value))


class ResampleAnimCurveUI(om.MPxCommand):
    def __init__(self): super().__init__()
    def isUndoable(self): return False
    def hasSyntax(self): return False

    def doIt(self, args):
        from shiboken6 import wrapInstance
        mayaWindow = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QMainWindow)
        window = ResampleAnimCurvesWindow(parent=mayaWindow)
        window.show()

    @classmethod
    def creator(cls): 
        return cls()


def add_cmd_to_shelf(label:str, cmd: Callable[[None], None], icon:str = None, tgt_tab: str = 'Rigging') -> str:
    return cmds.shelfButton(label=label, command=cmd, parent=tgt_tab, image=icon)

def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin, 'Me', '0.1')
    plugin_fn.registerCommand("resample_anim_curves", ResampleAnimCurves.creator)
    plugin_fn.registerCommand("resample_anim_curves_all", ResampleAnimCurvesAll.creator)

    plugin_fn.registerCommand("resample_anim_curves_ui", ResampleAnimCurveUI.creator)
    SHELF_BUTTON_NAMES.append(cmds.separator(parent='Animation'))
    SHELF_BUTTON_NAMES.append(add_cmd_to_shelf("Resample Anim Curves UI", cmds.resample_anim_curves_ui, icon='setKeyOnAnim.png', tgt_tab='Animation'))


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    plugin_fn.deregisterCommand("resample_anim_curves")
    plugin_fn.deregisterCommand("resample_anim_curves_all")
    plugin_fn.deregisterCommand("resample_anim_curves_ui")

    while len(SHELF_BUTTON_NAMES) > 0:
        cmds.deleteUI(SHELF_BUTTON_NAMES.pop())
