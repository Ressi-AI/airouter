import os
import decouple
from airouter.providers.openai_provider import OpenAIProvider

PROVIDER_CONFIGURED = False

try:
  import openai
  os.environ['AZURE_OPENAI_ENDPOINT'] = decouple.config("AZURE_OPENAI_ENDPOINT")
  os.environ['AZURE_OPENAI_API_KEY'] = decouple.config("AZURE_OPENAI_API_KEY")
  os.environ['AZURE_OPENAI_API_VERSION'] = decouple.config("OPENAI_API_VERSION", default="2023-09-01-preview") or \
                                           decouple.config("AZURE_OPENAI_API_VERSION", default="2023-09-01-preview")
  PROVIDER_CONFIGURED = True
except:
  pass


class AzureOpenAIProvider(OpenAIProvider):
  def __init__(self, **kwargs):
    super(OpenAIProvider, self).__init__(**kwargs)
    return

  @property
  def openai_client(self):
    return openai.AzureOpenAI(api_version=os.environ['AZURE_OPENAI_API_VERSION'])
