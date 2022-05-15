#this will be to use the basic test suite for the refactor.py

import unittest as utt
import refactor
class TestChunkMethods(utt.TestCase):

    def test_sanity(self):
        self.assertEqual(1,1)
    

    def test_compare_timestamps(self):
        older_date = "2022-05-07T12:58:51.000Z"
        newer_date = "2022-05-10T12:58:51.000Z"
        is_new =refactor.compare_timestamps(older_date,newer_date)
        self.assertEqual(is_new,True) 
        is_old =refactor.compare_timestamps(newer_date,older_date)
        self.assertNotEqual(is_old,is_new) 

def test_extract_sort_index(self):
    


    self.assertEqual(1,1)



