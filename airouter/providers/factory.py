import typing as t
from airouter.models import ProviderName
from airouter.providers.base_provider import BaseProvider


def provider_factory(provider_name, **llm_params) -> t.Optional[BaseProvider]:
  if isinstance(provider_name, str):
    provider_name = ProviderName.from_str(provider_name)

  if provider_name == ProviderName.OPENAI:
    from airouter.providers.openai_provider import OpenAIProvider
    return OpenAIProvider(stream=True, **llm_params)

  if provider_name == ProviderName.AWS_BEDROCK:
    from airouter.providers.aws_bedrock_provider import AWSBedrockProvider
    return AWSBedrockProvider(stream=True, **llm_params)

  if provider_name == ProviderName.AWS_BEDROCK_CHAT:
    from airouter.providers.aws_bedrock_chat_provider import AWSBedrockChatProvider
    return AWSBedrockChatProvider(stream=True, **llm_params)

  if provider_name == ProviderName.VERTEX_AI_TEXT:
    from airouter.providers.vertex_ai_text_provider import VertexAITextProvider
    return VertexAITextProvider(stream=True, **llm_params)

  if provider_name == ProviderName.OLLAMA:
    from airouter.providers.ollama_provider import OllamaProvider
    return OllamaProvider(stream=True, **llm_params)

  if provider_name == ProviderName.AZURE_OPENAI:
    from airouter.providers.azure_openai_provider import AzureOpenAIProvider
    return AzureOpenAIProvider(stream=True, **llm_params)

  return
