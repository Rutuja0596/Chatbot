import tiktoken

def count_tokens_openai(query):
    encoder = tiktoken.get_encoding("cl100k_base")  # Using the encoding used by GPT models
    tokens = encoder.encode(query)  # Tokenize the query
    return len(tokens)

# Example usage:
user_query = input("Type query: ")
token_count = count_tokens_openai(user_query)
print(f"Token count (OpenAI tokenizer): {token_count}")

