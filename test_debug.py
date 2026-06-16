#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="http://localhost:20128/v1",
    timeout=30.0
)

print("Testing local Kiro API...")

try:
    response = client.chat.completions.create(
        model="oc/big-pickle",
        messages=[
            {"role": "user", "content": "Write a short test response in Russian about vibe coding (2-3 sentences)."}
        ],
        max_tokens=150,
        stream=False
    )

    print("\nFull response object:")
    print(response)
    print("\nMessage content:")
    print(response.choices[0].message.content)
    print("\nAPI works!")
except Exception as e:
    print(f"Error: {e}")
