import unittest

class TestItemCreation(unittest.TestCase):

    def setUp(self):
        self.item = Item.item('name', 0, 'desc')

    def test_If_First_Element_Is_String(self):
        self.assertEqual(self.item[0], str)

    def test_If_Second_Element_Is_Integer(self):
        self.assertEqual(self.item[1], int)

    def test_If_Third_Element_is_String(self):
        self.assertEqual(self.item[2], str)
    
    def test_If_Has_All_Elements(self):
        pass

    def tearDown(self):
        pass

class TestDescribe(unittest.TestCase):

    def setUp(self):
        self.item = Item.item('name', 0, 'desc')

    def test_If_Returns_Desc(self):
        self.assertEqual(self.item[2] == 'desc')

if __name__ == '__main__':
    unittest.main() 
