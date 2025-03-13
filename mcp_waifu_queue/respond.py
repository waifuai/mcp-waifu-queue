# src/respond.py
# This file contains the core chatbot logic. It loads the distilgpt2 model, processes incoming prompts, and generates responses.

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import logging

from mcp_waifu_queue.config import Config

config = Config.load()

logging.basicConfig(level=logging.INFO)

device = 0 if torch.cuda.is_available() else -1
tokenizer = AutoTokenizer.from_pretrained(config.model_path)
model = AutoModelForCausalLM.from_pretrained(config.model_path)
if device >= 0:
    model = model.to(device).eval()

generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
max_new_tokens = config.max_new_tokens

# This function generates a suffix for a given prompt using the pre-trained language model.
def generate_suffix(prompt: str):
    """
    Generates a suffix for a given prompt using the pre-trained language model.

    Args:
        prompt: The input prompt.

    Returns:
        The generated suffix, or an empty string if an error occurs.
    """
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    if device >= 0:
        input_ids = input_ids.to(device)

    try:
        generation_result = generator(
            prompt,
            do_sample=True,
            min_length=len(prompt),
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
        )
        generated_text = generation_result[0]['generated_text']
        suffix = generated_text[len(prompt):]
        return suffix
    except RuntimeError as e:
        logging.error(f"RuntimeError in generate_suffix: {e}")
        return ""
    finally:
        if device >= 0:
            torch.cuda.empty_cache()

# This function generates a waifu reply by iteratively generating suffixes and combining them.
def waifu_reply(prompt: str):
    response = ""
    for _ in range(10):
        suffix = generate_suffix(prompt)
        if not suffix:
            break
        lines = suffix.split('\n')
        first_line = lines[0].split('"')[0]
        response += first_line
        prompt += first_line
        if len(lines) > 1 or '"' in suffix:
            break
    return response

# This function predicts the response for a given prompt using the waifu_reply function.
def predict_response(prompt):
    logging.info(f"Prompt: {prompt}")
    response = waifu_reply(prompt)
    logging.info(f"Response: {response}")
    return response