import os
from airouter.providers.base_provider import BaseProvider, GenerationOutput, LLM, map_context_size
from decouple import config

PROVIDER_CONFIGURED = False

try:
  import vertexai
  from vertexai.language_models import TextGenerationModel
  from vertexai.preview.language_models import TextGenerationModel as PreviewTextGenerationModel

  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config("GOOGLE_APPLICATION_CREDENTIALS")
  vertexai.init()
  PROVIDER_CONFIGURED = True
except:
  pass

class VertexAITextProvider(BaseProvider):

  def __init__(self, **kwargs):
    assert PROVIDER_CONFIGURED
    super(VertexAITextProvider, self).__init__(**kwargs)

    if self.model == LLM.PALM_TEXT_BISON_32K:
      vertex_class = PreviewTextGenerationModel
    else:
      vertex_class = TextGenerationModel

    self._attrs['text_generation_model'] = vertex_class.from_pretrained(self.model.value)
    if self.max_tokens is None:
      self.max_tokens = map_context_size[self.model]
    return

  @property
  def request_params(self):
    params = {"prompt": self.messages_to_prompt}

    if self.max_tokens is not None:
      params['max_output_tokens'] = self.max_tokens

    if self.temperature is not None:
      params['temperature'] = self.temperature

    return params

  def get_response(self):
    response = self._attrs['text_generation_model'].predict_streaming(**self.request_params)
    return response

  def get_generation_output(self, event) -> GenerationOutput:
    kwargs = {
      'content': event.text,
    }

    return GenerationOutput(**kwargs)

  def get_timeout_params(self):
    return {
      'start': 5.0,
      'maximum': 20.0,
      'increment': 5.0,
    }
