from airouter.streamed_completion import StreamedCompletion
from airouter.models import LLM
import httpx

if __name__ == '__main__':

    import pickle
    with open("/Users/laurentiupiciu/Desktop/goldslate.pickle", "rb") as fh:
        messages = pickle.load(fh)

    output = StreamedCompletion.create(
        model=LLM.GPT_3_5_TURBO_1106,
        messages=messages,
        temperature=0,
        max_tokens=4096,
        request_timeout_start=25,
        request_timeout_increment=25,
        request_timeout_max=50,
    )
