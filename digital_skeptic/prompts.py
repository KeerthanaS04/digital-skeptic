CLAIMS_PROMPT = (
"""
You are a critical-reading assistant. Extract the 3–5 *core factual claims* from the article below.
Each claim must be *verifiable* and *succinct*. Avoid opinions or vague statements.
Return plain bullets; no numbering, no extra commentary.


Article:
"""
)


COUNTER_ARGUMENT_PROMPT = (
"""
You are simulating an informed skeptic who disagrees with the article's main thrust.
Briefly (4–8 sentences) summarize the article from an *opposing viewpoint*, highlighting
possible biases, missing context, or alternative explanations. Maintain a professional tone.


Article:
"""
)


VERIFICATION_QUESTION_PROMPT = (
"""
Given the article text and its extracted core claims, propose 3–4 *specific verification questions*
that a reader could ask to independently verify the claims. Be concrete and actionable.
Return as plain bullets.


Article:
"""
)