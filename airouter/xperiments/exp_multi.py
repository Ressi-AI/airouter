import airouter

if __name__ == '__main__':
  # outputs = airouter.StreamedCompletion.create_interactive(
  #   models=['gpt-3.5-turbo-1106', 'text-bison-32k'],
  #   temperature=0.0,
  #   max_tokens=100,
  #   messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  # )

  outputs = airouter.StreamedCompletion.create_interactive(
    # models=['mixtral:8x7b'],
    models=[airouter.models.LLM.LLAMA2_13B],
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  )

  print(outputs)
