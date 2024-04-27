import unreal
import re
import os
from argparse import ArgumentParser

import unreal_utils as uu

def format_animation_filename(name: str, target_preffix: str = 'A_'):
    """
    Maps:
        ATest.fbx -> A_Test.fbx
        A_Test Something.fbx -> A_TestSomething.fbx
        AnimZombieAttack00.fbx -> A_ZombieAttack00.fbx
        Anim_ZombieAttack02_final.fbx -> A_ZombieAttack02_final.fbx
        Anm_ZombieAttack03 final fina.fbx -> A_ZombieAttack03finalfina.fbx
        ZombieAttack02.fbx -> A_ZombieAttack02.fbx
    """
    if (m:=re.match(r'[animationA]+((\s|_)?)', name)):
        if m.start(0) == 0:
            name = name.replace(m.group(0), target_preffix)
        else:
            name = target_preffix + name
    return os.path.splitext(name.replace(' ', ''))[0]


def import_animations(directory: str, destination_path: str, skeleton_asset: str) -> None:
    assert directory is not None and isinstance(directory, str), f"invalid directory passed {directory}"
    assert destination_path is not None and isinstance(destination_path, str), f"invalid destination_path passed {destination_path}"
    assert skeleton_asset is not None and isinstance(skeleton_asset, str), f"invalid skeleton_asset passed {skeleton_asset}"

    tasks = []
    for fname in list(map(lambda f: os.path.join(directory,f), os.listdir(directory))):
        task = unreal.AssetImportTask()
        task.filename = fname
        task.destination_path = destination_path
        task.destination_name = uu.format_preffix(os.path.basename(fname), 'A_', 'Aanimation')

        task.replace_existing = True
        task.automated = True
        task.save = True

        task.options = unreal.FbxImportUI()
        task.options.import_materials = False
        task.options.import_animations = True
        task.options.import_as_skeletal = True
        task.options.import_mesh = False

        task.options.skeleton = unreal.load_asset(skeleton_asset)
        task.options.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION 
        task.options.automated_import_should_detect_type = False
        tasks.append(task)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("destination_path")
    parser.add_argument("skeleton_asset")

    args = parser.parse_args()
    import_animations(args.directory, args.destination_path, args.skeleton_asset)
