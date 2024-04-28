import os
import subprocess

from argparse import ArgumentParser

from unreal import unreal_utils as uu

# import skeleton and process in maya
# export skeleton to unreal
# iterate over all animations in folder,
#   export fbx
#   read fbxs in unreal and import

PATH_MAYAPY="C:\\Program Files\\Autodesk\\Maya2025\\bin\\mayapy.exe"
PATH_UNREAL="E:\\UE_5.3\\Engine\\Binaries\\Win64\\UnrealEditor.exe"
PROJECT_PATH="E:\\UnrealProjects\\MyProject\\MyProject.uproject"

def run(
    path_mayapy: str, path_unreal_editor: str,
    source_folder: str, maya_processed_folder: str, 
    unreal_project: str, unreal_package_path: str
):
    print('running maya batch job')
    proc = subprocess.run([path_mayapy, os.path.join('maya', 'batch_process_mixamo.py'), source_folder, maya_processed_folder])
    proc.check_returncode()

    mesh_dir = os.path.join(maya_processed_folder, "Mesh")
    mesh_file = os.path.join(mesh_dir, [f for f in os.listdir(mesh_dir) if f.endswith('.fbx')][0])

    print('running ue mesh import job')
    ue_script_arg = f'{os.path.abspath(os.path.join("unreal", "import_mesh.py"))} {mesh_file} {unreal_package_path}'
    proc = subprocess.run([path_unreal_editor, unreal_project, '-run=pythonscript', f'-Script={ue_script_arg}'])
    proc.check_returncode()

    print('running ue animation import job')
    basename = uu.remove_file_ext(os.path.basename(mesh_file))
    skeleton_path = os.path.join(unreal_package_path, uu.format_asset_name(basename, 'Skeleton', basename))
    maya_anims_processed_folder = os.path.join(maya_processed_folder, 'Anims')
    unreal_package_path = os.path.join(unreal_package_path, 'Anims')
    ue_script_arg = f'{os.path.abspath(os.path.join("unreal", "import_animations.py"))} {maya_anims_processed_folder} {unreal_package_path} {skeleton_path}'
    proc = subprocess.run([path_unreal_editor, unreal_project, '-run=pythonscript', f'-Script={ue_script_arg}'])
    proc.check_returncode()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("source_folder", help="Folder containing .fbx files to be processed by Maya.")
    parser.add_argument("unreal_project", help="Unreal project path")
    parser.add_argument("unreal_package_path", help="Target unreal package path.")

    args = parser.parse_args()

    processed_folder = f'{args.source_folder}_Processed'
    run(PATH_MAYAPY, PATH_UNREAL, args.source_folder, processed_folder, args.unreal_project, args.unreal_package_path)


