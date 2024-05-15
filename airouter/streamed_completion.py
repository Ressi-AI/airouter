import logging
import typing as t
import uuid
import time
import httpx
import concurrent.futures
from tenacity import (
  after_log,
  retry,
  stop_after_attempt,
  wait_exponential,
)
from airouter.providers.base_provider import BaseProvider
from airouter.models import (
  GenerationOutput, FunctionCall,
  process_llm, LLM,
)
import airouter
from airouter.utils.interactive import enable_interactiveness
from airouter.providers.factory import provider_factory

SingleCreateOutput = t.Union[GenerationOutput, t.Tuple[t.Any, GenerationOutput]]
MultipleCreateOutputs = t.List[SingleCreateOutput]


class StreamedCompletion(object):
  def __init__(
      self,
      logger=None,
      call_name: t.Optional[str] = None,
      completion_timeout: t.Optional[int] = None,
      request_timeout_start: t.Optional[float] = None,
      request_timeout_max: t.Optional[float] = None,
      request_timeout_increment: t.Optional[float] = None,
      on_first_chunk_callback: t.Optional[t.Callable] = None,
      on_new_chunk_callback: t.Optional[t.Callable] = None,
      on_stop_generation_callback: t.Optional[t.Callable] = None,
      verbose: t.Optional[bool] = True,
      **llm_params
  ):
    self.logger = logger or airouter.logger

    model = llm_params.get('model')
    if model is None:
      raise ValueError("model cannot be None")

    self.provider_name, self.llm = process_llm(model)
    llm_params['model'] = self.llm

    self.completion_timeout = completion_timeout
    self.request_timeout_start = request_timeout_start
    self.request_timeout_max = request_timeout_max
    self.request_timeout_increment = request_timeout_increment
    self.on_first_chunk_callback = on_first_chunk_callback
    self.on_new_chunk_callback = on_new_chunk_callback
    self.on_stop_generation_callback = on_stop_generation_callback
    self.verbose = verbose

    self.full_generation_output: t.Optional[GenerationOutput] = None
    self.step_generation_output: t.Optional[GenerationOutput] = None

    self._attrs: t.Dict = {}
    self._attrs['call_id'] = call_name or str(uuid.uuid4())
    self._attrs['start_time'] = time.time()
    self._attrs['llm_params'] = llm_params
    self._attrs['provider'] = provider_factory(provider_name=self.provider_name, **self.llm_params)
    return

  @property
  def llm_params(self):
    return self._attrs.get('llm_params')

  @property
  def call_id(self):
    return self._attrs.get('call_id')

  @property
  def start_time(self):
    return self._attrs.get('start_time')

  @property
  def provider(self) -> t.Optional[BaseProvider]:
    return self._attrs.get('provider')

  @classmethod
  def _create_parallel(cls, lst_kwargs, interactive=False):
    interactive_obj = None
    if interactive:
      interactive_obj, lst_kwargs = enable_interactiveness(lst_kwargs)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(lst_kwargs)) as executor:
      # Submit each task with its own set of parameters
      futures = [executor.submit(StreamedCompletion.create, **params) for params in lst_kwargs]

      if interactive_obj is not None:
        interactive_obj.loop.run()

      # Wait for all threads to finish
      concurrent.futures.wait(futures)

      # Retrieve the results from each thread
      outputs = [future.result() for future in futures]
    #endwith
    return outputs

  @classmethod
  def create_parallel(cls, lst_kwargs):
    return StreamedCompletion._create_parallel(lst_kwargs, interactive=False)

  @classmethod
  def create_parallel_interactive(cls, lst_kwargs):
    return StreamedCompletion._create_parallel(lst_kwargs, interactive=True)

  @classmethod
  def generate(
      cls,
      call_name: t.Optional[str] = None,
      completion_timeout: t.Optional[int] = None,
      request_timeout_start: t.Optional[float] = None,
      request_timeout_max: t.Optional[float] = None,
      request_timeout_increment: t.Optional[float] = None,
      on_first_chunk_callback: t.Optional[t.Callable] = None,
      on_new_chunk_callback: t.Optional[t.Callable] = None,
      on_stop_generation_callback: t.Optional[t.Callable] = None,
      verbose: t.Optional[bool] = True,
      **llm_params
  ):
    completion = cls(
      call_name=call_name,
      completion_timeout=completion_timeout,
      request_timeout_start=request_timeout_start,
      request_timeout_max=request_timeout_max,
      request_timeout_increment=request_timeout_increment,
      on_first_chunk_callback=on_first_chunk_callback,
      on_new_chunk_callback=on_new_chunk_callback,
      on_stop_generation_callback=on_stop_generation_callback,
      verbose=verbose,
      **llm_params,
    )

    return completion.generator()

  @classmethod
  def create(
      cls,
      logger=None,
      call_name: t.Optional[str] = None,
      completion_timeout: t.Optional[int] = None,
      request_timeout_start: t.Optional[float] = None,
      request_timeout_max: t.Optional[float] = None,
      request_timeout_increment: t.Optional[float] = None,
      on_first_chunk_callback: t.Optional[t.Callable] = None,
      on_new_chunk_callback: t.Optional[t.Callable] = None,
      on_stop_generation_callback: t.Optional[t.Callable] = None,
      return_instance: t.Optional[bool] = False,
      verbose: t.Optional[bool] = True,
      models: t.Optional[t.List[str | LLM]] = None,
      **llm_params
  ) -> t.Union[SingleCreateOutput, MultipleCreateOutputs]:

    base_kwargs = dict(
      logger=logger,
      call_name=call_name,
      completion_timeout=completion_timeout,
      request_timeout_start=request_timeout_start,
      request_timeout_max=request_timeout_max,
      request_timeout_increment=request_timeout_increment,
      on_first_chunk_callback=on_first_chunk_callback,
      on_new_chunk_callback=on_new_chunk_callback,
      on_stop_generation_callback=on_stop_generation_callback,
      return_instance=return_instance,
      verbose=verbose,
      **llm_params,
    )

    if models is not None:
      lst_kwargs = []
      if not isinstance(models, list):
        models = [models]
      for m in models:
        crt_kwargs = base_kwargs.copy()
        crt_kwargs['model'] = m
        lst_kwargs.append(crt_kwargs)

      return StreamedCompletion.create_parallel(lst_kwargs)
    #endif

    completion = cls(
      logger=logger,
      call_name=call_name,
      completion_timeout=completion_timeout,
      request_timeout_start=request_timeout_start,
      request_timeout_max=request_timeout_max,
      request_timeout_increment=request_timeout_increment,
      on_first_chunk_callback=on_first_chunk_callback,
      on_new_chunk_callback=on_new_chunk_callback,
      on_stop_generation_callback=on_stop_generation_callback,
      verbose=verbose,
      **llm_params,
    )

    output = completion.run()
    completion.log_info(f"Timings for call id `{completion.call_id}`\n{completion.provider.get_str_timings()}")

    if return_instance:
      result = completion, output
    else:
      result = output

    return result

  @classmethod
  def create_interactive(cls, models: t.Optional[t.List[str | LLM]] = None, **kwargs):
    if models is not None:
      lst_kwargs = []
      if not isinstance(models, list):
        models = [models]
      for m in models:
        crt_kwargs = kwargs.copy()
        crt_kwargs['model'] = m
        lst_kwargs.append(crt_kwargs)

      return StreamedCompletion.create_parallel_interactive(lst_kwargs)
    else:
      outputs = StreamedCompletion.create_parallel_interactive([kwargs])
      return outputs

  def _should_stop_prematurely(self) -> bool:
    if self.completion_timeout is None:
      return False

    elapsed = time.time() - self.start_time
    stop = elapsed >= self.completion_timeout
    if stop:
      self.log_info(f"Call id {self.call_id} should stop prematurely. Elapsed {elapsed:.1f}s")
    return stop

  @staticmethod
  def compute_request_timeout(
      start,
      maximum,
      attempt_number,
      increment: t.Optional[float] = 1,
  ):

    if any([x is None for x in [start, maximum, attempt_number, increment]]):
      return

    result = start + (increment * (attempt_number - 1))
    return max(0, min(result, maximum))

  def _provider_stream(self, func):
    request_timeout_params = self.provider.get_timeout_params() or {}
    request_timeout = self.compute_request_timeout(
      attempt_number=func.retry.statistics.get('attempt_number', 1),
      start=self.request_timeout_start or request_timeout_params.get('start'),
      maximum=self.request_timeout_max or request_timeout_params.get('maximum'),
      increment=self.request_timeout_increment or request_timeout_params.get('increment'),
    )

    self.provider.timeout = httpx.Timeout(request_timeout)
    self.provider.clean_parameters()
    self.provider.refresh_timings()

    try:
      gen_events = self.provider.get_stream()
      return gen_events
    except Exception as e:
      self.provider.last_exception = e
      self.logger.error(f"Exception of type '{type(e)}' for `get_stream`: {e}")
      raise e

  def _handle_stream_step(self, i, event, start):
    self.step_generation_output = self.provider.get_generation_output(event)
    elapsed = time.time() - start
    finished = self.step_generation_output.finish_reason is not None
    crt_content = self.step_generation_output.content
    crt_function_call = self.step_generation_output.function_call

    self.full_generation_output.finish_reason = self.full_generation_output.finish_reason or self.step_generation_output.finish_reason

    first_response = self.full_generation_output.content is None and self.full_generation_output.function_call is None

    if crt_content is not None:
      if first_response:
        self.full_generation_output.content = ""
      self.full_generation_output.content += crt_content

      self.provider.set_speed(len(self.full_generation_output.content) / elapsed)

      if first_response and self.on_first_chunk_callback is not None:
        self.on_first_chunk_callback(self)

      if not first_response and self.on_new_chunk_callback is not None:
        res = self.on_new_chunk_callback(self)
        if res:
          return 'break'

    elif crt_function_call is not None:
      if first_response:
        self.full_generation_output.function_call = FunctionCall(name=crt_function_call.name, arguments='')
      self.full_generation_output.function_call.arguments += (crt_function_call.arguments or '')
      self.provider.set_speed(len(self.full_generation_output.function_call.arguments) / elapsed)
    #endif

    if self._should_stop_prematurely() and not finished:
      # do not stop prematurely if it's exactly the last chunk
      return 'return'

    return

  @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    after=after_log(airouter.logger, logging.INFO),
    retry_error_callback=lambda retry_state: None,
  )
  def _streamed_request_with_retry(self) -> t.Optional[GenerationOutput]:
    if self._should_stop_prematurely():
      return

    gen_events = self._provider_stream(func=self._streamed_request_with_retry)
    self.full_generation_output = GenerationOutput()

    start = time.time()
    last_event = time.time()

    try:
      for i, event in gen_events:
        last_event = time.time()
        r = self._handle_stream_step(i, event, start)
        if r == 'break':
          break
        elif r == 'return':
          return
      #endfor
    except Exception as e:
      elapsed_from_last_event = time.time() - last_event
      self.provider.last_exception = e
      self.logger.error(
        f"Exception of type '{type(e)}': {e}. Elapsed from last event: {elapsed_from_last_event:.2f}s. Managed to generate until now: {self.full_generation_output.content}"
      )
      raise e

    if self.full_generation_output.content is not None:
      self.full_generation_output.content = self.full_generation_output.content.strip('\n')

    if self.on_stop_generation_callback is not None:
      self.on_stop_generation_callback(self)

    self.provider.set_execution_time(time.time() - start)
    return self.full_generation_output

  @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    after=after_log(airouter.logger, logging.INFO),
    retry_error_callback=lambda retry_state: None,
  )
  def generator(self):
    self.log_info(f"Start generator call id `{self.call_id}` (provider={self.provider_name}, llm={self.llm})")
    if self._should_stop_prematurely():
      return

    gen_events = self._provider_stream(func=self.generator)
    self.full_generation_output = GenerationOutput()

    try:
      start = time.time()
      for i, event in gen_events:
        r = self._handle_stream_step(i, event, start)
        if r == 'break':
          break
        elif r == 'return':
          return
        if self.step_generation_output.content is not None:
          yield self.step_generation_output.content
      #endfor
    except Exception as e:
      self.provider.last_exception = e
      self.logger.error(f"Exception of type '{type(e)}': {e}")
      raise e

    self.log_info(f"End generator call id `{self.call_id}` (provider={self.provider_name}, llm={self.llm})")
    return

  def run(self):
    self.log_info(f"Start call id `{self.call_id}` (provider={self.provider_name}, llm={self.llm})")
    output = self._streamed_request_with_retry()

    if output is None:
      self.log_info(f"End call id `{self.call_id}` (provider={self.provider_name}, llm={self.llm})")
      return

    # output['usage'] = {'prompt_tokens': -1, 'completion_tokens': -1, 'total_tokens': -1}
    # if compute_usage:
    #   # in stream mode the usage is no more provided and it should be computed using tiktoken
    #   # TODO this computation does not take into account the functions!
    #   try:
    #     output['usage']['prompt_tokens'] = num_tokens_from_messages(
    #       messages=messages, model=self._model.value, encoding=tokenizer
    #     )
    #     output['usage']['completion_tokens'] = num_tokens_from_messages(
    #       messages=[{'role': 'assistant', 'content': output['content']}],
    #       model=self._model.value,
    #       encoding=tokenizer
    #     )
    #     output['usage']['total'] = output['usage']['prompt_tokens'] + output['usage']['completion_tokens']
    #   except Exception as e:
    #     airouter.logger.error("Could not compute tokens", exc_info=True)
    # # endif

    self.log_info(f"End call id `{self.call_id}` (provider={self.provider_name}, llm={self.llm})")
    return output

  def log_info(self, msg):
    if self.verbose:
      self.logger.info(msg)

  def log_warning(self, msg):
    if self.verbose:
      self.logger.warning(msg)
