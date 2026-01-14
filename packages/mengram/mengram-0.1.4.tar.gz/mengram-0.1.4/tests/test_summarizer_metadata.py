import unittest

from app.session.models import SessionItem
from app.session.summarizer import LLMSummarizer, SummarizerConfig


class SummarizerMetadataTest(unittest.TestCase):
    def test_metadata_in_summary_block(self):
        def fake_llm(prompt: str):
            self.assertIn("Do not invent facts", prompt)
            # braces in tool content should not break formatting
            self.assertNotIn("{", prompt.split("Conversation:")[-1].splitlines()[-1])
            # return longer than cap to trigger truncation
            return "Short summary " * 50

        summarizer = LLMSummarizer(
            fake_llm,
            SummarizerConfig(
                tool_trim_chars=5,
                max_summary_words=5,
                record_previews=True,
                prompt_preview_chars=50,
                output_preview_chars=20,
            ),
        )
        items = [
            SessionItem(role="user", content="hello"),
            SessionItem(role="tool", content="1234567890 {foo}", name="t1"),
        ]
        block = summarizer(items)
        self.assertIn("tool_trimmed", block.metadata)
        self.assertEqual(block.metadata.get("tool_trimmed"), 1)
        self.assertIn("prompt_preview", block.metadata)
        self.assertIn("output_preview", block.metadata)
        self.assertLessEqual(len(block.metadata.get("prompt_preview", "")), 50)
        self.assertLessEqual(len(block.metadata.get("output_preview", "")), 20)
        self.assertTrue(block.metadata.get("truncated_summary"))
        self.assertEqual(block.metadata.get("original_word_count"), 100)
        self.assertEqual(block.metadata.get("kept_word_count"), 5)
        self.assertIn("t1", block.metadata.get("tool_trimmed_names", []))
        trimmed_tools = block.metadata.get("trimmed_tools", [])
        self.assertTrue(any(t.get("name") == "t1" for t in trimmed_tools))

    def test_record_previews_off(self):
        def fake_llm(prompt: str):
            return "summary"

        summarizer = LLMSummarizer(fake_llm, SummarizerConfig(record_previews=False))
        block = summarizer([SessionItem(role="user", content="hi")])
        self.assertNotIn("prompt_preview", block.metadata)
        self.assertNotIn("output_preview", block.metadata)


if __name__ == "__main__":
    unittest.main()
