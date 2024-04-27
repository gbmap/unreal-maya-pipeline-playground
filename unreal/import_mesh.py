from argparse import ArgumentParser
import unreal
import os

import unreal_utils as uu

def import_mesh(source_fbx: str, destination_path: str):
    assert source_fbx is not None and isinstance(source_fbx, str), f"invalid source_fbx passed: {source_fbx}"
    assert destination_path is not None and isinstance(destination_path, str), f"invalid destination_path passed: {destination_path}"
    assert os.path.isfile(source_fbx), f"{source_fbx} does not exist"

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

    reg = unreal.AssetRegistryHelpers.get_asset_registry()

    assets_created = reg.get_assets_by_path(destination_path)
    for asset in assets_created:
        postproc_asset(task_mesh.destination_name, asset)

def postproc_asset(basename: str, asset: unreal.AssetData):
    asset_type = str(asset.asset_class_path.asset_name)
    print(f'=========================================== {asset_type}')

    helper = unreal.AssetToolsHelpers.get_asset_tools()

    name_without_ext = filter(lambda s: len(s) > 0, os.path.splitext(str(asset.asset_name))).__iter__().__next__()
    new_name = uu.ASSET_RENAME_FN_LOOKUP.get(asset_type, uu.format_default_asset)(basename, name_without_ext)
    rename = unreal.AssetRenameData(
        asset.get_asset(), 
        new_package_path=asset.package_path, 
        new_name=new_name
    )
    helper.rename_assets([rename])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("source_fbx")
    parser.add_argument("destination_path")

    args = parser.parse_args()
    import_mesh(args.source_fbx, args.destination_path)


