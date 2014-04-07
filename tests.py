import sys
import unittest
import planplex

URL = 'http://www.planplex.com'
USERNAME = ''
PASSWORD = ''

class TestPlanplex(unittest.TestCase):

    def setUp(self):
        self.session = planplex.Session(URL)
        
    def test_login(self):
        response = self.session.login(USERNAME, PASSWORD)
        self.assertEqual(response.status_code, 200)

        response = self.session.logout()
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    sys.argv = sys.argv[2:]
    unittest.main()
