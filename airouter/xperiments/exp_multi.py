import airouter
airouter.models.LLM.GPT_4_1106_PREVIEW

if __name__ == '__main__':
  # outputs = airouter.StreamedCompletion.create(
  #   model='azure_openai/gpt-4-1106-preview',
  #   temperature=0.0,
  #   max_tokens=100,
  #   messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  # )

  # outputs = airouter.StreamedCompletion.create_interactive(
  #   # models=['mixtral:8x7b'],
  #   models=[airouter.models.LLM.MIXTRAL],
  #   messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
  # )


  outputs = airouter.StreamedCompletion.create(
    # models=['mixtral:8x7b'],
    # models=[airouter.models.LLM.MIXTRAL],
    models=[airouter.models.LLM.LLAMA2],
    temperature=0.0,
    max_tokens=3000,
    messages=[{'role': 'user', 'content': 'write all numbers from 0 to 10000, or as many as you can fill in this text box. do not show me code to generate them'}]
  )
  print("processing done")
  print(outputs)
  print(len(outputs[0].content))
