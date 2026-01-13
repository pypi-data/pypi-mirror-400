import unittest
from tamilrulepy.mozhimarabu import word_ending

 
class TestWordEnding(unittest.TestCase):
    def test_uyir_check(self):
        data_list = [
            'ஆன',
            'புறா',
            'மணி',
            ' ஈ',
            'எறும்பு',
            'செரூ',
            'மழையே',
            'சந்தை',
            'அணல்பொ',
            'கப்பலோ',
            "வெள்ளோஔ",
            # false case
            'செவ்',
            'பாழ்',
        ]
        expected = [
        True,True,True,True,True,
        True,True,True,True,True,
        True, False,False ]
        res = map(word_ending.uyir_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)


    def test_mellinam_check(self):
        data_list = [
            'கணஞ்',
            'மண்',
            'மனந்',
            'மரம்',
            'மாணவன்',
            # false case
            'அணல்',
            'மயில்',
        ]
        expected = [
        True,True,True,True,True,
        False,False
            ]
        res = map(word_ending.mellinam_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)


    def test_idaiyinam_check(self):
        data_list = [
            'வாய்',
            'நடுவர்',
            'கடல்',
            'செவ்',
            'பாழ்',
            'நிழள்',
            # false case
            'மரம்',
            'கணம்',
        ]
        expected = [
        True,True,True,True,True,
        True,False,False
            ]
        res = map(word_ending.idaiyinam_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)

    def test_oorezhuthoorumozhi_check(self):
        data_list =  [
            "ஆ",
            "ஈ",
            "ஊ",
            "ஏ",
            "ஐ",
            "ஓ",
            # false case
            'செவ்',
            'பாழ்',
        ]
        expected = [
        True,True,True,True,True,True,False,False
            ]
        res = map(word_ending.oorezhuthoorumozhi_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)


    def test_alapedai_check(self):
        data_list =  [
            "அ",
            "இ",
            "உ",
            "எ",
            "ஒ",
            # false case
            "ஆ",
            "ஈ", 
        ]
        expected = [
        True,True,True,True,True,False,False
            ]
        res = map(word_ending.alapedai_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)


    def test_suttu_check(self):
        data_list =  [
            "அப்பையன்",
            "இவ்வீடு",
            "இக்காட்சி",
            # false case
            "அவை",
            "அது",
            "அம்மலை",
            "இந்நறுமணம்"
        ]
        expected = [
        True,True,True,False,False,False,False
            ]
        res = map(word_ending.suttu_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)

    def test_vinaa_check(self):
        data_list =  [
            "எங்கே",
            "எப்படி",
            "எவ்வாறு",
            # false case
            "என்ன",
            "ஏன்",
            "எதற்கு",
            "இந்நறுமணம்"
        ]
        expected = [
        True,True,True,
        False,False,False,False
            ]
        res = map(word_ending.vinaa_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)


 