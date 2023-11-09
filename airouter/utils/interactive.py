import urwid
import queue
from functools import partial

class InteractiveCallbacks(object):
  palette = [
    ("model_name", "white", "light blue", "bold"),
    ("exit_btn", "white", "light red", "bold")
  ]

  def __init__(self, models):
    self.models = models
    _div = urwid.Divider()
    _button = urwid.Button(('exit_btn', 'Exit'))
    display_objects = []
    self.models_objects = {}
    self.queues = {
      'msg': {},
      'speed': {},
    }
    for model in models:
      header = urwid.Text(('model_name', model))
      scratchpad = urwid.Text("")
      self.models_objects[model] = {'header': header, 'scratchpad': scratchpad}
      for k in self.queues.keys():
        self.queues[k][model] = queue.Queue(maxsize=1)
      display_objects.extend([header, scratchpad, _div])
    #endfor

    display_objects.append(_button)

    _pile = urwid.Pile(display_objects)
    self.top = urwid.Filler(_pile, valign='top')
    self.loop = urwid.MainLoop(self.top, self.palette, unhandled_input=self.unhandled_input)
    self.check_messages(self.loop, None)

    urwid.connect_signal(_button, 'click', self.on_exit_clicked)
    return

  def unhandled_input(self, k):
      if k == 'esc':
          raise urwid.ExitMainLoop()

  def on_exit_clicked(self, btn):
    raise urwid.ExitMainLoop()

  def run(self):
    urwid.MainLoop(self.top, self.palette).run()
    return

  def on_msg_callback(self, executor, model):
    msg_queue = self.queues['msg'][model]
    speed_queue = self.queues['speed'][model]

    if executor.full_generation_output.content is not None:
      msg_queue.put(executor.full_generation_output.content)
    elif executor.full_generation_output.function_call is not None:
      header = f"Function {executor.full_generation_output.function_call.name}"
      arguments = executor.full_generation_output.function_call.arguments
      header_dashes = "-" * len(header)
      msg_queue.put(header + "\n" + header_dashes + "\n" + arguments)

    speed_queue.put(executor.provider.timings['speed'])
    return

  def check_messages(self, loop, *_args):
    """add message to bottom of screen"""
    loop.set_alarm_in(
      sec=0.1,
      callback=self.check_messages,
    )

    for model in self.models:
      try:
        msg = self.queues['msg'][model].get_nowait()
      except queue.Empty:
        msg = None

      try:
        speed = self.queues['speed'][model].get_nowait()
      except queue.Empty:
        speed = None

      if msg is not None:
        scratchpad = self.models_objects[model]['scratchpad']
        scratchpad.set_text(msg)
      #endif

      if speed is not None:
        header = self.models_objects[model]['header']
        header.set_text(('model_name', f"{model} ({speed:.1f}) chars/s"))
      #endif
    #endfor

    return

def enable_interactiveness(lst_kwargs):
  models = [kwargs['model'] for kwargs in lst_kwargs]
  interactive_obj = InteractiveCallbacks(models=models)
  for i in range(len(lst_kwargs)):
    kwargs = lst_kwargs[i]
    model = kwargs['model']
    on_first_chunk_callback = partial(interactive_obj.on_msg_callback, model=model)
    on_new_chunk_callback = partial(interactive_obj.on_msg_callback, model=model)
    on_stop_generation_callback = partial(interactive_obj.on_msg_callback, model=model)
    kwargs['on_first_chunk_callback'] = on_first_chunk_callback
    kwargs['on_new_chunk_callback'] = on_new_chunk_callback
    kwargs['on_stop_generation_callback'] = on_stop_generation_callback
    kwargs['verbose'] = False
  #endfor
  return interactive_obj, lst_kwargs