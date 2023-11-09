import os
import time
from decouple import config
from airouter.providers.base_provider import BaseProvider, GenerationOutput

PROVIDER_CONFIGURED = False

try:
  import openai
  os.environ['OPENAI_API_KEY'] = config("OPENAI_API_KEY")
  PROVIDER_CONFIGURED = True
except:
  pass

class OpenAIProvider(BaseProvider):
  def __init__(self, **kwargs):
    super(OpenAIProvider, self).__init__(**kwargs)
    return

  def get_response(self):
    client = openai.OpenAI()
    if isinstance(self.last_exception, openai.RateLimitError):
      sleep_before = 20.0
      print(f"Sleeping {sleep_before}s before making the LLM call")
      time.sleep(sleep_before)
    response = client.chat.completions.create(**self.cleaned_parameters)
    return response

  def get_generation_output(self, event) -> GenerationOutput:
    choice = event.choices[0]
    crt_content = choice.delta.content
    crt_function_call = choice.delta.function_call

    if crt_function_call is not None:
      crt_function_call = {'name': crt_function_call.name, 'arguments': crt_function_call.arguments}

    kwargs = {
      'finish_reason': choice.finish_reason,
      'content': crt_content,
      'function_call': crt_function_call,
    }

    return GenerationOutput(**kwargs)

  def get_timeout_params(self):
    return {
      'start': 5.0,
      'maximum': 20.0,
      'increment': 5.0,
    }
