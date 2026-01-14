"""Configuration management for impostor."""

import os
from typing import Literal

import dspy
from dspy.adapters.baml_adapter import BAMLAdapter
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_gpt_5_mini(reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low", verbosity: Literal["low", "medium", "high"] = "low"):
    """get a gpt-5 mini model"""
    full_model = f"openai/gpt-5-mini"

    return dspy.LM(full_model, temperature=1.0, max_tokens=40_000, reasoning_effort=reasoning_effort, verbosity=verbosity, allowed_openai_params=["reasoning_effort","verbosity"], api_key=OPENAI_API_KEY)


def get_gpt_5_2(reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low", verbosity: Literal["low", "medium", "high"] = "low"):
    """get a gpt-5 model"""
    full_model = f"openai/gpt-5.2"

    return dspy.LM(full_model, temperature=1.0, max_tokens=40_000, reasoning_effort=reasoning_effort, verbosity=verbosity, allowed_openai_params=["reasoning_effort","verbosity"], api_key=OPENAI_API_KEY)



REASONING_EFFORT: Literal["minimal", "low", "medium", "high"] = "high"
VERBOSITY: Literal["low", "medium", "high"] = "low"
CACHE: bool = False

gpt_5_mini = get_gpt_5_mini(reasoning_effort=REASONING_EFFORT, verbosity=VERBOSITY)
gpt_5_2 = get_gpt_5_2(reasoning_effort=REASONING_EFFORT, verbosity=VERBOSITY)


# DSPY CONFIGURATION
dspy.configure(lm=gpt_5_mini, adapter=BAMLAdapter())
dspy.configure_cache(enable_disk_cache=CACHE, enable_memory_cache=CACHE)


## PARALLEL EXECUTION

# async def run(input):
#     result = await program.acall(input=input)
#     return result

# tasks = [run(input) for input in inputs]
# results = await asyncio.gather(*tasks)