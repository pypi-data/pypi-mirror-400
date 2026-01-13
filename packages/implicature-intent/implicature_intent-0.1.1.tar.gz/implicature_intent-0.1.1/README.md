# Implicature Intent

**Detect implicit intent vs. tone in short conversational turns.**

`implicature-intent` is a lightweight, zero-dependency Python library designed to separate *what* someone means (Intent) from *how* they say it (Tone). It is deterministic, explainable, and fast.

## Why Intent ≠ Sentiment?

Sentiment analysis often conflates "tone" with "intent":

| Response | Sentiment Tools Say | Actual Intent |
|----------|---------------------|---------------|
| "I'd love to, but I'm swamped." | Positive ("love") | **NO** |
| "Fine, I'll do it." | Negative | **YES** |
| "How about Tuesday instead?" | Neutral | **Counter-offer** |
| "I guess so, if I have to." | Negative | **YES** (reluctant) |

This library disentangles these signals.

## Features

- **Zero Dependencies**: Fast, heuristic-based scoring
- **Explainable**: Returns evidence phrases and confidence scores
- **Actionable Output**: Commitment level, needs_clarification flags, response types
- **Offline-First**: No API calls, no network required

## Installation

```bash
pip install implicature-intent
```

## Quick Start

```python
from implicature_intent import analyze_intent

result = analyze_intent("I'd love to, but I have a conflict.")

print(result["orientation"])      # "NO"
print(result["sentiment_tone"])   # "positive"
print(result["intent_type"])      # "polite_reject"
print(result["mismatch"])         # True (tone contradicts intent)
```

## Output Schema

```python
{
    # Core Intent
    "orientation": "YES" | "NO" | "NON_COMMITTAL" | "UNKNOWN",
    "intent_type": "direct_accept" | "polite_reject" | "angry_agreement" |
                   "reluctant_yes" | "conditional_yes" | "counter_offer" |
                   "soft_deferral" | "delegation" | ...,

    # Response Classification
    "response_type": "direct" | "conditional" | "counter_offer" |
                     "deferral" | "delegation" | "question",

    # Sentiment & Tone
    "sentiment_tone": "positive" | "negative" | "neutral" | "mixed",
    "sentiment_score": -1.0 to 1.0,

    # Actionable Signals
    "commitment_level": 0.0 to 1.0,      # How firm is this response?
    "needs_clarification": bool,          # Should you follow up?
    "mismatch": bool,                     # Tone contradicts intent?

    # Politeness
    "politeness": "low" | "medium" | "high",
    "politeness_score": 0.0 to 1.0,

    # Explainability
    "confidence": 0.0 to 1.0,
    "evidence_phrases": list[str],
    "explanation": str
}
```

## Examples

### Detecting Hidden "No"
```python
analyze_intent("Thanks for thinking of me, but I'm slammed this week.")
# → orientation: "NO", intent_type: "polite_reject", sentiment_tone: "positive"
```

### Angry Agreement
```python
analyze_intent("It's a stupid idea, but fine, I'll do it.")
# → orientation: "YES", intent_type: "angry_agreement", mismatch: True
```

### Counter-Offer
```python
analyze_intent("How about we push it to next Tuesday instead?")
# → orientation: "NO", response_type: "counter_offer", needs_clarification: True
```

### Conditional Yes
```python
analyze_intent("Sure, as long as we can wrap up by 5pm.")
# → orientation: "YES", response_type: "conditional", intent_type: "conditional_yes"
```

### Low Commitment
```python
analyze_intent("I'll try my best, hopefully I can make it work.")
# → orientation: "YES", commitment_level: 0.2, needs_clarification: True
```

## Use Cases

- **Sales CRM**: Detect when a lead is politely declining vs. genuinely interested
- **Customer Support**: Identify frustrated agreement vs. satisfied resolution
- **Meeting Scheduling**: Parse conditional availability and counter-offers
- **Chatbots**: Understand user intent beyond keyword matching
- **Email Analysis**: Flag responses that need follow-up

## Limitations

- **Sarcasm**: Hard to detect without audio/visual cues or deeper context
- **Domain-Specific Language**: "I'll table this" might be YES or NO depending on culture
- **Very Short Responses**: "Ok" is ambiguous without context

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build for distribution
python -m build
```

## Roadmap

- [ ] v0.2: Evaluation harness with benchmark dataset
- [ ] v0.3: Domain tuning (sales, support, scheduling)
- [ ] v0.4: Optional LLM adapter for complex cases

## License

MIT

---


Built by [Loom Labs](https://loomlabs.io)

## Research Inspiration

This library is inspired by the research paper [Disentangling Intent from Tone in Conversational Agents](https://www.tandfonline.com/doi/full/10.1080/08839514.2025.2565173).

