# Importing the unittest package
import unittest
# Importing the module to be tested
from tamilrulepy.mozhimarabu import  word_starting


# சோதனை செய்ய பயன்படுத்தப்பட்ட சொற்ககளுக்கான மூல தொடுப்பு 
# https://www.tamilvu.org/courses/degree/c021/c0211/html/c0211502.htm

# Test case definition

class TestWordStarting(unittest.TestCase):

    def test_uyirezhuthu_check(self):
        data_list = ['அன்பு','அறிவு','அகந்தை','வலை']
        expected = [True,True,True,None]
        res = map(word_starting.uyirezhuthu_check,data_list)
        actual = list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_ka_check(self):
        data_list = ['அறிவு','கல்வி','காண்','கிளி','கீறு','குறிப்பு','கூகை','கெஞ்சு','கேள்வி','கை','கொப்பறை','கோவில்','கௌரி']
        expected = [None,True,True,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_ka_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_sa_check(self):
        data_list = [
            "அறிவு",
            "ச",
            "சாப்பிடு",
            "சி",
            "சீ",
            "சு",
            "சூ",
            "செ",
            "சே",
            "சொ",
            "சோ"]
        expected = [None,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_sa_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_nga_check(self):
        data_list = ["ஞமலி","ஞாலம்", "ஞெகிழி", "ஞொள்குதல்"]
        expected = [None,True,True,True]
        res = map(word_starting.uyirmei_nga_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_ta_check(self):
        data_list = ["ஸிர்","கண்ணன்","தரை","தாமரை","திசை","தீர்ப்பு","துடிப்பு","தூண்","தென்னைமரம்","தேன்","தொழில்","தோட்டம்","தௌவை"]
        expected = [None,None,True,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_ta_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_na_check(self):
        data_list = ["ஜூம்பா","கதிரவன்","நன்றி","நாடு","நிறம்","நீர்","நுங்கு","நூல்","நெல்","நேற்று","நையாண்டி","நொடி","நோக்கம்","நௌவி"]
        expected = [None,None,True,True,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_na_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_pa_check(self):
        data_list = ["குறிச்சி","ஜோ","பல்","பால்","பிடி","பீலி","புகழ்","பூங்கா","பெட்டி","பேச்சு","பை","பொன்","போட்டி","பௌத்தர்"]
        expected = [None,None,True,True,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_pa_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_ma_check(self):
        data_list = ["குறிச்சி","ஜோ","மண்","மான்","மின்னல்","மீன்","முரசு","மூங்கில்","மெய்","மேடு","மை","மொழி","மோதிரம்","மௌனம்"]
        expected = [None,None,True,True,True,True,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_ma_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_ya_check(self):
        data_list = ["குறிச்சி","ஜோ","யானை","யாழ்"]
        expected = [None,None,True,True]
        res = map(word_starting.uyirmei_ya_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)

    def test_uyirmei_va_check(self):
        data_list =  ["குறிச்சி","ஜோ","வணக்கம்", "வால்", "வில்", "வீடு", "வெற்றி", "வேல்", "வைகை", "வௌவால்"]
        expected = [None,None,True,True,True,True,True,True,True,True]
        res = map(word_starting.uyirmei_va_check,data_list)
        actual =list(res)
        self.assertEqual(expected,actual)
    



