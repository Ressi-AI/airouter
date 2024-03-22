import abc
import typing as t
import json
import time
import statistics
import numpy as np
import httpx
from pydantic import BaseModel, Extra
from airouter.models import (
  LLM, Messages, Functions, map_context_size, map_role_for_prompt,
  ChatRole, GenerationOutput,
)



class Schema(BaseModel):
  model: LLM
  messages: Messages
  max_tokens: t.Optional[int] = None
  temperature: t.Optional[float] = None
  functions: t.Optional[Functions] = None
  n: t.Optional[int] = None
  top_p: t.Optional[float] = None
  frequence_penalty: t.Optional[float] = None
  presence_penalty: t.Optional[float] = None
  stop: t.Optional[t.Union[str, t.List[str]]] = None
  user: t.Optional[str] = None

  timeout: t.Optional[float | httpx.Timeout] = None

  class Config:
    arbitrary_types_allowed = True


def basic_statistics(lst):
  if len(lst) == 0:
    return {
      'min': np.nan, 'max': np.nan,
      'avg': np.nan, 'median': np.nan,
    }

  try:
    max_value = max(lst)
  except:
    max_value = np.nan

  try:
    min_value = min(lst)
  except:
    min_value = np.nan

  try:
    avg_value = statistics.mean(lst)
  except:
    avg_value = np.nan

  try:
    median_value = statistics.median(lst)
  except:
    median_value = np.nan

  return {
    'min': min_value, 'max': max_value,
    'avg': avg_value, 'median': median_value,
  }


def _default_timings():
  return {
    'response_time': np.nan,
    'first_event_time': np.nan,
    'next_events_times': [],
    'execution_time': np.nan,
    'speed': np.nan, # chars per second
  }


class BaseProvider(Schema, extra=Extra.allow, arbitrary_types_allowed=True):
  _attrs = {
    'parameters': {},
    'timings': _default_timings(),
    'last_exception': None,
  }

  def __init__(self, **kwargs):
    super(BaseProvider, self).__init__(**kwargs)
    self.clean_parameters()
    return

  @property
  def last_exception(self):
    return self._attrs['last_exception']

  @last_exception.setter
  def last_exception(self, exc):
    self._attrs['last_exception'] = exc

  def clean_parameters(self):
    self._attrs['parameters'] = self.model_dump(exclude={'_attrs', 'retry'})
    keys = list(self._attrs['parameters'].keys())
    for k in keys:
      if self._attrs['parameters'][k] is None:
        self._attrs['parameters'].pop(k)
      elif isinstance(self._attrs['parameters'][k], httpx.Timeout):
        timeout = self._attrs['parameters'][k]
        if timeout.read is None and timeout.connect is None and timeout.write is None and timeout.pool is None:
          self._attrs['parameters'].pop(k)
    return

  def refresh_timings(self):
    self._attrs['timings'] = _default_timings()
    return

  def set_response_time(self, nr_seconds):
    self._attrs['timings']['response_time'] = nr_seconds
    return

  def set_first_event_time(self, nr_seconds):
    self._attrs['timings']['first_event_time'] = nr_seconds
    return

  def append_next_event_time(self, nr_seconds):
    self._attrs['timings']['next_events_times'].append(nr_seconds)
    return

  def set_execution_time(self, nr_seconds):
    self._attrs['timings']['execution_time'] = nr_seconds
    return

  def set_speed(self, speed):
    self._attrs['timings']['speed'] = speed

  @property
  def timings(self):
    timings = self._attrs['timings']
    next_events_times = timings['next_events_times']
    stats1 = basic_statistics(next_events_times)
    timings['next_event_time'] = stats1
    return timings

  def get_str_timings(self):
    timings = self.timings
    s = ""
    s += f"Response time: {timings['response_time']:.3f}s\n"
    s += f"First event time: {timings['first_event_time']:.3f}s\n"
    s += (
        f"Next event time: "
        f"min={timings['next_event_time']['min']:.3f}s | "
        f"avg={timings['next_event_time']['avg']:.3f}s | "
        f"median={timings['next_event_time']['median']:.3f}s | "
        f"max={timings['next_event_time']['max']:.3f}s\n"
    )
    s += f"Execution time: {timings['execution_time']:.3f}s\n"
    s += f"Speed: {timings['speed']:.1f} chars/s\n"
    return s

  @property
  def cleaned_parameters(self):
    return self._attrs['parameters']

  @property
  def messages_to_prompt(self):
    prompt = ""
    for m in self.messages:
      prefix = map_role_for_prompt[m.role]
      prompt += f"{prefix}: {m.content}\n\n"

    prompt += f"{map_role_for_prompt[ChatRole.ASSISTANT]}:\n"
    return prompt

  @property
  def prompt_nr_characters(self):
    return len(self.messages_to_prompt)

  def get_stream(self):
    start = time.time()
    # TODO response could be none??
    response = self.get_response()
    end = time.time()

    self.set_response_time(end-start)

    i = -1
    start = time.time()
    for event in response:
      # TODO event can be None??
      i += 1
      end = time.time()
      if i == 0:
        self.set_first_event_time(end-start)
      else:
        self.append_next_event_time(end-start)
      start = time.time()
      yield i,event

  @abc.abstractmethod
  def get_response(self) -> t.Any:
    pass

  @abc.abstractmethod
  def get_generation_output(self, event) -> GenerationOutput:
    pass

  def get_timeout_params(self):
    return
