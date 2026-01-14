import unittest

from app.session.summarizer import LLMSummarizer, SummarizerConfig
from app.session.models import SessionItem


class SummarizerConfigTest(unittest.TestCase):
    def test_privacy_default_off(self):
        def fake_llm(prompt: str):
            return "summary"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig())
        block = summarizer([SessionItem(role="user", content="hi")])
        self.assertNotIn("prompt_preview", block.metadata)
        self.assertNotIn("output_preview", block.metadata)

    def test_tool_performance_toggle(self):
        captured = {}

        def fake_llm(prompt: str):
            captured["prompt"] = prompt
            return "summary"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig(include_tool_performance=False))
        summarizer([SessionItem(role="user", content="hi"), SessionItem(role="tool", content="tool output")])
        self.assertNotIn("Tool Calls & Outcomes", captured["prompt"])

    def test_max_output_tokens_hint(self):
        hints = {}

        def fake_llm(prompt: str, **kwargs):
            hints.update(kwargs)
            return "summary"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig(max_output_tokens=123))
        summarizer([SessionItem(role="user", content="hi")])
        self.assertEqual(hints.get("max_output_tokens"), 123)

    def test_max_output_tokens_fallback_for_plain_callable(self):
        called = {"count": 0}

        def fake_llm(prompt: str):
            called["count"] += 1
            return "summary"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig(max_output_tokens=50))
        summarizer([SessionItem(role="user", content="hi")])
        self.assertEqual(called["count"], 1)


if __name__ == "__main__":
    unittest.main()
