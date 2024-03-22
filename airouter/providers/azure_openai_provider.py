import os
from decouple import config
from airouter.providers.openai_provider import OpenAIProvider

PROVIDER_CONFIGURED = False

try:
  import openai
  os.environ['AZURE_OPENAI_ENDPOINT'] = config("AZURE_OPENAI_ENDPOINT")
  os.environ['AZURE_OPENAI_API_KEY'] = config("AZURE_OPENAI_API_KEY")
  os.environ['OPENAI_API_VERSION'] = config("OPENAI_API_VERSION", "2023-09-01-preview")
  PROVIDER_CONFIGURED = True
except:
  pass

class AzureOpenAIProvider(OpenAIProvider):
  def __init__(self, **kwargs):
    super(OpenAIProvider, self).__init__(**kwargs)
    return

  @property
  def openai_client(self):
    return openai.AzureOpenAI(api_version=os.environ['OPENAI_API_VERSION'])
