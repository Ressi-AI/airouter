import os
import time
from decouple import config
from airouter.providers.base_provider import BaseProvider, GenerationOutput
#
PROVIDER_CONFIGURED = False
#
try:
  import ollama
  OLLAMA_HOST = config("OLLAMA_HOST", None)
  PROVIDER_CONFIGURED = True
except:
  pass

class OllamaProvider(BaseProvider):
  def __init__(self, **kwargs):
    super(OllamaProvider, self).__init__(**kwargs)
    return

  @property
  def request_params(self):
    params = {
      "model": self.cleaned_parameters['model'],
      "stream": self.cleaned_parameters['stream'],
      "messages": self.cleaned_parameters['messages'],
      "options": {}
    }

    if self.temperature is not None:
      params["options"]["temperature"] = self.temperature
    if self.max_tokens is not None:
      params["options"]["num_predict"] = self.max_tokens

    return params

  def get_response(self):
    ollama_client = ollama.Client(host=OLLAMA_HOST)
    response = ollama_client.chat(
      # **self.cleaned_parameters
      **self.request_params
    )
    return response

  def get_generation_output(self, event) -> GenerationOutput:
    kwargs = {
      'content': event['message']['content'],
    }

    return GenerationOutput(**kwargs)

