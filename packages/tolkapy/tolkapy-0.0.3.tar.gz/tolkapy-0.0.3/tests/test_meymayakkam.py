import unittest
from tamilrulepy.meymayakkam import meymayakkam1, meymayakkam2, meymayakkam3, meymayakkam4, meymayakkam5, meymayakkam6, meymayakkam7, meymayakkam8, meymayakkam9, meymayakkam10, meymayakkam11, meymayakkam12, meymayakkam13, meymayakkam14, meymayakkam15, meymayakkam16, meymayakkam17, meymayakkam18


class TestMeymayakkam(unittest.TestCase):
    
    def test_meymayakkam1(self):
        # correct words
        self.assertTrue(meymayakkam1("மயக்கம்"))
        self.assertTrue(meymayakkam1("மெய்மயக்கம்"))
        # Detecting incorrect words
        self.assertFalse(meymayakkam1("மயக்க்கம்"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam1("தடம்"))
        self.assertIsNone(meymayakkam1("திட்டு"))

    def test_meymayakkam2(self):
        # Correct Words
        self.assertTrue(meymayakkam2("வெங்காயம்"))
        self.assertTrue(meymayakkam2("வேங்கை"))
        self.assertTrue(meymayakkam2("குரங்கு"))
        self.assertTrue(meymayakkam2("அங்குலம்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam2("வெங்ங்கயம்"))
        self.assertFalse(meymayakkam2("இனிங்சி"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam2("விளையாட்டு"))
        self.assertIsNone(meymayakkam2("மீன்கள்"))
        self.assertIsNone(meymayakkam2("சாப்பாடு"))

    def test_meymayakkam3(self):
        # Correct Words
        self.assertTrue(meymayakkam3("அச்சரம்"))
        self.assertTrue(meymayakkam3("அச்சாணி"))
        self.assertTrue(meymayakkam3("சிகிச்சை"))
        self.assertTrue(meymayakkam3("சர்ச்சை"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam3("சட்ச்ச்சி"))
        self.assertFalse(meymayakkam3("திச்டட"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam3("பூங்கா"))
        self.assertIsNone(meymayakkam3("நேரம்"))
        self.assertIsNone(meymayakkam3("நாட்கள்"))


    def test_meymayakkam4(self):
        # Correct Words
        # TODO Still for "ஞ்","ய்" didn't have any words
        self.assertTrue(meymayakkam4("இஞ்சி"))
        self.assertTrue(meymayakkam4("மஞ்சள்"))
        self.assertTrue(meymayakkam4("காஞ்சிபுரம்"))
        self.assertTrue(meymayakkam4("அஞ்சறைப்பெட்டி"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam4("அஞ்ககி"))
        self.assertFalse(meymayakkam4("மிஞ்வலி"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam4("காலை"))
        self.assertIsNone(meymayakkam4("சிறப்பு"))
        self.assertIsNone(meymayakkam4("வர்ணம்"))

    def test_meymayakkam5(self):
        # Correct Words
        self.assertTrue(meymayakkam5("வெட்கம்"))
        self.assertTrue(meymayakkam5("நுட்பம்"))
        self.assertTrue(meymayakkam5("மாட்சி"))
        self.assertTrue(meymayakkam5("முட்டாள்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam5("வெடஂதச"))
        self.assertFalse(meymayakkam5("சாடஂவா"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam5("மஞ்சள்"))
        self.assertIsNone(meymayakkam5("சிறப்பு"))
        self.assertIsNone(meymayakkam5("அச்சரம்"))

    def test_meymayakkam6(self):
        # Correct Words
        self.assertTrue(meymayakkam6("வெண்கலம் "))
        self.assertTrue(meymayakkam6("மண்சேறு"))
        self.assertTrue(meymayakkam6("வெண்ஞமலி"))
        self.assertTrue(meymayakkam6("மண்டலம் "))
        self.assertTrue(meymayakkam6("நண்பகல் "))
        self.assertTrue(meymayakkam6("வெண்மலர்"))
        self.assertTrue(meymayakkam6("மண்யாது"))
        self.assertTrue(meymayakkam6("மண்வலிது"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam6("கணஂளியே"))
        self.assertFalse(meymayakkam6("சணஂராலய"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam6("நுட்பம்"))
        self.assertIsNone(meymayakkam6("சிகிச்சை"))
        self.assertIsNone(meymayakkam6("காஞ்சிபுரம்"))

    def test_meymayakkam7(self):
        # Correct Words
        self.assertTrue(meymayakkam7("கத்தி"))
        self.assertTrue(meymayakkam7("பத்து"))
        self.assertTrue(meymayakkam7("மத்தளம்"))
        self.assertTrue(meymayakkam7("வித்தகன்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam7("சத்நியாச"))
        self.assertFalse(meymayakkam7("பத்சலம்"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam7("நண்பகல் "))
        self.assertIsNone(meymayakkam7("அச்சரம்"))
        self.assertIsNone(meymayakkam7("நண்பகல் "))

    def test_meymayakkam8(self):
        # Correct Words
        self.assertTrue(meymayakkam8("வெந்நீர் "))
        self.assertTrue(meymayakkam8("செந்நீர்"))
        self.assertTrue(meymayakkam8("வந்தான்"))
        self.assertTrue(meymayakkam8("வெரிந்யாது"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam8("தந்ராலயா"))
        self.assertFalse(meymayakkam8("சிந்ஙாண"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam8("மதஂதமஂ"))
        self.assertIsNone(meymayakkam8("சர்ச்சை"))
        self.assertIsNone(meymayakkam8("தடம்"))

    def test_meymayakkam9(self):
        # Correct Words
        self.assertTrue(meymayakkam9("கப்பல் "))
        self.assertTrue(meymayakkam9("குப்பை"))
        self.assertTrue(meymayakkam9("சிப்பம்"))
        self.assertTrue(meymayakkam9("கப்பம்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam9("யாப்தய"))
        self.assertFalse(meymayakkam9("ஞப்ழச"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam9("பத்து"))
        self.assertIsNone(meymayakkam9("வந்தான்"))
        self.assertIsNone(meymayakkam9("குரங்கு"))

    def test_meymayakkam10(self):
        # Correct Words
        self.assertTrue(meymayakkam10("அம்மை"))
        self.assertTrue(meymayakkam10("கம்பன் "))
        self.assertTrue(meymayakkam10("புலம்யாது"))
        self.assertTrue(meymayakkam10("வலம்வரும்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam10("பழம்ரச"))
        self.assertFalse(meymayakkam10("கம்ளத"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam10("செந்நீர்"))
        self.assertIsNone(meymayakkam10("மஞ்சள்"))
        self.assertIsNone(meymayakkam10("அஞ்சறைப்பெட்டி"))

    def test_meymayakkam11(self):
        # Correct Words
        self.assertTrue(meymayakkam11("பொய்கை"))
        self.assertTrue(meymayakkam11("வேய்சிறிது"))
        self.assertTrue(meymayakkam11("வேய்ஞான்ற "))
        self.assertTrue(meymayakkam11("நொய்து"))
        self.assertTrue(meymayakkam11("மெய்நீண்டது"))
        self.assertTrue(meymayakkam11("மெய்பெரிது"))
        self.assertTrue(meymayakkam11("பேய்மனம்"))
        self.assertTrue(meymayakkam11("பேய்வலிது"))
        self.assertTrue(meymayakkam11("செய்யான் "))
#        self.assertTrue(meymayakkam11("வேய்ங்குழல்")) Having doubts here need to check with professor
        # Detecting Incorrect words
        self.assertFalse(meymayakkam11("காய்டமம்"))
        self.assertFalse(meymayakkam11("வய்றம்"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam11("அம்மை"))
        self.assertIsNone(meymayakkam11("நண்பகல் "))
        self.assertIsNone(meymayakkam11("நுட்பம்"))

    def test_meymayakkam12(self):
        # Correct Words
        self.assertTrue(meymayakkam12("வேர்கடிது"))
        self.assertTrue(meymayakkam12("வேர்ஙனம்"))
        self.assertTrue(meymayakkam12("வேர்சிறிது"))
        self.assertTrue(meymayakkam12("வேர்ஞான்றது"))
        self.assertTrue(meymayakkam12("வேர்நீண்டது"))
        self.assertTrue(meymayakkam12("வேர்பெரிது"))
        self.assertTrue(meymayakkam12("வேர்மாண்டது"))
        self.assertTrue(meymayakkam12("வேர்யாது"))
        self.assertTrue(meymayakkam12("வேர்வலிது"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam12("ராமராஜ்ஜியம்"))
        self.assertFalse(meymayakkam12("சாம்ராட்"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam12("சாம்பல்"))
        self.assertIsNone(meymayakkam12("வெண்மை"))
        self.assertIsNone(meymayakkam12("பச்சை"))

    def test_meymayakkam13(self):
        # Correct Words
        self.assertTrue(meymayakkam13("வீழ்கடிது"))
        self.assertTrue(meymayakkam13("வீழ்ஙனம்"))
        self.assertTrue(meymayakkam13("வீழ்சிறிது"))
        self.assertTrue(meymayakkam13("வீழ்ஞான்றது"))
        self.assertTrue(meymayakkam13("வீழ்தீது"))
        self.assertTrue(meymayakkam13("வீழ்நீண்டது"))
        self.assertTrue(meymayakkam13("வீழ்பெரிது"))
        self.assertTrue(meymayakkam13("வீழ்மாண்டது"))
        self.assertTrue(meymayakkam13("வீழ்யானை"))
        self.assertTrue(meymayakkam13("வாழ்வோர்"))

        # Detecting Incorrect words
        self.assertFalse(meymayakkam13("சூழ்ச்சி"))
        self.assertFalse(meymayakkam13("காழ்ப்புணர்ச்சி"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam13("பட்டை"))
        self.assertIsNone(meymayakkam13("வட்டம்"))
        self.assertIsNone(meymayakkam13("சதுரம்"))
        
    def test_meymayakkam14(self):
         # Correct Words
         self.assertTrue(meymayakkam14("செவ்வானம்"))
         # Detecting Not Applicable words
         self.assertIsNone(meymayakkam14("செங்காந்தள்"))

    def test_meymayakkam15(self):
        # Correct Words
        self.assertTrue(meymayakkam15("செல்க"))
        self.assertTrue(meymayakkam15("வல்சி"))
        self.assertTrue(meymayakkam15("செல்ப"))
        self.assertTrue(meymayakkam15("கொல்யானை"))
        self.assertTrue(meymayakkam15("கோல்வளை"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam15("செல்மாண்பு"))
        self.assertFalse(meymayakkam15("கொல்தவிடு"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam15("செவ்வானம்"))

    def test_meymayakkam16(self):
        # Correct Words
        self.assertTrue(meymayakkam16("கொள்க"))
        self.assertTrue(meymayakkam16("நீள்சினை"))
        self.assertTrue(meymayakkam16("கொள்ப"))
        self.assertTrue(meymayakkam16("வெள்ளை"))
        self.assertTrue(meymayakkam16("வெள்யாறு"))
        self.assertTrue(meymayakkam16("கள்வன்"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam16(""))
        self.assertFalse(meymayakkam16(""))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam16(""))
        self.assertIsNone(meymayakkam16(""))
        self.assertIsNone(meymayakkam16(""))

    def test_meymayakkam17(self):
        # Correct Words
        self.assertTrue(meymayakkam17("கற்க"))
        self.assertTrue(meymayakkam17("முயற்சி"))
        self.assertTrue(meymayakkam17("கற்ப"))
        self.assertTrue(meymayakkam17("கற்றாழை"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam17("இதற்க்காக"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam17("கண்ணம்"))
        self.assertIsNone(meymayakkam17("கிண்ணம்"))
        self.assertIsNone(meymayakkam17("வண்ணம்"))

    def test_meymayakkam18(self):
        # Correct Words
        self.assertTrue(meymayakkam18("புன்கண்"))
        self.assertTrue(meymayakkam18("புன்செய்"))
        self.assertTrue(meymayakkam18("மென்ஞாண்"))
        self.assertTrue(meymayakkam18("அன்பு"))
        # Detecting Incorrect words
        self.assertFalse(meymayakkam18("என்தங்கை"))
        self.assertFalse(meymayakkam18("எம்புதல்வன்"))
        # Detecting Not Applicable words
        self.assertIsNone(meymayakkam18("சத்ரு"))
        self.assertIsNone(meymayakkam18("சுபாவம்"))
        self.assertIsNone(meymayakkam18("கண்மணி"))

#    def test_meymayakkam_(self):
#        # Correct Words
#        self.assertTrue(meymayakkam_(""))
#        self.assertTrue(meymayakkam_(""))
#        self.assertTrue(meymayakkam_(""))
#        self.assertTrue(meymayakkam_(""))
#        # Detecting Incorrect words
#        self.assertFalse(meymayakkam_(""))
#        self.assertFalse(meymayakkam_(""))
#        # Detecting Not Applicable words
#        self.assertIsNone(meymayakkam_(""))
#        self.assertIsNone(meymayakkam_(""))
#        self.assertIsNone(meymayakkam_(""))

