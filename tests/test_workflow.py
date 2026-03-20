import unittest

from agent.workflow import run_workflow


class WorkflowTests(unittest.TestCase):
    def test_workflow_generates_login_assertion_code(self):
        result = run_workflow(
            "Open login page and enter username test and password 1234 then click login",
            execute=False,
        )

        self.assertIn('page.fill("#username", "test")', result["generated_code"])
        self.assertIn('page.fill("#password", "1234")', result["generated_code"])
        self.assertIn('raise AssertionError', result["generated_code"])
        self.assertEqual(result["expected_result"], "Success")

    def test_workflow_generates_clean_youtube_code(self):
        result = run_workflow(
            "Go to youtube and click on the first video",
            execute=False,
        )

        self.assertNotIn("```", result["generated_code"])
        self.assertIn('page.goto("https://www.youtube.com"', result["generated_code"])
        self.assertIn('consent_buttons = [', result["generated_code"])
        self.assertIn('a[href*="/watch?v="]:visible', result["generated_code"])
        self.assertIn('first_video.scroll_into_view_if_needed(timeout=5000)', result["generated_code"])
        self.assertIn('raise RuntimeError("Could not find a clickable YouTube video on the page")', result["generated_code"])
        self.assertIn('print("Clicked first YouTube video")', result["generated_code"])


if __name__ == "__main__":
    unittest.main()
