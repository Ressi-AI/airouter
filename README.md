# AI Router

```
pip install airouter
```

```python 
import airouter

outputs = airouter.StreamedCompletion.create(
    model='gpt-3.5-turbo-1106',
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
)
```

```python 
import airouter

outputs = airouter.StreamedCompletion.create(
    model='text-bison-32k',
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
)
```

```python 
import airouter

outputs = airouter.StreamedCompletion.create(
    models=['gpt-3.5-turbo-1106', 'text-bison-32k'],
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
)
```

```python 
import airouter

outputs = airouter.StreamedCompletion.create_interactive(
    models=['gpt-3.5-turbo-1106', 'text-bison-32k'],
    temperature=0.0,
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'write a story about the big Large Language Models convention'}]
)
```
