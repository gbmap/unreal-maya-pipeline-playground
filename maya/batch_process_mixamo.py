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


    mesh_dir = os.path.join(source, 'Mesh')
    assert os.path.isdir(mesh_dir), "needs a folder called Mesh in source dir"

    mesh_files = [f for f in os.listdir(mesh_dir) if f.endswith('.fbx')]
    assert len(mesh_files) == 1, "only one mesh file allowed in mesh file"


    mesh_file = os.path.join(mesh_dir, mesh_files[0])
    target_mesh_path = os.path.join(target, 'Mesh', os.path.basename(mesh_file))
    os.makedirs(os.path.dirname(target_mesh_path), exist_ok=True)

    print(f'[+] processing mesh: {mesh_file}')
    cmds.currentUnit(t='ntsc')
    cmds.file(mesh_file, i=True, type='Fbx', itr='override')
    cmds.mixamo_rename()


    export(target_mesh_path)
    cmds.file(f=True, new=True)

    target_anim_folder = os.path.join(target, 'Anims')
    os.makedirs(target_anim_folder, exist_ok=True)

    anim_src_dir = os.path.join(source, 'Anims')
    files = [os.path.join(anim_src_dir,f) for f in os.listdir(anim_src_dir) if f.endswith('.fbx')]
    for file in files:
        print(f'[+] processing animation: {file}...')

        print('\timporting')
        cmds.currentUnit(t='ntsc')
        cmds.file(file, i=True, type='Fbx', itr="override")

        print('\tprocessing rig')
        cmds.mixamo_rename()

        print('\tresampling anim curves')
        cmds.resample_anim_curves_all(n=resample)

        target_anim_path = os.path.join(target_anim_folder, os.path.basename(file))
        print(f'\texporting to {target}')

        export(target_anim_path)

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
