import typing as t
from pydantic import BaseModel
from enum import Enum

class ChatRole(str, Enum):
  SYSTEM = "system"
  USER = "user"
  ASSISTANT = "assistant"

class ProviderName(str, Enum):
  OPENAI = "openai",
  VERTEX_AI_TEXT = "vertex_ai_text"
  AWS_BEDROCK = "aws_bedrock"

  @classmethod
  def from_str(cls, value):
    for item in cls:
      if item.value == value:
        return item
    raise ValueError(f"{value} is not a valid Provider")

class LLM(str, Enum):
  GPT_3_5_TURBO = "gpt-3.5-turbo"
  GPT_3_5_TURBO_0301 = "gpt-3.5-turbo-0301"
  GPT_3_5_TURBO_0613 = "gpt-3.5-turbo-0613"

  GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
  GPT_3_5_TURBO_16K_0613 = "gpt-3.5-turbo-16k-0613"

  GPT_3_5_TURBO_1106 = "gpt-3.5-turbo-1106" # default 16K

  GPT_4 = "gpt-4"
  GPT_4_0613 = "gpt-4-0613"

  GPT_4_32K = "gpt-4-32k"
  GPT_4_32K_0613 = "gpt-4-32k-0613"

  GPT_4_1106_PREVIEW = "gpt-4-1106-preview" # 128K

  ANTROPHIC_CLAUDE_INSTANT_V1 = "anthropic.claude-instant-v1"
  ANTROPHIC_CLAUDE_V2 = "anthropic.claude-v2"

  PALM_TEXT_BISON_32K = "text-bison-32k"

  @classmethod
  def from_str(cls, value):
    for item in cls:
      if item.value == value:
        return item
    raise ValueError(f"{value} is not a valid LLM")

def process_llm(llm: t.Union[str, LLM]) -> t.Tuple[ProviderName, LLM]:
  provider_name = None
  if isinstance(llm, str):
    str_llm = llm
    if "/" in str_llm:
      str_provider_name, str_llm = str_llm.split("/")
      provider_name = ProviderName.from_str(str_provider_name)

    llm = LLM.from_str(str_llm)
  #endif

  infered_provider_name = map_llm_to_provider[llm]
  if provider_name is not None and infered_provider_name != provider_name:
    print("Warning!")

  return infered_provider_name, llm


def get_provider_llms(provider_name: t.Union[str, ProviderName]):
  if isinstance(provider_name, str):
    provider_name = ProviderName.from_str(provider_name)

  if provider_name not in map_provider_to_llms:
    raise ValueError(f"Unknown provider {provider_name}")

  return map_provider_to_llms[provider_name]

def get_llm_context_size(llm: t.Union[str, LLM]):
  _, llm = process_llm(llm)
  if llm not in map_context_size:
    raise ValueError(f"Unknown LLM {llm}")

  return map_context_size[llm]

class ChatMessage(BaseModel):
  role: ChatRole
  content: str

class Function(BaseModel):
  name: str
  parameters: t.Optional[t.Dict] = None
  description: t.Optional[str] = None

class FunctionCall(BaseModel):
  name: t.Optional[str] = None
  arguments: t.Optional[str] = None

class Usage(BaseModel):
  prompt_tokens: t.Optional[int] = None
  completion_tokens: t.Optional[int] = None
  total_tokens: t.Optional[int] = None

class GenerationOutput(BaseModel):
  finish_reason: t.Optional[str] = None
  content: t.Optional[str] = None
  function_call: t.Optional[FunctionCall] = None
  usage: t.Optional[Usage] = None

Messages = t.List[ChatMessage]
Functions = t.List[Function]

# mappings
if True:
  map_llm_pointers = {
    LLM.GPT_3_5_TURBO: LLM.GPT_3_5_TURBO_0613,
    LLM.GPT_3_5_TURBO_16K: LLM.GPT_3_5_TURBO_16K_0613,
    LLM.GPT_4: LLM.GPT_4_0613,
    LLM.GPT_4_32K: LLM.GPT_4_32K_0613,
  }

  map_provider_to_llms = {
    ProviderName.OPENAI: [
      LLM.GPT_3_5_TURBO,
      LLM.GPT_3_5_TURBO_0301,
      LLM.GPT_3_5_TURBO_0613,

      LLM.GPT_3_5_TURBO_16K,
      LLM.GPT_3_5_TURBO_16K_0613,

      LLM.GPT_3_5_TURBO_1106,

      LLM.GPT_4,
      LLM.GPT_4_0613,

      LLM.GPT_4_32K,
      LLM.GPT_4_32K_0613,

      LLM.GPT_4_1106_PREVIEW,
    ],
    ProviderName.AWS_BEDROCK: [
      LLM.ANTROPHIC_CLAUDE_INSTANT_V1,
      LLM.ANTROPHIC_CLAUDE_V2,
    ],
    ProviderName.VERTEX_AI_TEXT: [
      LLM.PALM_TEXT_BISON_32K,
    ]
  }

  map_llm_to_provider = {llm: p for p, llms in map_provider_to_llms.items() for llm in llms}

  map_context_size = {
    LLM.GPT_3_5_TURBO: 4_096,
    LLM.GPT_3_5_TURBO_0301: 4_096,
    LLM.GPT_3_5_TURBO_0613: 4_096,

    LLM.GPT_3_5_TURBO_16K: 16_385,
    LLM.GPT_3_5_TURBO_16K_0613: 16_385,

    LLM.GPT_3_5_TURBO_1106: 16_385,

    LLM.GPT_4: 8_192,
    LLM.GPT_4_0613: 8_192,

    LLM.GPT_4_32K: 32_768,
    LLM.GPT_4_32K_0613: 32_768,

    LLM.GPT_4_1106_PREVIEW: 128_000,

    LLM.ANTROPHIC_CLAUDE_INSTANT_V1: 100_000,
    LLM.ANTROPHIC_CLAUDE_V2: 100_000,

    LLM.PALM_TEXT_BISON_32K: 32_000,
  }

  map_role_for_prompt = {
    ChatRole.SYSTEM: "System",
    ChatRole.USER: "Human",
    ChatRole.ASSISTANT: "Assistant"
  }
