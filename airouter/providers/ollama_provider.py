import os
import time
from decouple import config
from airouter.providers.base_provider import BaseProvider, GenerationOutput
#
PROVIDER_CONFIGURED = False
#
try:
  import ollama
#   os.environ['OPENAI_API_KEY'] = config("OPENAI_API_KEY")
  OLLAMA_HOST = config("OLLAMA_HOST", None)
  PROVIDER_CONFIGURED = True
except:
  pass

class OllamaProvider(BaseProvider):
  def __init__(self, **kwargs):
    super(OllamaProvider, self).__init__(**kwargs)
    return

  def get_response(self):
    ollama_client = ollama.Client(host=OLLAMA_HOST)
    response = ollama_client.chat(
      **self.cleaned_parameters
    )
    # response = client.chat.completions.create(**self.cleaned_parameters)
    return response

  def get_generation_output(self, event) -> GenerationOutput:
    kwargs = {
      'content': event['message']['content'],
    }

    return GenerationOutput(**kwargs)

  # def get_timeout_params(self):
  #   return {
  #     'start': 5.0,
  #     'maximum': 20.0,
  #     'increment': 5.0,
  #   }

