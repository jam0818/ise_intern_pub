import unittest
from src.summanote_database import Summanote_database


class TestSummanoteDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Summanote_database()

    def tearDown(self):
        self.db.db.drop_table('summanote')

    def test_insert_data(self):
        title = 'Test Title'
        note_path = '/path/to/note'
        self.db.insert_data(title, note_path)

        # データが正しく挿入されたことを確認
        data = self.db.select_single_data('title', title)
        self.assertIsNotNone(data)
        self.assertEqual(data[1], title)
        self.assertEqual(data[2], note_path)

    def test_delete_data(self):
        title = 'Test Title'
        note_path = '/path/to/note'
        self.db.insert_data(title, note_path)

        # データが正しく挿入されたことを確認
        data = self.db.select_single_data('title', title)
        self.assertIsNotNone(data)
        self.assertEqual(data[1], title)
        self.assertEqual(data[2], note_path)

        # データが正しく削除されたことを確認
        self.db.delete_data('title', title)
        data = self.db.select_single_data('title', title)
        self.assertIsNone(data)


if __name__ == '__main__':
    unittest.main()
