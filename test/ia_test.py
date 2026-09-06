from openai import OpenAI


API_KEY = "sk-nous-aRuYqRRbxQoVAaSKA3MjzNR6FPdxd9RI"


client = OpenAI(
    api_key=API_KEY,
    base_url="https://inference-api.nousresearch.com/v1"
)


MODEL = "stepfun/step-3.7-flash:free"


response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Hola, ¿quién eres?"
        }
    ],
    extra_body={
        "tags": ["user=robot"]
    }
)


print("Respuesta del LLM:")
print(response.choices[0].message.content)