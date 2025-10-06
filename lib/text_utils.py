import re
from transformers import AutoTokenizer

# Initialize tokenizer globally to avoid reloading it on every call
try:
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
except Exception as e:
    print(f"Error initializing tokenizer: {e}")
    tokenizer = None

def scrub_unsafe_characters(text: str) -> str:
    """
    Removes characters from the input text that are not in the allowed set.

    Allowed characters: a-z, A-Z, 0-9, ?, !, ,, space.

    Args:
        text: The input string to scrub.

    Returns:
        The scrubbed string.
    """
    # Define the allowed characters using a regex character set
    # The characters are: a-z, A-Z, 0-9, ?, !, ,, space, *
    allowed_chars_pattern = r"[a-zA-Z0-9?,!\*\n\.\'\-\; ]"  # Added * and \n for newlines
    
    
    # Use re.findall to get all characters that match the allowed pattern
    # Then join them back into a string
    scrubbed_text = "".join(re.findall(allowed_chars_pattern, text))
    
    return scrubbed_text

def chunk_text(text: str, max_tokens: int = 200) -> list[str]:
    """
    Chunks the input text into smaller pieces based on the maximum token count.

    Args:
        text: The input string to chunk.
        max_tokens: The maximum number of tokens per chunk.

    Returns:
        A list of text chunks.
    """
    if tokenizer is None:
        print("Tokenizer not initialized. Cannot chunk text.")
        return [text] # Return original text if tokenizer failed to load

    tokens = tokenizer.encode(text)
    chunks = []
    current_chunk_tokens = []

    for token in tokens:
        current_chunk_tokens.append(token)
        if len(current_chunk_tokens) >= max_tokens:
            chunk_text = tokenizer.decode(current_chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text)
            current_chunk_tokens = []

    # Add any remaining tokens as the last chunk
    if current_chunk_tokens:
        chunk_text = tokenizer.decode(current_chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)

    return chunks

# Example usage (optional, for testing the function)
if __name__ == "__main__":
    test_string = "Hello, world! This is a test with some unsafe characters like @#$%^&*()_+={}[]|\\:;\"'<>. And emojis 😊👍."
    scrubbed_string = scrub_unsafe_characters(test_string)
    print(f"Original: {test_string}")
    print(f"Scrubbed: {scrubbed_string}")

    long_text = "This is a very long sentence that needs to be chunked. " * 50 # Create a long text for testing chunking
    chunked_texts = chunk_text(long_text, max_tokens=50) # Use a smaller max_tokens for easier testing
    print(f"\n--- Chunking Test ---")
    print(f"Original length (tokens): {len(tokenizer.encode(long_text)) if tokenizer else 'N/A'}")
    print(f"Number of chunks: {len(chunked_texts)}")
    for i, chunk in enumerate(chunked_texts):
        print(f"Chunk {i+1} (length: {len(tokenizer.encode(chunk)) if tokenizer else 'N/A'} tokens): {chunk[:100]}...") # Print first 100 chars of chunk