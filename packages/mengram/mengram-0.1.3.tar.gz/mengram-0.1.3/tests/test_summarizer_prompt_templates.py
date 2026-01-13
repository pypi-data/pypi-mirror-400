import unittest

from app.session.summary_prompts import DEFAULT_SUMMARY_TEMPLATE, get_summary_prompt
from app.session.summarizer import LLMSummarizer, SummarizerConfig
from app.session.models import SessionItem


class SummarizerPromptTemplatesTest(unittest.TestCase):
    def test_registry_returns_default(self):
        prompt = get_summary_prompt(DEFAULT_SUMMARY_TEMPLATE)
        self.assertTrue(prompt)
        self.assertIn("UNVERIFIED", prompt)
        self.assertIn("Superseded", prompt)
        self.assertIn("User Goal", prompt)

    def test_llm_summarizer_uses_template(self):
        captured_prompt = {}

        def fake_llm(prompt: str):
            captured_prompt["p"] = prompt
            return "ok"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig(template_name=DEFAULT_SUMMARY_TEMPLATE))
        summarizer([SessionItem(role="user", content="hi")])
        self.assertIn("User Goal / Current Ask", captured_prompt["p"])
        self.assertIn("Do not invent facts", captured_prompt["p"])

    def test_metadata_template_name(self):
        def fake_llm(prompt: str):
            return "summary"

        block = LLMSummarizer(fake_llm, SummarizerConfig(template_name=DEFAULT_SUMMARY_TEMPLATE))(
            [SessionItem(role="user", content="hello")]
        )
        self.assertEqual(block.metadata.get("template_name"), DEFAULT_SUMMARY_TEMPLATE)
        self.assertEqual(block.metadata.get("max_summary_words"), 200)

    def test_unknown_template_errors(self):
        with self.assertRaises(ValueError) as ctx:
            get_summary_prompt("doesnotexist")
        self.assertIn("doesnotexist", str(ctx.exception))
        self.assertIn("generic.v1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
