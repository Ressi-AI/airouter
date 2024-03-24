import airouter
airouter.models.LLM.GPT_4_1106_PREVIEW

if __name__ == '__main__':
  outputs = airouter.StreamedCompletion.create(
    model='azure_openai/gpt-4-1106-preview',
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  )

  # outputs = airouter.StreamedCompletion.create_interactive(
  #   # models=['mixtral:8x7b'],
  #   models=[airouter.models.LLM.LLAMA2_13B],
  #   messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  # )

  print(outputs)
