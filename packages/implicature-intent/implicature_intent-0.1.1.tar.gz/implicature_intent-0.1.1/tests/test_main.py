import pytest
from implicature_intent import analyze_intent


class TestBasicOrientation:
    """Test basic YES/NO/NON_COMMITTAL detection"""

    def test_direct_yes(self):
        res = analyze_intent("Absolutely, I'd love to.")
        assert res["orientation"] == "YES"
        assert res["sentiment_tone"] == "positive"
        assert res["intent_type"] == "direct_accept"

    def test_direct_no(self):
        res = analyze_intent("No, I can't do that.")
        assert res["orientation"] == "NO"
        assert res["intent_type"] == "direct_reject"

    def test_soft_deferral(self):
        res = analyze_intent("Let me check my calendar and get back to you.")
        assert res["orientation"] == "NON_COMMITTAL"
        assert res["intent_type"] == "soft_deferral"
        assert res["response_type"] == "deferral"


class TestIntentTypes:
    """Test various intent type classifications"""

    def test_polite_refusal(self):
        res = analyze_intent("Thanks for asking, but unfortunately I can't.")
        assert res["orientation"] == "NO"
        assert res["intent_type"] == "polite_reject"
        assert "polite" in " ".join(res["evidence_phrases"])

    def test_angry_agreement(self):
        res = analyze_intent("It's stupid, but yes.")
        assert res["orientation"] == "YES"
        assert res["sentiment_tone"] == "negative"
        assert res["intent_type"] == "angry_agreement"
        assert res["mismatch"] == True

    def test_reluctant_yes(self):
        res = analyze_intent("I guess so, if I have to.")
        assert res["orientation"] == "YES"
        assert res["intent_type"] == "reluctant_yes"


class TestResponseTypes:
    """Test response type detection"""

    def test_counter_offer(self):
        res = analyze_intent("How about we do it next Tuesday instead?")
        assert res["response_type"] == "counter_offer"
        assert res["intent_type"] == "counter_offer"

    def test_conditional_yes(self):
        res = analyze_intent("Sure, as long as we finish by 5pm.")
        assert res["orientation"] == "YES"
        assert res["response_type"] == "conditional"
        assert res["intent_type"] == "conditional_yes"

    def test_delegation(self):
        res = analyze_intent("You should talk to Sarah, she handles that.")
        assert res["response_type"] == "delegation"
        assert res["needs_clarification"] == True

    def test_question_response(self):
        res = analyze_intent("Can I get back to you tomorrow?")
        assert res["response_type"] == "question"
        assert res["needs_clarification"] == True


class TestCommitment:
    """Test commitment level scoring"""

    def test_high_commitment(self):
        res = analyze_intent("I will definitely have it done by Friday.")
        assert res["orientation"] == "YES"
        assert res["commitment_level"] >= 0.7

    def test_low_commitment(self):
        res = analyze_intent("I'll try my best, hopefully I can do it.")
        assert res["commitment_level"] <= 0.4

    def test_no_commitment(self):
        res = analyze_intent("No, I can't do that.")
        assert res["commitment_level"] == 0.0


class TestNeedsClarification:
    """Test needs_clarification flag"""

    def test_clear_yes_no_clarification(self):
        res = analyze_intent("Yes, absolutely, I'll handle it.")
        assert res["needs_clarification"] == False

    def test_short_response_needs_clarification(self):
        res = analyze_intent("Ok")
        assert res["needs_clarification"] == True

    def test_hedged_needs_clarification(self):
        res = analyze_intent("I think maybe I could possibly do it.")
        assert res["needs_clarification"] == True


class TestToneDetection:
    """Test tone and enthusiasm detection"""

    def test_enthusiastic(self):
        res = analyze_intent("Yes!!! That sounds amazing!")
        assert res["sentiment_tone"] == "positive"
        assert "ENTHUSIASTIC" in " ".join(res["evidence_phrases"])

    def test_passive_aggressive(self):
        res = analyze_intent("Fine, if you say so, whatever you want.")
        assert "PASSIVE_AGGRESSIVE" in " ".join(res["evidence_phrases"])


class TestEdgeCases:
    """Test edge cases and complex scenarios"""

    def test_mixed_signals(self):
        # "love to" is positive, "but I can't" is NO
        res = analyze_intent("I'd love to, but I can't make it.")
        assert res["orientation"] == "NO"
        assert res["mismatch"] == True

    def test_empty_adjacent(self):
        res = analyze_intent("   Sure   ")
        assert res["orientation"] == "YES"

    def test_negation_flip(self):
        res = analyze_intent("That's not bad at all.")
        # "not bad" should flip to positive
        assert res["sentiment_score"] > 0
