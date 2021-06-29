import unittest
import galore



class test_check_imports(unittest.TestCase):
    "We use this to test whether the following functions and packages were imported into galore or not "

    def test_check_get_cross_sections(self):

        try:
            from galore import get_cross_section
        except ImportError as e:
            self.assertEqual(e, None)
    
    def test_check_cross_sections_info(self):

        try:
            from galore import cross_sections_info
        except ImportError as e:
            self.assertEqual(e, None)
    
    def test_check_sqrt(self):
        
        try:
            from galore import sqrt
        except ImportError as e:
            self.assertEqual(e, None)

    def test_check_log(self):
        
        try:
            from galore import log
        except ImportError as e:
            self.assertEqual(e, None)    

    
    def test_check_OrderedDict(self):

        try:
            from galore import OrderedDict
        except ImportError as e:
            self.assertEqual(e, None)   


    def test_check_Sequence(self):
        
        try:
            from galore import Sequence
        except ImportError as e:
            self.assertEqual(e, None)   

    
    def test_check_logging(self):
        
        try:
            from galore import logging
        except ImportError as e:
            self.assertEqual(e, None)   

    def test_check_print_function(self):
        
        try:
            from galore import print_function
        except ImportError as e:
            self.assertEqual(e, None)   


    def test_check_interp1d(self):

        try:
            from galore import interp1d
        except ImportError as e:
            self.assertEqual(e, None)   



    def test_check_numpy(self):

        try:
            from galore import np
        except ImportError as e:
            self.assertEqual(e, None)   

    
    def test_check_os_path(self):

        try:
            from galore import os
        except ImportError as e:
            self.assertEqual(e, None)   
  
        


if __name__ == '__main__':
    unittest.main()


    