import unittest
from tamilrulepy.euphonic.common import  add_joining_consonents, make_double_required_ending_consonents, remove_ending_consonent_u,joining_consonents_with_vowel
from tamilrulepy.euphonic.stackwords import Maintainer


def words_data(words_list):
    return Maintainer(words_list,lang='ta')



class Test_Euphonic_commin(unittest.TestCase):


    def test_add_joining_consonents(self):
        # true case
       
        case1 = add_joining_consonents( words_data(["ஆ","இன்","ஐ"]) )
        self.assertTrue(case1[0])
  
        case2 = add_joining_consonents( words_data([ "மணி" , "அடித்தான்" ]) )
        self.assertTrue(case2[0])
   
        case3 = add_joining_consonents( words_data(["பூ" , "அரும்பு"]) )
        self.assertTrue(case3[0])
  
        case4 = add_joining_consonents( words_data([ "பூ" , "இதழ்" ]) )
        self.assertTrue(case4[0])
 

        # false case


        case11 = add_joining_consonents( words_data(["அவை","வற்று","ஐ"]) )
        self.assertFalse(case11[0])
  
        case12 = add_joining_consonents( words_data([ "பல்" , "இல்லை"  ]) )
        self.assertFalse(case12[0])
   
        case13 = add_joining_consonents( words_data([ "நட்" , "இரவில்" ]) )
        self.assertFalse(case13[0])
  
        case14 = add_joining_consonents( words_data([ "கண்" , "அழகிய" ]) )
        self.assertFalse(case14[0])
        
        case15 = add_joining_consonents( words_data([ 'மரம்' , 'அழகு' ]) )
        self.assertFalse(case15[0])
 

    def test_make_double_required_ending_consonents(self):
        # true case
      
        case1 = make_double_required_ending_consonents( words_data([ 'வீட்','இன்','தென்புறம்' ]) )
        self.assertTrue(case1[0])
  
        case2 = make_double_required_ending_consonents( words_data([ "வெற்" , "இலை" ]) )
        self.assertTrue(case2[0])
   
        case3 = make_double_required_ending_consonents( words_data([ 'நாட்' , 'அரசன்' ]) )
        self.assertTrue(case3[0])
        
        # TODO
        #case4 = make_double_required_ending_consonents( words_data([ 'சோற்' , 'பானை' ]) )
        #self.assertTrue(case4[0])
 

        # false case
        
        case10 = make_double_required_ending_consonents( words_data([ "வெற்ற்" + "இலை" ]) )
        self.assertFalse(case10[0])

        case11 = make_double_required_ending_consonents( words_data([ "மாடு" , "வால்" ]) )
        self.assertFalse(case11[0])
        
        case12 = make_double_required_ending_consonents( words_data([ "ஆ","இன்","ஐ" ]) )
        self.assertFalse(case12[0])
   

    def test_remove_ending_consonent_u(self):
        # true case
     
        case1 = remove_ending_consonent_u( words_data([ 'குன்று','அக்கு','குடி' ]) )
        self.assertTrue(case1[0])
  
        case2 = remove_ending_consonent_u( words_data([ "காடு" , "ஆறு" ]) )
        self.assertTrue(case2[0])
        
        # TODO
        #case3 = remove_ending_consonent_u( words_data(["நாடு" , "யாது"]) )
        #self.assertTrue(case3[0])
        
        case4 = remove_ending_consonent_u( words_data([ "வரகு" , "அடி" ]) )
        self.assertTrue(case4[0])

        case5 = remove_ending_consonent_u( words_data([ "துப்பு" , "அழகு" ]) )
        self.assertTrue(case5[0])
 
        case6 = remove_ending_consonent_u( words_data([ "பட்டு" , "ஆடை" ]) )
        self.assertTrue(case6[0])
  

        # false case
        
        case10 = remove_ending_consonent_u( words_data([ "கு","இன்","ஐ" ]) )
        self.assertFalse(case10[0])

        case11 = remove_ending_consonent_u( words_data([ 'புளி','அம்','நுனி' ]) )
        self.assertFalse(case11[0])
        
        case12 = remove_ending_consonent_u( words_data([ "ஆ","இன்","ஐ" ]) )
        self.assertFalse(case12[0])
   



    #TODO
    #def test_joining_consonents_with_vowel(self):
    #    pass







