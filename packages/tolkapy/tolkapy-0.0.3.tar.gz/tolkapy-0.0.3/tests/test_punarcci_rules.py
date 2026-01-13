import unittest
from tamilrulepy.euphonic import get 
from tamilrulepy.euphonic.stackwords import Maintainer



def words_data(words_list):
    return Maintainer(words_list,lang='ta')



class Test_Punarcci(unittest.TestCase):

    def test_punarcci_rule_1(self):
        
        # true case 
        
        sample1 = get( ["ஆ","இன்","ஐ"] ) 
        self.assertIn( ['ஆவினை'] , sample1)
        self.assertIn( ['ஆனை'] , sample1)

        sample2 = get( ["தா","இன்","ஐ"] ) 
        self.assertIn( ['தாவினை'], sample2)
        self.assertIn( ['தானை'] , sample2)

        sample3 = get([ 'விழா',"இன்",'சிறப்பு' ]) 
        self.assertIn( ['விழாவின்சிறப்பு'] , sample3)
        self.assertIn( ['விழான்சிறப்பு'] , sample3)
        
        sample4 = get( ["கலா","இன்","கலை"] ) 
        self.assertIn( ['கலாவின்கலை'] , sample4)
        self.assertIn( ['கலான்கலை'] , sample4)

        sample5 = get( ["நிலா","இன்","ஒளி"] ) 
        self.assertIn( ['நிலாவினொளி'] , sample5)
        self.assertIn( ['நிலானொளி'] , sample5)

        sample6 = get([ 'பலா',"இன்",'கனி' ]) 
        self.assertIn( ['பலாவின்கனி'] , sample6)
        self.assertIn( ['பலான்கனி'] , sample6)
        
        sample7 = get( ["மா","இன்","தலை"] ) 
        self.assertIn( ['மாவின்தலை'] , sample7)
        self.assertIn( ['மான்தலை'] , sample7)

        sample8 = get([ 'ஆ',"இன்",'பால்' ]) 
        self.assertIn( ['ஆவின்பால்'], sample8)
        self.assertIn( ['ஆன்பால்'] , sample8)



    def test_punarcci_rule_2(self):
        
        sample1 = get(  ["பத்து","இன்","உழக்கு"] ) 
        self.assertIn(['பதிற்றுழக்கு'],sample1) 

        sample2 = get(  ["பத்து","இன்","அகழ்"] ) 
        self.assertIn(['பதிற்றகழ்'],sample2) 

        sample3 = get( [ 'பத்து',"இன்",'ஆலாக்கு' ]) 
        self.assertIn(['பதிற்றாலாக்கு'],sample3) 

        sample4 = get(  ["பத்து","இன்","அங்குலம்"] ) 
        self.assertIn(['பதிற்றங்குலம்'],sample4) 

        # type 2

        sample11 = get(  ["பத்து","இன்","ஏழு"] ) 
        self.assertIn(['பதிற்றேழு'],sample11) 

        sample12 = get(  ["பத்து","இன்","ஒன்று"] ) 
        self.assertIn(['பதிற்றொன்று'],sample12) 

        sample13 = get( [ 'பத்து',"இன்",'ஒன்பது' ]) 
        self.assertIn(['பதிற்றொன்பது'],sample13) 





    def test_punarcci_rule_3(self):
        sample0 = get(["அவை","வற்று","ஐ"])
        self.assertIn(['அவையற்றை'],sample0) 
        
        sample1 = get(  ["அவை","வற்று","கு"] ) 
        self.assertIn(['அவையற்றுக்கு'],sample1) 

        sample2 = get(  ["இவை","வற்று","ஐ"] ) 
        self.assertIn(['இவையற்றை'],sample2) 

        sample3 = get( [ 'அவை',"வற்று",'ஆல்' ]) 
        self.assertIn(['அவையற்றால்'],sample3) 
        
        sample4 = get(["அவை","வற்று","இன்"])
        self.assertIn(['அவையற்றின்'],sample4) 
        
        # TODO
        #sample2 = get(  ["இவை","வற்று","கண்"] ) 
        #self.assertIn(['அவையற்றின்'],sample2) 

        #sample3 = get( [ 'அவை',"வற்று",'கண்' ]) 
        #self.assertIn(['பதிற்றாலாக்கு'],sample3) 

        sample10 = get(  ["இவை","வற்று","இன்"] ) 
        self.assertIn(['இவையற்றின்'],sample10) 

        sample11 = get(  ["உ","வற்று","ஐ"] ) 
        self.assertIn(['உவற்றை'],sample11) 

        sample12 = get(  ["இ","வற்று","ஐ"] ) 
        self.assertIn(['இவற்றை'],sample12) 

        sample13 = get( [ 'அ',"வற்று",'ஐ' ]) 
        self.assertIn(['அவற்றை'],sample13) 
        
        
    def test_punarcci_rule_4(self):
        
        sample0 = get([ "விள","இன்","கு" ])
        self.assertIn(['விளவிற்கு'],sample0) 
        
        sample1 = get(["அவன்","இன்","கு"]) 
        self.assertIn(['அவனிற்கு'],sample1) 

        sample2 = get(["அவள்","இன்","கு"]) 
        self.assertIn(['அவளிற்கு'],sample2) 

        sample3 = get([ 'மகம்',"இன்",'கு' ]) 
        self.assertIn(['மகவிற்கு'],sample3) 
        
        sample4 = get(["கதவு","இன்","கு"])
        self.assertIn(['கதவிற்கு'],sample4) 
        



    def test_punarcci_rule_5(self):
        
        sample0 = get(['பரணி','ஆன்','கொண்டான்'])
        self.assertIn(['பரணியாற்கொண்டான்'],sample0) 
        
        sample1 = get(['தடத்தின்','ஆன்','கொண்டான்']) 
        self.assertIn(['தடத்தினாற்கொண்டான்'],sample1) 

        sample2 = get(['தரனி','ஆன்','கொண்டான்']) 
        self.assertIn(['தரனியாற்கொண்டான்'],sample2) 

        sample3 = get(['ஊரனி','ஆன்','கொண்டான்']) 
        self.assertIn(['ஊரனியாற்கொண்டான்'],sample3) 
        
        sample4 = get(['அதன்','ஆன்','கொண்டான்'])
        self.assertIn(['அதனாற்கொண்டான்'],sample4) 
        

    def test_punarcci_rule_6(self):
    
        #TODO
        result = get(["மரம்","அத்து","ஐ"])
        #self.assertIn(['மரத்தை'],result) 

        sample1 = get( [ 'மடம்','அத்து','கை' ]  ) 
        self.assertIn( ['மடத்துக்கை'] ,sample1) 

        sample2 = get(['மரம்','அத்து','கேணி' ] ) 
        self.assertIn(['மரத்துக்கேணி'],sample2) 

        sample3 = get( ['மரம்','அத்து','கை'] ) 
        self.assertIn(['மரத்துக்கை'],sample3) 
        
        sample4 = get( ['மரம்','அத்து','கிளை'] )
        self.assertIn(['மரத்துக்கிளை'],sample4) 
   


    def test_punarcci_rule_7(self):

        sample0 = get([ 'ஆடி','இக்கு','கொண்டான்'])
        self.assertIn(['ஆடிக்குக்கொண்டான்'],sample0) 
        
        sample1 = get([ 'சித்திரை','இக்கு','கொண்டான்']) 
        self.assertIn( ['சித்திரைக்குக்கொண்டான்'] ,sample1) 

        sample2 = get(['ஆடி','இக்கு','கொண்டான்' ] ) 
        self.assertIn(['ஆடிக்குக்கொண்டான்'],sample2) 

        sample3 = get( ['ஆடி','இக்கு','தந்தான்'] ) 
        self.assertIn(['ஆடிக்குதந்தான்'],sample3) 
        
        sample4 = get( ['ஆடி','இக்கு','போயினான்'] )
        self.assertIn(['ஆடிக்குப்போயினான்'],sample4) 
           
        sample5 = get([ 'சித்திரை','இக்கு','சன்றான்']) 
        self.assertIn( ['சித்திரைக்குச்சன்றான்'] ,sample5) 



    def test_punarcci_rule_8(self):
        result = get([ 'சித்திரை','இக்கு','கொண்டான்'])
        self.assertIn(['சித்திரைக்குக்கொண்டான்'],result)   


    def test_punarcci_rule_9(self):
        result = get([ 'குன்று','அக்கு','குடி'  ])
        self.assertIn(['குன்றக்குடி'],result) 

    def test_punarcci_rule_10(self):                    
        result = get([ 'புளி','அம்','கிளை' ])
        self.assertIn(['புளியங்கிளை'],result) 
            
    
    def test_punarcci_rule_11(self):
       
        sample0 = get(['புளி','அம்','நுனி'])
        self.assertIn(['புளியநுனி'],sample0) 
        
        sample1 = get( ['புளி','அம்','தலை']  ) 
        self.assertIn( ['புளியந்தலை'] ,sample1) 

        sample2 = get(['புளி','அம்','கோது' ] ) 
        self.assertIn(['புளியங்கோது'],sample2) 

        sample3 = get( ['புளி','அம்','செதில்'] ) 
        self.assertIn(['புளியஞ்செதில்'],sample3) 
        
        sample4 = get( ['புளி','அம்','தோல்'] )
        self.assertIn(['புளியந்தோல்'],sample4) 
        
        sample5 = get( ['புளி','அம்','பட்டை'] )
        self.assertIn(['புளியப்பட்டை'],sample5) 
   


    def test_punarcci_rule_12(self):
        
        sample0 = get([ 'வீடு','இன்','தென்புறம்' ])
        self.assertIn(['வீட்டின்தென்புறம்'],sample0) 
        
        sample1 = get( [ 'மடம்','அத்து','கை' ]  ) 
        self.assertIn( ['மடத்துக்கை'] ,sample1) 

        sample2 = get(['மரம்','அத்து','கேணி' ] ) 
        self.assertIn(['மரத்துக்கேணி'],sample2) 

        sample3 = get( ['மரம்','அத்து','கை'] ) 
        self.assertIn(['மரத்துக்கை'],sample3) 
        
        sample4 = get( ['மரம்','அத்து','கிளை'] )
        self.assertIn(['மரத்துக்கிளை'],sample4) 
   

    def test_punarcci_rule_13(self):
      
        sample0 = get( [ 'மடம்','அத்து','கேணி' ] )
        self.assertIn(['மடத்துக்கேணி'],sample0) 
        
        sample1 = get( [ 'மடம்','அத்து','கை' ]  ) 
        self.assertIn( ['மடத்துக்கை'] ,sample1) 

        sample2 = get(['மரம்','அத்து','கேணி' ] ) 
        self.assertIn(['மரத்துக்கேணி'],sample2) 

        sample3 = get( ['மரம்','அத்து','கை'] ) 
        self.assertIn(['மரத்துக்கை'],sample3) 
        
        sample4 = get( ['மரம்','அத்து','கிளை'] )
        self.assertIn(['மரத்துக்கிளை'],sample4) 

    def test_punarcci_rule_14_to_16(self):
        result = get([ 'பு' ])
        self.assertIn(['புகாரம்'],result) 
        self.assertIn(['புகரம்'],result) 
        self.assertIn(['புஃகான்'],result) 
        
        result = get([ 'சு' ])
        self.assertIn(['சுகாரம்'],result) 
        self.assertIn(['சுகரம்'],result) 
        self.assertIn(['சுஃகான்'],result) 

        result = get([ 'ஐ' ])
        self.assertIn(['ஐகாரம்'],result) 
        self.assertIn(['ஐகான்'],result) 

        result = get([ 'ஔ' ])
        self.assertIn(['ஔகாரம்'],result) 
        self.assertIn(['ஔகான்'],result) 

    def test_punarcci_rule_17(self):
        result = get(['கடல்','அலை'])
        self.assertIn(['கடலலை'],result) 
    
    def test_punarcci_rule_18(self):
        result = get([ 'ஆவ்','இலை' ])
        self.assertIn(['ஆவிலை'],result) 

