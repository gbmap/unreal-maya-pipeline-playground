from argparse import ArgumentParser
import unreal
import os

import sys
sys.path.append("D:\\Code\\maya-api\\unreal")

import unreal_utils as uu

def import_mesh(source_fbx: str, destination_path: str):
    assert source_fbx is not None and isinstance(source_fbx, str), f"invalid source_fbx passed: {source_fbx}"
    assert destination_path is not None and isinstance(destination_path, str), f"invalid destination_path passed: {destination_path}"
    assert os.path.isfile(source_fbx), f"{source_fbx} does not exist"

    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    helper = unreal.AssetToolsHelpers.get_asset_tools()

    # add old_ preffix to old assets
    assets_on_path = reg.get_assets_by_path(destination_path)
    helper.rename_assets([unreal.AssetRenameData(a.get_asset(), a.package_path, f'old_{a.asset_name}') for a in assets_on_path])

    # import mesh/material/skeleton
    task_mesh = unreal.AssetImportTask()
    task_mesh.filename = source_fbx
    task_mesh.destination_path = destination_path
    task_mesh.destination_name = uu.remove_file_ext(os.path.basename(source_fbx))
    task_mesh.replace_existing = True
    task_mesh.automated = True
    task_mesh.save = True

    options = unreal.FbxImportUI()
    options.import_materials = True
    options.import_as_skeletal = True
    options.import_mesh = True
    options.import_animations = False
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    options.automated_import_should_detect_type = False
    task_mesh.options = options

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task_mesh])

    # rename newly imported assets
    renames = [get_rename_data(task_mesh.destination_name, asset) for asset in reg.get_assets_by_path(destination_path)]
    helper.rename_assets(renames)

    # the code below breaks unreal ):
    # # consolidate to equivalent old assets
    # editor_asset_library = unreal.EditorAssetLibrary()
    # for asset in reg.get_assets_by_path(destination_path):
    #     old_asset_path = f'{asset.package_path}/old_{asset.asset_name}'
    #     if (old_asset:=reg.get_asset_by_object_path(old_asset_path)).package_name == "":
    #         continue

    #     editor_asset_library.consolidate_assets(asset.get_asset(),[old_asset.get_asset()])

    # # remove all old assets
    # for asset in reg.get_assets_by_path(destination_path):
    #     if str(asset.asset_name).startswith('old_'):
    #         editor_asset_library.delete_asset(asset.package_name)


def get_rename_data(basename: str, asset: unreal.AssetData):
    asset_type = str(asset.asset_class_path.asset_name)
    name_without_ext = filter(lambda s: len(s) > 0, os.path.splitext(str(asset.asset_name))).__iter__().__next__()
    new_name = uu.ASSET_RENAME_FN_LOOKUP.get(asset_type, uu.format_default_asset)(basename, name_without_ext)

    unreal.log(f'Renaming file {asset.asset_name} -> {new_name}')
    return unreal.AssetRenameData(asset.get_asset(), asset.package_path, new_name)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("source_fbx")
    parser.add_argument("destination_path")

    args = parser.parse_args()
    import_mesh(args.source_fbx, args.destination_path)


