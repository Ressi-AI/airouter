import airouter

if __name__ == '__main__':
  outputs = airouter.StreamedCompletion.create(
    model='azure_openai/gpt-3.5-turbo-1106',
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}],
  )
  # print(outputs)
  # for o in outputs:
  #   print(o)

