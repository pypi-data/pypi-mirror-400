# Heuristic Dictionaries matching Node version

# === ORIENTATION PHRASES ===

PHRASES_YES = [
    "yes", "yeah", "yep", "sure", "ok", "okay", "alright", "sounds good",
    "approved", "absolutely", "definitely", "certainly", "works for me",
    "i'm in", "count me in", "go ahead", "agreed", "perfect", "fine by me",
    "will do", "on it", "consider it done", "no problem", "happy to",
    "of course", "gladly", "affirmative", "you bet", "for sure",
    "i guess so", "i suppose"
]

PHRASES_NO = [
    "no", "nope", "nah", "negative", "can't", "cannot", "won't",
    "impossible", "unable", "unfortunately", "pass", "not possible",
    "don't think so", "i'm out", "reviewing other options", "cancel",
    "decline", "reject", "refuse", "not interested", "no way",
    "not a chance", "forget it", "no can do", "out of the question"
]

PHRASES_DEFERRAL = [
    "maybe", "perhaps", "possibly", "not sure", "unsure",
    "circle back", "let me check", "check my calendar", "review internally",
    "get back to you", "we'll see", "need time", "thinking about it",
    "tentative", "pencil in", "need to think", "let me see",
    "i'll consider", "give me a moment", "hold on", "one moment"
]

# === CONDITIONAL PHRASES ===

PHRASES_CONDITIONAL_YES = [
    "if you", "as long as", "provided that", "assuming", "only if",
    "depends on", "contingent on", "given that", "on the condition",
    "subject to", "pending", "would need", "if we can", "if it's possible"
]

PHRASES_CONDITIONAL_NO = [
    "not unless", "only way", "can't without", "would need to",
    "impossible without", "not until", "only after", "except if"
]

# === RESPONSE TYPE PHRASES ===

PHRASES_COUNTER_OFFER = [
    "how about", "what if", "instead", "alternatively", "another option",
    "would it work if", "can we", "could we", "what about", "rather",
    "prefer to", "suggest we", "propose", "counter", "different approach"
]

PHRASES_DELEGATION = [
    "ask", "check with", "talk to", "reach out to", "contact",
    "better suited", "not my area", "handles that", "responsible for",
    "speak to", "consult", "refer you to", "belongs to", "owned by"
]

PHRASES_QUESTION_RESPONSE = [
    "can i", "could i", "would it be", "is it okay if", "do you mind if",
    "what do you think", "how do you feel", "is that alright"
]

# === TONE PHRASES ===

PHRASES_PASSIVE_AGGRESSIVE = [
    "i guess", "if you say so", "whatever you want", "no choice",
    "if i have to", "if that's what you need", "if you insist",
    "fine then", "suit yourself", "have it your way", "as you wish"
]

PHRASES_ENTHUSIASTIC = [
    "!", "!!", "absolutely", "definitely", "100%", "can't wait",
    "excited", "love to", "thrilled", "would love", "amazing",
    "fantastic", "perfect", "wonderful", "brilliant"
]

PHRASES_RELUCTANT = [
    "i suppose", "i guess so", "if i must", "fine", "alright then",
    "okay fine", "very well", "so be it"
]

# === SENTIMENT WORDS ===

SENTIMENT_POSITIVE = [
    "great", "good", "awesome", "excellent", "amazing", "love",
    "happy", "glad", "excited", "fantastic", "perfect", "nice",
    "cool", "sweet", "appreciate", "thanks", "thank you",
    "wonderful", "brilliant", "delighted", "pleased", "thrilled",
    "grateful", "fortunate", "superb", "outstanding"
]

SENTIMENT_NEGATIVE = [
    "bad", "terrible", "awful", "horrible", "hate", "angry",
    "stupid", "dumb", "annoying", "waste", "ridiculous", "poor",
    "shame", "disappointed", "sad", "sorry", "frustrated",
    "upset", "irritated", "concerned", "worried", "unfortunate",
    "regret", "unacceptable", "problematic"
]

# === MODIFIERS ===

POLITENESS_MARKERS = [
    "please", "thanks", "thank you", "appreciate", "kindly",
    "would you mind", "if possible", "grateful", "honored",
    "apologies", "sorry", "excuse me", "pardon"
]

HEDGES = [
    "might", "could", "would", "possibly", "think", "believe",
    "seem", "appear", "suggest", "probably", "likely", "perhaps",
    "suppose", "assume", "guess", "hope"
]

MODIFIERS_NEGATION = ["not", "n't", "never", "no", "hardly", "fail", "without"]

INTENSIFIERS = [
    "very", "really", "so", "totally", "absolutely", "extremely", "highly",
    "completely", "entirely", "utterly", "incredibly", "seriously"
]

# === COMMITMENT INDICATORS ===

HIGH_COMMITMENT = [
    "will", "promise", "guarantee", "commit", "definitely",
    "absolutely", "certainly", "for sure", "no doubt", "100%",
    "consider it done", "you have my word", "i'll make sure"
]

LOW_COMMITMENT = [
    "try", "attempt", "maybe", "might", "possibly", "hopefully",
    "we'll see", "no promises", "can't guarantee", "not sure if",
    "do my best", "see what i can do"
]
