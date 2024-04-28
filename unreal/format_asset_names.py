import unreal

import unreal_utils as uu


def format_asset_names(package_name: str):
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    helper = unreal.AssetToolsHelpers.get_asset_tools()

    assets = reg.get_assets_by_package_name(package_name)
    renames = [None]*len(assets)
    for i, asset in enumerate(assets):
        new_name = uu.ASSET_RENAME_FN_LOOKUP.get(asset.class_path.asset_name)('', asset.asset_name)
        renames[i] = unreal.AssetRenameData(asset.get_asset(), asset.package_path, new_name)
    helper.rename_assets(renames)
