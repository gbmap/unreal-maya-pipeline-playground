"""
Batch processes mixamo animations in directory.
"""
from argparse import ArgumentParser
import os

from maya.standalone import initialize
import maya.cmds as cmds

use_newMayaAPI = True

os.environ['MAYA_PLUG_IN_PATH'] = f'D:\\Code\\maya-api\\maya\\plugins;{os.environ.get("MAYA_PLUG_IN_PATH")}' 

def batch_process(source: str, target: str, resample:int) -> None:
    initialize("python")
    initialize("mel")
    cmds.loadPlugin("fbxmaya")
    cmds.loadPlugin("preprocess_mixamo_animation.py")
    cmds.loadPlugin("resample_anim_curves.py")

    for file in [os.path.join(source,f) for f in os.listdir(source) if f.endswith('.fbx')]:
        print(f'[+] processing {file}...')

        print('\timporting')
        cmds.currentUnit(t='ntsc')
        cmds.file(file, i=True, type='Fbx', itr="override")

        print('\tprocessing rig')
        cmds.mixamo_rename()

        print('\tresampling anim curves')
        cmds.resample_anim_curves_all(n=resample)

        print(f'\texporting to {target}')
        export(os.path.join(target, os.path.basename(file)))

        cmds.file(f=True, new=True)

import maya.cmds as cmds
def export(target: str):
    cmds.FBXResetExport()
    cmds.FBXExportConvertUnitString('cm')
    cmds.FBXExportFileVersion('FBX201800')
    cmds.FBXExportSmoothMesh('-v', False)
    cmds.FBXExportBakeComplexAnimation('-v', True)
    cmds.FBXExportUseSceneName('-v', False)
    cmds.FBXExportUpAxis('z')
    cmds.FBXExportCameras('-v', False)
    cmds.FBXExportLights('-v', False)
    cmds.FBXExport('-f', target)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("source", help="Source folder to read animations from.")
    parser.add_argument("target", help="Target folder to save animations to.")
    parser.add_argument("--resample", type=int, default=12, help="Resamples animations at n frames per key.")
    args = parser.parse_args()

    batch_process(args.source, args.target, args.resample)
