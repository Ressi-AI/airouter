import airouter

if __name__ == '__main__':
    outputs = airouter.StreamedCompletion.create_interactive(
      models=['gpt-3.5-turbo-1106', 'text-bison-32k'],
      temperature=0.0,
      # model='gpt-3.5-turbo-1106',
      max_tokens=100,
      messages=[{'role': 'user', 'content': 'what is Ebitda?'}]
    )
