from openai import OpenAI

client = OpenAI()

prompt = """
What is greater, 9.53 or 9.67?
"""

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": prompt,
        },
    ],
    stream=True,
    reasoning_effort="low",
)

for chunk in stream:
    print(chunk)
    print(chunk.choices[0].delta)
    print("****************")

# response = client.chat.completions.create(
#     model="gpt-5",
#     reasoning_effort="low",
#     messages=[
#         {
#             "role": "user",
#             "content": prompt,
#         },
#     ],
# )

# print(response.choices[0].message.content)
