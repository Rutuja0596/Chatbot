import openai

client = openai.OpenAI(
    api_key="a329f819-51f4-4953-9ac3-9d36093a7021",
    base_url="https://api.sambanova.ai/v1",
)

response = client.chat.completions.create(
    model='Meta-Llama-3.1-8B-Instruct',
    messages=[{"role":"system","content":"You are a helpful assistant for coding"},{"role":"user","content":"What is the capital of India"}],
    temperature =  0.1,
    top_p = 0.1
)

print(response.choices[0].message.content)
