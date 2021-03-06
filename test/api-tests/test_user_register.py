import unittest
import json
import test_helpers as helpers
from copy import copy
import subprocess
import os


class TestUserRegister(unittest.TestCase):

    def setUp(self):
        resp_auth = helpers.server_post("/auth", {"username":"teacher_coll2", "password":"noway"})
        self.auth_hash = json.loads(resp_auth.read())["token"]
        self.user_hash = {"first_name": "bob", "last_name":"monkey", "email":"mail@mail.com", "team":"team1"}
        self.user_hash_unicode = {"first_name": u"b\u00F6b", "last_name":"monkey", "email":"mail@mail.com", "team":"team1"}
        self.user_hash_trailing = {"first_name": "    space     ", "last_name":"win", "email":"mail@mail.com", "team":"team1"}
        os.system("rm -f users.csv")

    def dump_db(self):
        p = subprocess.Popen("../../nemesis/scripts/dump_db.py")
        code = p.wait()
        return open("users.csv").read(), code

    def test_no_authentication(self):
        result = helpers.server_post("/user/register", self.user_hash)
        self.assertEqual(result.status, 403)

    def test_register_response_code(self):
        local_hash = copy(self.user_hash)
        local_hash["token"] = self.auth_hash
        result = helpers.server_post("/user/register", local_hash)
        self.assertEqual(result.status, 200)

    def test_register_database(self):
        local_hash = copy(self.user_hash)
        local_hash["token"] = self.auth_hash

        helpers.server_post("/user/register", local_hash)
        print helpers.get_registrations()
        self.assertEqual(len(helpers.get_registrations()), 1)

    def test_dump_db_ascii(self):
        local_hash = copy(self.user_hash)
        local_hash["token"] = self.auth_hash
        helpers.server_post("/user/register", local_hash)
        users_csv,code = self.dump_db()
        self.assertTrue("bob" in users_csv)
        self.assertTrue("monkey" in users_csv)
        self.assertTrue("mail@mail.com" in users_csv)
        self.assertTrue("team1" in users_csv)

    def test_dump_db_unicode(self):
        local_hash = copy(self.user_hash_unicode)
        local_hash["token"] = self.auth_hash
        helpers.server_post("/user/register", local_hash)
        users_csv, code = self.dump_db()
        self.assertTrue(u"b\u00F6b" in users_csv.decode("utf-8"))
        self.assertTrue("monkey" in users_csv)
        self.assertTrue("mail@mail.com" in users_csv)
        self.assertTrue("team1" in users_csv)

    def test_dump_db_trailing(self):
        local_hash = copy(self.user_hash_trailing)
        local_hash["token"] = self.auth_hash
        helpers.server_post("/user/register", local_hash)
        users_csv, code = self.dump_db()
        self.assertEqual("space", users_csv.split("\n")[0].split(",")[3])
        self.assertTrue("win" in users_csv)
        self.assertTrue("mail@mail.com" in users_csv)
        self.assertTrue("team1" in users_csv)

    def test_dump_db_twice(self):
        local_hash = copy(self.user_hash_trailing)
        local_hash["token"] = self.auth_hash
        helpers.server_post("/user/register", local_hash)
        self.dump_db()
        csv, code = self.dump_db()
        self.assertEqual(code, 1)


    def tearDown(self):
        helpers.server_post("/deauth", {"token":self.auth_hash})
        helpers.delete_db()
        os.system("rm -f users.csv")



if __name__ == '__main__':
    unittest.main()
