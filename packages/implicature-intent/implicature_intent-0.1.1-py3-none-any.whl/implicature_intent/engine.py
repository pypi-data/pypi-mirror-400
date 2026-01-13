import re
from typing import List, Optional, Dict, TypedDict

from .consts import (
    PHRASES_YES, PHRASES_NO, PHRASES_DEFERRAL,
    PHRASES_CONDITIONAL_YES, PHRASES_CONDITIONAL_NO,
    PHRASES_COUNTER_OFFER, PHRASES_DELEGATION, PHRASES_QUESTION_RESPONSE,
    PHRASES_PASSIVE_AGGRESSIVE, PHRASES_ENTHUSIASTIC, PHRASES_RELUCTANT,
    SENTIMENT_POSITIVE, SENTIMENT_NEGATIVE,
    POLITENESS_MARKERS, MODIFIERS_NEGATION, HEDGES,
    HIGH_COMMITMENT, LOW_COMMITMENT
)


class IntentObject(TypedDict):
    orientation: str  # "YES" | "NO" | "NON_COMMITTAL" | "UNKNOWN"
    intent_type: str
    response_type: str  # "direct" | "conditional" | "counter_offer" | "deferral" | "delegation" | "question"
    sentiment_tone: str  # "negative" | "neutral" | "positive" | "mixed"
    sentiment_score: float
    commitment_level: float  # 0.0 to 1.0 - how firm is this response?
    needs_clarification: bool  # should follow-up be requested?
    politeness: str  # "low" | "medium" | "high"
    politeness_score: float
    mismatch: bool
    confidence: float
    evidence_phrases: List[str]
    explanation: str


class Options(TypedDict, total=False):
    thresholds: Dict[str, float]
    customPhrases: Dict[str, List[str]]


def tokenize(text: str) -> List[str]:
    """Lowercase, replace non-word chars with space, split."""
    clean = re.sub(r"[^\w\s']", " ", text.lower())
    return [t for t in clean.split() if t]


def has_phrase(text_lower: str, phrases: List[str]) -> Optional[str]:
    """Check if any phrase exists in text with word boundaries."""
    padded = " " + text_lower + " "
    for p in phrases:
        if " " + p + " " in padded:
            return p
    return None


def analyze_intent(
    response: str,
    context: Optional[str] = None,
    options: Optional[Options] = None
) -> IntentObject:
    """
    Analyze a conversational response to detect intent vs. tone.

    Args:
        response: The response text to analyze
        context: Optional context/question that prompted the response
        options: Optional configuration overrides

    Returns:
        IntentObject with orientation, sentiment, commitment, and more
    """
    # Clean text for phrase matching
    clean_text = re.sub(r"[^\w\s']", " ", response.lower())
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    original_text = response  # Keep original for enthusiasm detection

    tokens = tokenize(response)
    evidence: List[str] = []

    # Initialize scores
    orientation_score = 0.0
    deferral_score = 0.0
    sentiment_score = 0.0
    politeness_score = 0.0
    commitment_score = 0.5  # Start neutral
    hedge_count = 0

    # === 1. ORIENTATION ANALYSIS ===
    yes_match = has_phrase(clean_text, PHRASES_YES)
    no_match = has_phrase(clean_text, PHRASES_NO)
    defer_match = has_phrase(clean_text, PHRASES_DEFERRAL)

    if yes_match:
        orientation_score += 0.8
        evidence.append(f'match:YES("{yes_match}")')

    if no_match:
        orientation_score -= 0.8
        evidence.append(f'match:NO("{no_match}")')

    if defer_match:
        deferral_score += 0.8
        evidence.append(f'match:DEFER("{defer_match}")')

    # === 2. RESPONSE TYPE DETECTION ===
    response_type = "direct"

    conditional_yes = has_phrase(clean_text, PHRASES_CONDITIONAL_YES)
    conditional_no = has_phrase(clean_text, PHRASES_CONDITIONAL_NO)
    counter_offer = has_phrase(clean_text, PHRASES_COUNTER_OFFER)
    delegation = has_phrase(clean_text, PHRASES_DELEGATION)
    question_response = has_phrase(clean_text, PHRASES_QUESTION_RESPONSE)

    if counter_offer:
        response_type = "counter_offer"
        evidence.append(f'type:COUNTER("{counter_offer}")')
        orientation_score -= 0.3  # Counter-offers lean toward NO on original ask
    elif delegation:
        response_type = "delegation"
        evidence.append(f'type:DELEGATION("{delegation}")')
    elif question_response or clean_text.strip().endswith("?"):
        response_type = "question"
        evidence.append('type:QUESTION')
    elif conditional_yes or conditional_no:
        response_type = "conditional"
        if conditional_yes:
            evidence.append(f'type:CONDITIONAL_YES("{conditional_yes}")')
        if conditional_no:
            evidence.append(f'type:CONDITIONAL_NO("{conditional_no}")')
            orientation_score -= 0.4
    elif defer_match:
        response_type = "deferral"

    # === 3. TONE DETECTION ===
    passive_aggressive = has_phrase(clean_text, PHRASES_PASSIVE_AGGRESSIVE)
    enthusiastic = has_phrase(clean_text, PHRASES_ENTHUSIASTIC)
    reluctant = has_phrase(clean_text, PHRASES_RELUCTANT)

    if passive_aggressive:
        evidence.append(f'tone:PASSIVE_AGGRESSIVE("{passive_aggressive}")')
        sentiment_score -= 0.3
    if enthusiastic or "!" in original_text:
        exclamation_count = original_text.count("!")
        if exclamation_count > 0:
            evidence.append(f'tone:ENTHUSIASTIC({"!" * min(exclamation_count, 3)})')
            sentiment_score += 0.2 * min(exclamation_count, 3)
    if reluctant:
        evidence.append(f'tone:RELUCTANT("{reluctant}")')
        sentiment_score -= 0.2

    # === 4. COMMITMENT ANALYSIS ===
    high_commit = has_phrase(clean_text, HIGH_COMMITMENT)
    low_commit = has_phrase(clean_text, LOW_COMMITMENT)

    if high_commit:
        commitment_score += 0.4
        evidence.append(f'commit:HIGH("{high_commit}")')
    if low_commit:
        commitment_score -= 0.3
        evidence.append(f'commit:LOW("{low_commit}")')

    # === 5. SENTIMENT & POLITENESS (token-level) ===
    for i, token in enumerate(tokens):
        score = 0.0

        if token in SENTIMENT_POSITIVE:
            score = 0.5
        elif token in SENTIMENT_NEGATIVE:
            score = -0.5

        if token in POLITENESS_MARKERS:
            politeness_score += 0.2
            evidence.append(f'polite:"{token}"')

        if token in HEDGES:
            hedge_count += 1
            commitment_score -= 0.1

        # Check negation (flip sentiment if preceded by negation)
        if i > 0 and tokens[i - 1] in MODIFIERS_NEGATION:
            score *= -1
            if score != 0:
                evidence.append(f'negated:"{token}"')

        sentiment_score += score

    # Clamp scores
    politeness_score = min(1.0, politeness_score)
    sentiment_score = max(-1.0, min(1.0, sentiment_score))
    commitment_score = max(0.0, min(1.0, commitment_score))

    # === 6. FINAL ORIENTATION ===
    orientation = "UNKNOWN"
    if deferral_score > 0.5:
        orientation = "NON_COMMITTAL"
    elif orientation_score > 0.2:
        orientation = "YES"
    elif orientation_score < -0.2:
        orientation = "NO"
    else:
        # Fallback to sentiment
        if sentiment_score > 0.5:
            orientation = "YES"
        elif sentiment_score < -0.5:
            orientation = "NO"

    # === 7. INTENT TYPE ===
    intent_type = "ambiguous"
    if orientation == "YES":
        if passive_aggressive or reluctant:
            intent_type = "reluctant_yes"
        elif sentiment_score < -0.2:
            intent_type = "angry_agreement"
        elif defer_match:
            intent_type = "hedged_yes"
        elif response_type == "conditional":
            intent_type = "conditional_yes"
        else:
            intent_type = "direct_accept"
    elif orientation == "NO":
        if sentiment_score > 0.2:
            intent_type = "polite_reject"
        elif response_type == "counter_offer":
            intent_type = "counter_offer"
        elif response_type == "conditional":
            intent_type = "conditional_no"
        else:
            intent_type = "direct_reject"
    elif orientation == "NON_COMMITTAL":
        if response_type == "delegation":
            intent_type = "delegation"
        else:
            intent_type = "soft_deferral"

    # === 8. MISMATCH DETECTION ===
    mismatch = (orientation == "NO" and sentiment_score > 0.2) or \
               (orientation == "YES" and sentiment_score < -0.2)

    # === 9. NEEDS CLARIFICATION ===
    needs_clarification = (
        orientation == "UNKNOWN" or
        response_type == "question" or
        response_type == "conditional" or
        response_type == "delegation" or
        len(tokens) < 3 or
        hedge_count >= 2 or
        commitment_score < 0.3
    )

    # === 10. CONFIDENCE ===
    confidence = 0.5
    if yes_match or no_match:
        confidence += 0.3
    if response_type == "direct":
        confidence += 0.1
    if mismatch:
        confidence -= 0.1
    if hedge_count > 0:
        confidence -= 0.05 * hedge_count
    if len(tokens) < 3:
        confidence -= 0.2

    confidence = max(0.0, min(1.0, confidence))

    # Adjust commitment based on orientation
    if orientation == "NO":
        commitment_score = 0.0  # NO means no commitment to the ask
    elif orientation == "NON_COMMITTAL":
        commitment_score = min(commitment_score, 0.3)

    # === BUILD EXPLANATION ===
    explanation_parts = [f"Detected {orientation}"]
    if response_type != "direct":
        explanation_parts.append(f"via {response_type}")
    if mismatch:
        explanation_parts.append("with tone mismatch")
    if needs_clarification:
        explanation_parts.append("- follow-up recommended")
    explanation = " ".join(explanation_parts) + f". Evidence: {', '.join(evidence[:5])}."

    return {
        "orientation": orientation,
        "intent_type": intent_type,
        "response_type": response_type,
        "sentiment_tone": _score_to_tone(sentiment_score),
        "sentiment_score": round(sentiment_score, 2),
        "commitment_level": round(commitment_score, 2),
        "needs_clarification": needs_clarification,
        "politeness": _score_to_politeness(politeness_score),
        "politeness_score": round(politeness_score, 2),
        "mismatch": mismatch,
        "confidence": round(confidence, 2),
        "evidence_phrases": evidence,
        "explanation": explanation
    }


def _score_to_tone(score: float) -> str:
    """Convert sentiment score to categorical tone."""
    if score > 0.3:
        return "positive"
    if score < -0.3:
        return "negative"
    if score == 0:
        return "neutral"
    return "mixed"


def _score_to_politeness(score: float) -> str:
    """Convert politeness score to categorical level."""
    if score > 0.6:
        return "high"
    if score > 0.2:
        return "medium"
    return "low"
