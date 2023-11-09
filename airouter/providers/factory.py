import typing as t
from airouter.models import ProviderName
from airouter.providers.base_provider import BaseProvider
from airouter.providers.openai_provider import OpenAIProvider
from airouter.providers.aws_bedrock_provider import AWSBedrockProvider
from airouter.providers.vertex_ai_text_provider import VertexAITextProvider

def provider_factory(provider_name, **llm_params) -> t.Optional[BaseProvider]:
  if isinstance(provider_name, str):
    provider_name = ProviderName.from_str(provider_name)

  if provider_name == ProviderName.OPENAI:
    return OpenAIProvider(stream=True, **llm_params)

  if provider_name == ProviderName.AWS_BEDROCK:
    return AWSBedrockProvider(stream=True, **llm_params)

  if provider_name == ProviderName.VERTEX_AI_TEXT:
    return VertexAITextProvider(stream=True, **llm_params)

  return
