import unittest
from tamilrulepy.euphonic.previous import remove_ending_consonent_m 
from tamilrulepy.euphonic.stackwords import Maintainer


def words_data(words_list):
    return Maintainer(words_list,lang='ta')



class Test_Euphonic_commin(unittest.TestCase):


    def test_remove_ending_consonent_m(self):
        # true case 
        case1 = remove_ending_consonent_m( words_data(["மரம்","அத்து","ஐ"]) )
        self.assertTrue(case1[0])

        case2 = remove_ending_consonent_m( words_data(["மகம்","அத்து","கிளை"]) )
        self.assertTrue(case2[0])

        case3 = remove_ending_consonent_m( words_data([ 'மடம்','அத்து','கேணி' ]) )
        self.assertTrue(case3[0])
        
        case4 = remove_ending_consonent_m( words_data([ 'பவளம்','இதல்', ]) )
        self.assertTrue(case4[0])
  
        case4 = remove_ending_consonent_m( words_data([ 'குளம்','கரை', ]) )
        self.assertTrue(case4[0])
  

        # false case

        case10 = remove_ending_consonent_m( words_data([ 'குன்று','அக்கு','குடி' ]) )
        self.assertFalse(case10[0])
  
        case11 = remove_ending_consonent_m( words_data([ 'மா','மரம்' ]) )
        self.assertFalse(case11[0])
  


