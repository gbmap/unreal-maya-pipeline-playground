import unittest

import sys
sys.path.append("../unreal/")


from unreal import unreal_utils as uu


class TestAssetRename(unittest.TestCase):

    def test_remove_file_ext(self):
        cases = [
            ('some file.jpg', 'some file'),
            ('SomeOtherFile final (1).png', 'SomeOtherFile final (1)'),
            ('someonedroppedazip.zip', 'someonedroppedazip'),
        ]
        for case in cases:
            self.assertEqual(uu.remove_file_ext(case[0]), case[1])


    def test_format_preffix(self):
        cases = [
            ('ATest' , 'A_Test'),
            ('A_Test Something' , 'A_Test Something'),
            ('AnimZombieAttack00' , 'A_ZombieAttack00'),
            ('Anim_ZombieAttack02_final' , 'A_ZombieAttack02_final'),
            ('Anm_ZombieAttack03 final fina', 'A_ZombieAttack03 final fina'),
            ('ZombieAttack02' , 'A_ZombieAttack02'),
            ('anim some animation', 'A_some animation'),
            ('Anim some animation', 'A_some animation'),
            ('A some animation', 'A_some animation'),
            ('amin_test_animation', 'A_test_animation')
        ]
        for case in cases:
            self.assertEqual(uu.format_preffix(case[0], 'A_', 'ANIManim'), case[1])

    def test_format_suffix(self):
        cases = [
            ('T_SomeTexture', 'T_SomeTexture_Normal'),
            ('SomeTextureNormal', 'SomeTexture_Normal'),
            ('some texture normal', 'some texture_Normal'),
            ('opacity albedo normal', 'opacity albedo_Normal'),
            ('sometexture_normal', 'sometexture_Normal')
        ]
        for case in cases:
            self.assertEqual(uu.format_suffix(case[0], '_Normal', 'NORMALnormal'), case[1])

    def test_remove_preffix(self):
        cases = [
            ('Txtr_Test', 'texture', 'Test'),
            ('SomePreffix Removed', 'somepreffix', 'Removed'),
            ('NormalWhatever', 'normal', 'Whatever')
        ]
        for case in cases:
            self.assertEqual(uu.remove_preffix(case[0], case[1]), case[2])


    def test_format_textures(self):
        cases = [
            ('SomeTextureNormal', 'T_Zombie_SomeTexture_Normal'),
            ('SomeTextureAlbedo', 'T_Zombie_SomeTexture_Albedo'),
            ('SomeOthertxtr Mask', 'T_Zombie_SomeOthertxtr_Mask'),
            ('Txtr_SomeOthertxtr Mask', 'T_Zombie_SomeOthertxtr_Mask'),
            ('Txt_SomeOthertxtr Mask', 'T_Zombie_SomeOthertxtr_Mask'),
            ('T_Zombie_Shoe_Mask', 'T_Zombie_Shoe_Mask'),
            ('T_Zombie Shoe2 Mask', 'T_Zombie_Shoe2_Mask'),
            ('T_ZombieShoe Opacity', 'T_Zombie_Shoe_Opacity'),
            ('mremireh_body__diffuse', 'T_Zombie_mremireh_body_Diffuse')
        ]
        for case in cases:
            self.assertEqual(uu.format_texture_name('Zombie', case[0]), case[1])
        


