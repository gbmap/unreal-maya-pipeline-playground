import re
from collections import defaultdict
from functools import partial


def remove_file_ext(s: str) -> str: return re.sub(r'\.[a-zA-Z0-9]+$', '', s)
def remove_repeated_chars(s: str, c: str): return re.sub(r'['+c+']{2,}', '_', s)

def format_preffix(name: str, target_preffix: str, preffix_capture: str) -> str:
    if name.startswith(target_preffix): 
        return name

    new_name = re.sub(preffix_regex(preffix_capture), target_preffix, name, count=1)
    if new_name != name: return new_name
    return target_preffix+name

# example for 'animation' preffix: ^([Aa][nimationANIMATION]*(?![a-z]))(\s|_)?
def preffix_regex(preffix: str): return f'^([{preffix[0].lower()}{preffix[0].upper()}][{preffix[1:].lower()}{preffix[1:].upper()}]*(?![a-z]))(\\s|_)?'
def has_preffix(s: str, preffix: str): return re.match(preffix_regex(preffix), s) is not None
def remove_preffix(string: str, preffix: str):
    if not has_preffix(string, preffix): return string
    return re.sub(preffix_regex(preffix), '', string)


def suffix_regex(suffix:str): return '(([A-Z]|\\s|_)['+ suffix.lower()+suffix.upper() +']{1,})$'
# def suffix_regex(suffix:str): return f'(\\s|_)?([{suffix[0].lower()}{suffix[0].upper()}][{suffix[1:].lower()}{suffix[1:].upper()}])*'
def has_suffix(string: str, suffix: str):  return re.search(suffix_regex(suffix), string) is not None
def remove_suffix(s: str, suffix: str): 
    if not has_suffix(s, suffix): return s
    return re.sub(suffix_regex(suffix), '', s)

def format_suffix(name: str, target_suffix: str, suffix_capture: str) -> str:
    if name.endswith(target_suffix): return name

    new_name = re.sub(suffix_regex(suffix_capture), target_suffix, name, count=1)
    if new_name != name: return new_name
    return name+target_suffix


def format_default_asset(basename: str, asset_name: str) -> str:
    final_name = remove_file_ext(asset_name)
    final_name = remove_preffix(asset_name, basename)
    final_name = remove_repeated_chars(asset_name, '_')
    final_name = format_preffix(final_name, f'{basename}_', basename)
    final_name = final_name.strip(' _')
    return final_name


TEXTURE_CAPTURE_RULES = [
    ('_Normal', 'normal'),
    ('_Albedo', 'albedo'),
    ('_Diffuse', 'diffuse'),
    ('_Mask', 'mask'),
    ('_Specular', 'specular'),
    ('_Color', 'color'),
    ('_Opacity', 'opacity')
]
def format_texture_name(basename: str, texture_name: str) -> str:
    found_rule = None
    for target_suffix, capture_rule in TEXTURE_CAPTURE_RULES:
        if has_suffix(texture_name, capture_rule):
            found_rule = (target_suffix, capture_rule)
            break

    final_name = remove_preffix(texture_name, 'texture')
    final_name = format_default_asset(basename, final_name)
    final_name = format_suffix(format_preffix(final_name, 'T_', 'TEXTUREtexture'), found_rule[0], found_rule[1]).replace(' ','_')
    return final_name

def _format_asset_name(basename: str, name: str, target_preffix: str, preffix_capture: str) -> str:
    final_name = remove_suffix(remove_preffix(name, preffix_capture), preffix_capture)
    final_name = format_default_asset(basename, final_name)
    return format_preffix(final_name, target_preffix, preffix_capture).replace(' ', '_')


ASSET_RENAME_FN_LOOKUP = defaultdict(lambda: format_default_asset)
for t in [
    ('Material', 'M_', 'material'),
    ('Skeleton', 'Sk_', 'skeleton'),
    ('SkeletalMesh', 'SkMsh_', 'mesh'),
    ('PhysicsAsset', 'Phys_', 'physicsasset'),
    ('Animation', 'A_', 'animation')
]:
    ASSET_RENAME_FN_LOOKUP[t[0]] = partial(_format_asset_name, target_preffix=t[1], preffix_capture=t[2])
ASSET_RENAME_FN_LOOKUP['Texture2D'] = format_texture_name

def format_asset_name(asset: str, asset_type: str, basename: str) -> str:
    return ASSET_RENAME_FN_LOOKUP.get(asset_type)(basename, asset)