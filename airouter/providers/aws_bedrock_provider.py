import json
import httpx
from airouter.providers.base_provider import BaseProvider, GenerationOutput
from airouter.models import map_context_size
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
  PROVIDER_CONFIGURED = True
except:
  pass

class AWSBedrockProvider(BaseProvider):
  def __init__(self, **kwargs):
    assert PROVIDER_CONFIGURED
    super(AWSBedrockProvider, self).__init__(**kwargs)
    if self.max_tokens is None:
      self.max_tokens = map_context_size[self.model]
    return

  @property
  def request_params(self):
    accept = "application/json"
    contentType = "application/json"
    modelId = self.model.value
    body = {
      'prompt': self.messages_to_prompt,
    }
    if self.max_tokens is not None:
      body['max_tokens_to_sample'] = self.max_tokens
    if self.temperature is not None:
      body['temperature'] = self.temperature

    return {
      'body': json.dumps(body),
      'modelId': modelId,
      'accept': accept,
      'contentType': contentType,
    }

  def get_response(self):
    aws_config = None
    if self.timeout is not None:
      if isinstance(self.timeout, float):
        self.timeout = httpx.Timeout(self.timeout)
      aws_config = Config(
        connect_timeout=self.timeout.connect,
        read_timeout=self.timeout.read,
        retries={'max_attempts': 0}
      )

    boto3_sess = boto3.Session(**BOTO3_KWARGS)
    boto3_bedrock = boto3_sess.client(
      service_name='bedrock-runtime',
      config=aws_config,
      **BOTO3_KWARGS
    )
    self._attrs['boto3_sess'] = boto3_sess
    self._attrs['boto3_bedrock'] = boto3_bedrock

    response = self._attrs['boto3_bedrock'].invoke_model_with_response_stream(**self.request_params)
    response = response.get('body')
    return response

  def get_generation_output(self, event) -> GenerationOutput:
    chunk = event.get('chunk')
    if chunk:
      chunk_obj = json.loads(chunk.get('bytes').decode())
      text = chunk_obj['completion']

      kwargs = {
        'content': text,
      }
      return GenerationOutput(**kwargs)

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
