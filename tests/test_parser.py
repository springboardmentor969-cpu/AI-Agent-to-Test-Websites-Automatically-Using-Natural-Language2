import unittest

from agent.parser import parse_instruction_details


class ParserTests(unittest.TestCase):
    def test_login_prompt_extracts_credentials(self):
        parsed = parse_instruction_details(
            "Open login page and enter username test and password 1234 then click login"
        )

        self.assertEqual(parsed.target_type, "demo_login")
        self.assertEqual(parsed.username, "test")
        self.assertEqual(parsed.password, "1234")
        self.assertEqual(parsed.actions[1].value, "test")
        self.assertEqual(parsed.actions[2].value, "1234")

    def test_login_prompt_extracts_credentials_with_as(self):
        parsed = parse_instruction_details(
            "Open the local file login.html, type username as test and password as 1234"
        )

        self.assertEqual(parsed.username, "test")
        self.assertEqual(parsed.password, "1234")

    def test_external_site_prompt_targets_website(self):
        parsed = parse_instruction_details("Go to YouTube and click on the first video")

        self.assertEqual(parsed.target_type, "website")
        self.assertEqual(parsed.target_url, "https://www.youtube.com")
        self.assertEqual(parsed.actions[-1].target, "first_video")


if __name__ == "__main__":
    unittest.main()
