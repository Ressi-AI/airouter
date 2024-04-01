import airouter
from airouter.models import LLM

if __name__ == '__main__':

    outputs = airouter.StreamedCompletion.create(
      model=f'azure_openai/{LLM.GPT_4_1106_PREVIEW}',
      temperature=0.0,
      max_tokens=100,
      messages=[
          {'role': 'system', 'content': 'You are a poet.'},
          {'role': 'user', 'content': 'write a story about the big Large Language Models convention'},
          {'role': 'assistant', 'content': "I don't want to ...."},
          {'role': 'user', 'content': "But pleaaaase....!!!"},
      ]
    )
