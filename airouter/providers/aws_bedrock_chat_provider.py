import json
import httpx
from airouter.providers.base_provider import BaseProvider, GenerationOutput
from airouter.models import map_context_size
from airouter.providers.aws_bedrock_provider import AWSBedrockProvider
from decouple import config

PROVIDER_CONFIGURED = False

try:
  import boto3
  from botocore.client import Config

  BOTO3_KWARGS = dict(
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
    region_name=config("AWS_DEFAULT_REGION"),
  )
  ANTROPHIC_VERSION = config("ANTROPHIC_VERSION", default=None)
  PROVIDER_CONFIGURED = True
except:
  pass


class AWSBedrockChatProvider(AWSBedrockProvider):
  @property
  def request_params(self):
    accept = "application/json"
    contentType = "application/json"
    modelId = self.model.value
    body = {
      'messages': self.messages_dump,
    }
    if self.max_tokens is not None:
      body['max_tokens'] = self.max_tokens
    if self.temperature is not None:
      body['temperature'] = self.temperature

    if ANTROPHIC_VERSION is not None:
        body['anthropic_version'] = ANTROPHIC_VERSION

    return {
      'body': json.dumps(body),
      'modelId': modelId,
      'accept': accept,
      'contentType': contentType,
    }

  def get_generation_output(self, event) -> GenerationOutput:
    chunk = event.get('chunk')
    if chunk:
      chunk_obj = json.loads(chunk.get('bytes').decode())
      chunk_type = chunk_obj.get('type')
      if chunk_type not in ['content_block_delta', 'message_delta']:
        return GenerationOutput()

      if chunk_type == 'content_block_delta':
        text = chunk_obj['delta']['text']
        return GenerationOutput(content=text)

      elif chunk_type == 'message_delta':
        stop_reason = chunk_obj['delta']['stop_reason']
        return GenerationOutput(finish_reason=stop_reason)

    return GenerationOutput()

  def get_timeout_params(self):
    prompt_size = self.prompt_nr_characters
    if prompt_size <= 10_000:
      return {
        'start': 5.0,
        'maximum': 20.0,
        'increment': 5.0,
      }
    elif prompt_size <= 50_000:
      return {
        'start': 20.0,
        'maximum': 60.0,
        'increment': 20.0,
      }
    else:
      return {
        'start': 100.0,
        'maximum': 150.0,
        'increment': 20.0,
      }
