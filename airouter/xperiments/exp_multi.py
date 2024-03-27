import airouter
airouter.models.LLM.GPT_4_1106_PREVIEW

import tiktoken

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

  enc = tiktoken.get_encoding('cl100k_base')

  _callback = lambda self: print(self.full_generation_output.content)

  outputs = airouter.StreamedCompletion.create(
    # models=['mixtral:8x7b'],
    # models=[airouter.models.LLM.MIXTRAL],
    on_first_chunk_callback=_callback,
    on_new_chunk_callback=_callback,
    models=[airouter.models.LLM.LLAMA2],
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write all numbers from 0 to 10000, or as many as you can fill in this text box. do not show me code to generate them'}]
  )
  print("processing done")
  print(outputs)
  print(len(enc.encode(outputs[0].content)))
