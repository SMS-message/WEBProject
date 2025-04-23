import unittest
# from data.functions import make_queue
from requests import delete


class MyTestCase(unittest.TestCase):
    # def test_queue(self):
    #     result = [1, 2, 3, 4, 5, 6]
    #     self.assertEqual(make_queue(2140097795, "../db/VideoHoster.db"), result)

    # def test_del(self):
    #     expected_res = {
    #                 "status": "200",
    #                 "info": f"video 2140097795_1862.mp4 succesfully deleted."
    #             }
    #
    #     self.assertEqual(expected_res, delete("http://127.0.0.1:1501/api/videos/107").json())

    @staticmethod
    def test_delete():
        print(delete("http://127.0.0.1:1501/api/videos/110").json())

if __name__ == '__main__':
    unittest.main()
