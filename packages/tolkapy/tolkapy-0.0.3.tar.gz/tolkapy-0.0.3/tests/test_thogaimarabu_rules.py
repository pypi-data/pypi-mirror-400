import unittest
from tamilrulepy.euphonic import get
from tamilrulepy.thogaimarabu.thogaimarabu import thogai_6, thogai_7, thogai_8
from tamilrulepy.thogaimarabu.thogaimarabu import (
    thogai_1,
    thogai_2,
    thogai_3,
    thogai_4,
    thogai_5,
)


class Test_thogaimarabu(unittest.TestCase):

    def test_thogai_rule_1(self):
        result = get(["தட", "தோள்"])
        self.assertIn(["தடந்தோள்"], result)
        result = get(["கருமை", "சூழ்"])
        self.assertIn(["கருஞ்சூழ்"], result)

    def test_thogai_rule_2(self):
        result = get(["முருகன்", "மலை"])
        self.assertIn(["முருகன்மலை"], result)
        # result = get( ["அறம்","யாது"])
        # self.assertIn(['கருஞ்சூழ்'],result)
        result = get(["தமிழ்", "வாளர்கிறது"])
        self.assertIn(["தமிழ்வாளர்கிறது"], result)

    def test_thogai_1(self):
        output = thogai_1("தட", "தோள்")
        self.assertEqual("தடந்தோள்", output)
        # output2 = thogai_1("கருமை", "சூழ்")
        # self.assertEqual("கருஞ்சூழ்", output2) TODO: Need to check with professor. He removed mai at first word last
        output3 = thogai_1("உயிர்மெய்", "எழுத்துகள்")
        self.assertIsNone(output3)
        output4 = thogai_1("கருப்பு", "எருமை")
        self.assertIsNone(output4)

    def test_thogai_2(self):
        output = thogai_2("முருகன்", "மலை")
        self.assertEqual("முருகன் மலை", output)
        output2 = thogai_2("அறம்", "யாது")
        self.assertEqual("அறம் யாது", output2)
        output3 = thogai_2("அறம்", "சிலை")
        self.assertIsNone(output3)
        with self.assertRaises(ValueError):
            thogai_2("அறம்ஃ", "யாது")

    def test_thogai_3(self):
        output = thogai_3("மெய்", "ஞானம்")
        self.assertEqual("மெய்ஞ்ஞானம்", output)
        output2 = thogai_3("கை", "நொடி")
        self.assertEqual("கைந்நொடி", output2)
        with self.assertRaises(ValueError):
            thogai_3("அறம்ஃ", "யாது")
        output3 = thogai_3("கை", "சிலை")
        self.assertIsNone(output3)

    def test_thogai_4(self):
        output = thogai_4("மண்", "யாத்த")
        self.assertEqual("மண்ஞாத்த", output)
        output2 = thogai_4("பொன்", "யாத்த")
        self.assertEqual("பொன்ஞாத்த", output2)
        output3 = thogai_4("கை", "நொடி")
        self.assertIsNone(output3)
        output4 = thogai_4("மண்", "ஆத்த")
        self.assertIsNone(output4)

    def test_thogai_5(self):
        output = thogai_5("மண்", "வலிது")
        self.assertEqual("மண்வலிது", output)
        output2 = thogai_5("பொன்", "கடிது")
        self.assertEqual("பொன்கடிது", output2)
        with self.assertRaises(ValueError):
            thogai_5("அறம்", "ஃயாது")
        output3 = thogai_5("கை", "நொடி")
        self.assertIsNone(output3)

    # def test_thogai_rule_3(self):
    # result = get(["கை","நொடி"])
    # self.assertIn(['தடந்தோள்'], result)
    # result = get(["மேய்","ஞானம்"])
    # self.assertIn(['தடந்தோள்'], result)

    def test_thogai_rule_4(self):
        result = get(["மண்", "யாத்த"])
        self.assertIn(["மண்ஞாத்த"], result)
        result = get(["பொன்", "யாத்த"])
        self.assertIn(["பொன்ஞாத்த"], result)

    def test_thogai_rule_5(self):
        result = get(["மண்", "கடிது"])
        # self.assertIn(["மண்கடிது"], result)
        result = get(["மண்", "வலிது"])
        self.assertIn(["மண்வலிது"], result)
        result = get(["பொன்", "கடிது"])
        # self.assertIn(["பொன்கடிது"], result)
        result = get(["பொன்", "வலிது"])
        self.assertIn(["பொன்வலிது"], result)

    # unittest for functions written by hariharan U -- starts 
    def test_thogai_rule_6(self):

        word_list = [
            ("பொன்","குடம்","பொற்குடம்"),
            ("மண்","துனை","மட்துனை"),
            ("மண்","ஞாலம்","மண்ஞாலம்"),
            ("பொன்","விலை","பொன்விலை"),
            ("பொன்","சிலை","பொற்சிலை"),
            ("மண்","பாண்டம்","மட்பாண்டம்"),
            ("வின்","அரசன்","வின்அரசன்"),
            ("தன்","பெறுமை","தற்பெறுமை")
            ]
        
        for first_word,second_word,result in word_list:
            self.assertIn(thogai_6(first_word,second_word),result)
        
    def test_thogai_rule_7(self):
        word_list = [
            ("பொன்","தாலி","பொற்றாலி"),
            ("கல்","தரை","கற்றரை"),
            ("தன்","நிலை","தன்னிலை"),
            ("கல்","தவளை","கற்றவளை"),
            ("பொன்","திரை","பொற்றிரை"),
            ("தன்","தரப்பு","தற்றரப்பு"),
            ("சிலம்பன்","தை","சிலம்பற்றை")
            ]
        for first_word,second_word,result in word_list:
                self.assertIn(thogai_7(first_word,second_word),result)
        
    def test_thogai_rule_8(self):
        #boobalan's testcases for euphonic 
        """ result =  get(["மண்","தீது"])  #bug
        self.assertIn(["மட்டீது"], result) 
        result =  get(["மண்","நன்று"]) 
        self.assertIn(["மண்ணன்று"], result) 
        result =  get(["மண்","நினைவு"])
        self.assertIn(["மண்ணினைவு"], result)

        result =  get(["கள்","தீது"]) 
        self.assertIn(["கட்டது"], result) 
        result =  get(["கள்","நன்று"]) 
        self.assertIn(["கண்ணின்று"], result) 
        result =  get(["கள்","நினைவு"])
        self.assertIn(["கண்ணினைவு"], result)

        result =  get(["உள்","தீது"]) 
        self.assertIn(["உட்டீது"], result) 
        result =  get(["உள்","நன்று"]) 
        self.assertIn(["உண்ணன்று"], result) 
        result =  get(["உள்","நினைவு"])
        self.assertIn(["உண்ணினைவு"], result) """
        # thogaimarabu individual function testcases
        word_list = [
            ("மண்","தீது","மட்டீது"),
            ("மண்","நன்று","மண்ணன்று"),
            ("கள்","தீது","கட்டீது"),
            ("உள்","நினைவு","உண்ணினைவு"),
            ("ஊண்","தின்று","ஊட்டின்று")
        ]
        for first_word,second_word,result in word_list: 
            self.assertIn(thogai_8(first_word,second_word),result)


"""
    def test_thogai_rule_17(self):
        result = get("அதோனி","கொண்டான்")
        self.assertIn("அதோனிக்கொண்டான்")
        result = get("இதோனி","கொண்டான்")
        self.assertIn("இதோனிக்கொண்டான்")
        result = get("உதோனி","கொண்டான்")
        self.assertIn("உதோனிக்கொண்டான்")
        result = get("எதோனி","கொண்டான்")
        self.assertIn("எதோனிக்கொண்டான்")
        result = get("ஆண்டை","கொண்டான்")
        self.assertIn("ஆண்டைக்கொண்டான்")
        result = get("யாண்டை","கொண்டான்")
        self.assertIn("யாண்டைக்கொண்டான்")
    
    def test_thogai_rule_19(self):
        result =  get(["தாம்","கு"]) 
        self.assertIn(["தமக்கு"], result) 
        result =  get(["நாம்","கு"]) 
        self.assertIn(["நமக்கு"], result) 
        result =  get(["யான்","கு"]) 
        self.assertIn(["எனக்கு"], result) 

        result =  get(["தாம்","அது"]) 
        self.assertIn(["தமது"], result) 
        result =  get(["நாம்","அது"]) 
        self.assertIn(["நமது"], result) 
        result =  get(["யான்","அது"]) 
        self.assertIn(["எனது"], result) 
   
    def test_thogai_rule_20(self):
        result =  get(["நும்","கு"]) 
        self.assertIn(["நுமக்கு"], result) 
        result =  get(["நும்","அது"]) 
        self.assertIn(["நுமது"], result) 
    
    def test_thogai_rule_21(self):
        result =  get(["உரிஞு","யாது"]) 
        self.assertIn(["உரிஞ்யாது"], result) 
        result =  get(["பொருநு","யாது"]) 
        self.assertIn(["பொருந்யாது"], result) 
        result =  get(["உரிஞு","அழகா"]) 
        self.assertIn(["உரிஞ்அழகா"], result) 
        result =  get(["பொருநு","அழகா"]) 
        self.assertIn(["பொருந்அழகா"], result) 

    def test_thogai_rule_21(self):
        pass

    def test_thogai_rule_23(self):
        result =  get(["ஒன்று","அரை"]) 
        self.assertIn(["ஒன்றரை"], result) 
        result =  get(["ஏழு","அரை"]) 
        self.assertIn(["ஏழரை"], result) 


    def test_thogai_rule_24(self):
        result =  get(["உரி","குறை"]) 
        self.assertIn(["உரிக்குறை"], result) 
        result =  get(["காணி","குறை"]) 
        self.assertIn(["காணிக்குறை"], result) 


    def test_thogai_rule_25(self):
        result =  get(["உழக்கு","குறை"]) 
        self.assertIn(["உழக்கின்குறை"], result) 
        result =  get(["ஒன்று","குறை"]) 
        self.assertIn(["ஒன்றின்குறை"], result) 

    def test_thogai_rule_26(self):
        result =  get(["கலம்","குறை"]) 
        self.assertIn(["கலத்துக்குறை"], result) 
      
    def test_thogai_rule_27(self):
        result =  get(["பனை","குறை"]) 
        #self.assertIn(["பனையின்குறை"], result)  # பனைவின்குறை
        result =  get(["கா","குறை"]) 
        self.assertIn(["காவின்குறை"], result) 

"""
        
