Supports OpenAI GPT, Google Gemini, Anthropic Claude and xAI Grok APIs

To install:

```shell
pip install gpt-token-tracker
```

Examples:
```python
from gpt_token_tracker.token_logger import TokenLogger
from gpt_token_tracker.writers.log_writer import LogWriter
from gpt_token_tracker.pricing import PricingRealtime

log_writer = LogWriter("realtime_tokens")   ### Name of logger
realtime_costs = {
        "text_in": 0.60,
        "cached_text_in": 0.06,
        "text_out": 2.40,
        "audio_in": 10.00,
        "audio_out": 20.00,
        "image_in": 5.00,
        "cached_image_in": 0.50,
        "cached_audio_in": 0.40,
    }
token_logger = TokenLogger(log_writer, PricingRealtime(realtime_costs))

token_logger_realtime.record(realtime_model, realtime_result, fake_realtime_usage)

MODEL_NAME = "gpt-realtime-mini"
response = ...
realtime_result = "This is a fake realtime result"
usage = response.usage
token_logger.record(MODEL_NAME, realtime_result, usage)
```


```python
from gpt_token_tracker.token_logger import TokenLogger
from gpt_token_tracker.writers.csv_writer import CSVWriter
from gpt_token_tracker.pricing import PricingTextCompletion

csv_writer = CSVWriter("completion_usage.csv")
text_completion_costs = {
        "text_in": 0.25,
        "cached_text_in": 0.025,
        "text_out": 2.00,
    }
csv_token_logger = TokenLogger(csv_writer, PricingTextCompletion(text_completion_costs))

MODEL_NAME = "gpt-5-mini"

response = ...
completion_result = "This is a fake completion result"
usage = response.usage
csv_token_logger.record(MODEL_NAME, completion_result, usage)
```

```python
from gpt_token_tracker.token_logger import TokenLogger
from gpt_token_tracker.writers.csv_writer import CSVWriter
from gpt_token_tracker.pricing_gemini import PricingGemini

csv_writer = CSVWriter("gemini_usage.csv")
costs = {
        "text_in": 0.10,
        "image_in": 0.10,
        "video_in": 0.10,
        "audio_in": 0.30,
        "cached_text_in": 0.01,
        "cached_video_in": 0.01,
        "cached_image_in": 0.01,
        "cached_audio_in": 0.03,
        "text_out": 0.40,
        "audio_out": 0.40,
        "thinking": 0.40
    }


csv_token_logger = TokenLogger(csv_writer, PricingGemini(costs))

MODEL_NAME = "gemini-2.5-flash-native-audio"

response = ...
result = "This is a fake completion result"
usage = ...
csv_token_logger.record(MODEL_NAME, result, usage)
```

To run tests:
```shell
python -m pip install -r requirements.txt -r requirements_tests.txt --upgrade
python -m pytest tests
```

