import unittest

from core.chatbot import analyze_sentiment, check_faq


class SupportRulesTests(unittest.TestCase):
    def test_matches_known_faq_case_insensitively(self):
        self.assertIn("30 days", check_faq("What is the RETURN policy?"))

    def test_unknown_question_has_no_faq_answer(self):
        self.assertIsNone(check_faq("Can I change the color?"))

    def test_negative_message_scores_below_neutral(self):
        self.assertLess(analyze_sentiment("This is terrible and broken"), 0.5)

    def test_mixed_message_balances_sentiment(self):
        self.assertEqual(analyze_sentiment("great but disappointed"), 0.5)


if __name__ == "__main__":
    unittest.main()
