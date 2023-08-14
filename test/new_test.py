import numpy as np
import unittest
import json
import os
import platform
from os.path import join as path_join


from galore.cross_sections import get_csv_file_path
from galore.cross_sections import _cross_sections_from_csv_data

##obtain directory of current test file
test_dir = os.path.abspath(os.path.dirname(__file__))

##obtain expected directory of data-storing file of different systems
if platform.system() == "Windows":
    correct_directory = os.path.join(os.getenv('LOCALAPPDATA'), 'galore_data')
else:
    correct_directory = os.path.join(os.path.expanduser('~'), '.galore_data')


class test_get_cross_sections_from_data_table(unittest.TestCase):
    '''To check function _cross_sections_from_csv_data works well with csv datatable'''

    def test_get_cross_sections_from_scofield_datatable(self):
    ##Import datatable stored in json file and convert them to the correct form, which mocks csv datatable for element Al
        json_path = path_join(test_dir, 'Al_test_scofield.json')
        with open(json_path) as json_file:
            data = json.load(json_file)
        data['data_table'] = np.array(data['data_table'])
        data['electron_counts'] = np.array(data['electron_counts'])

    ##check the function goes well with above datatable
        cross_sections_scofield,_= _cross_sections_from_csv_data(800,data,'Scofield')
        self.assertAlmostEqual(cross_sections_scofield['s'],4.41385e-06)
    

    def test_get_cross_sections_from_yeh_datatable(self):
    
        ##Import datatable stored in json file and convert them to the correct form, which mocks csv datatable for element Al
        json_path = path_join(test_dir, 'Al_test_yeh.json')
        with open(json_path) as json_file:
            data = json.load(json_file)
        data['data_table'] = np.array(data['data_table'])
        data['electron_counts'] = np.array(data['electron_counts'])

    ##check the function goes well with above datatable
        cross_sections_scofield,_= _cross_sections_from_csv_data(800,data,'Yeh')
        self.assertAlmostEqual(cross_sections_scofield['s'], 0.00145)
    
class test_datafile_path(unittest.TestCase):
    '''To check the path created by function get_csv_file_path is correct '''

    def test_scofield_directory_and_path(self):
        ## Simulate expected correct directory and path for scofield data
        correct_path = os.path.join(correct_directory, 'Scofield_csv_database.zip')
        _,_,Scofield_file_path = get_csv_file_path('Scofield')
    ## check the path obtained from get_csv_file_path is correct
        self.assertEqual(correct_path, Scofield_file_path)


    def test_yeh_directory_and_path(self):
        ## Simulate expected correct directory and path for yeh data
        correct_path = os.path.join(correct_directory, 'Yeh_Lindau_1985_Xsection_CSV_Database.zip')
        _,_,Yeh_file_path = get_csv_file_path('yeh')
     ## check the path obtained from get_csv_file_path is correct   
        self.assertEqual(correct_path, Yeh_file_path)



if __name__ == '__main__':
    unittest.main()