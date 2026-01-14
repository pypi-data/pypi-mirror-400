# ArcMethod

ArcMethod is an LLM interaction framework based on the Arc Yöntemi.

## Installation

```
pip install arc-method
```

## Usage

```python
from arc_method.core import ArcMethod

arc = ArcMethod(provider="llama", api_key="YOUR_GROQ_KEY")

# SYSTEM = extraction rules, nothing else
system = """
You are an AI assistant.
Your role is to extract the GUID-like reference code embedded inside user text.
The code typically follows patterns such as XXX-XXX-XXXX-XXXX or similar.
Return only the extracted code with no extra words or explanations.
"""

# USER = long natural text (data only)
user = "Transfer from acct 123 to acct 456 completed successfully on 25/11/2025. Internal reference: TRT-REF-9988-ABCD. Please verify with finance."

print(arc.interact(system, user))
```

## Providers
- **openai** → GPT-4.1 family  
- **llama** → Groq LLaMA 3.3 70B Versatile

## License
ARC
