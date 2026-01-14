import logging
import pytest

from gpt_token_tracker.models import RealtimeModel, RealtimeTranscribeModel, ChatCompletionModel, GeminiModel, AnthropicModel, TimedIntervalModel
from gpt_token_tracker.pricing import TOKENS_PER_PRICE


# -----------------------------
# Tests
# -----------------------------

def test_compute_costs_realtime(token_logger_realtime, fake_realtime_usage, realtime_pricing, realtime_model):
    costs: RealtimeModel = token_logger_realtime.compute_costs(fake_realtime_usage, realtime_model)
    pricing = realtime_pricing.pricing[realtime_model]
    expected_text = (50 * pricing["text_in"]) / TOKENS_PER_PRICE
    expected_audio = (100 * pricing["audio_in"]) / TOKENS_PER_PRICE
    expected_image = (10 * pricing["image_in"]) / TOKENS_PER_PRICE
    expected_cached_text = (5 * pricing["cached_text_in"]) / TOKENS_PER_PRICE
    expected_cached_audio = 0
    expected_cached_image = 0
    expected_output_text = (30 * pricing["text_out"]) / TOKENS_PER_PRICE
    expected_output_audio = (20 * pricing["audio_out"]) / TOKENS_PER_PRICE

    expected_input_total = (
        expected_text
        + expected_audio
        + expected_image
        + expected_cached_text
        + expected_cached_audio
        + expected_cached_image
    )
    expected_output_total = expected_output_text + expected_output_audio
    expected_total = expected_input_total + expected_output_total

    assert costs.input_text_cost == pytest.approx(expected_text)
    assert costs.input_audio_cost == pytest.approx(expected_audio)
    assert costs.input_image_cost == pytest.approx(expected_image)

    assert costs.cached_text_cost == pytest.approx(expected_cached_text)
    assert costs.cached_audio_cost == expected_cached_audio
    assert costs.cached_image_cost == expected_cached_image

    assert costs.text_output_cost == pytest.approx(expected_output_text)
    assert costs.audio_output_cost == pytest.approx(expected_output_audio)

    assert costs.total_input_cost == pytest.approx(expected_input_total)
    assert costs.total_output_cost == pytest.approx(expected_output_total)
    assert costs.total_cost == pytest.approx(expected_total)


def test_record_logs_realtime(log_writer, realtime_model, realtime_result, token_logger_realtime, fake_realtime_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_realtime.record(realtime_model, realtime_result, fake_realtime_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: gpt-realtime-mini | Result: The capital of Ireland is Dublin | Input Tokens: 165 | Input Text Tokens: 50 | Input Audio Tokens: 100 | Input Image Tokens: 10 | Cached Text Tokens: 5 | Cached Audio Tokens: 0 | Cached Image Tokens: 0 | Output Tokens: 50 | Output Text Tokens: 30 | Output Audio Tokens: 20 | Total Tokens: 215 | Input Text Cost: 0.000030 | Input Audio Cost: 0.001000 | Input Image Cost: 0.000050 | Cached Text Cost: 0.000000 | Cached Audio Cost: 0.000000 | Cached Image Cost: 0.000000 | Text Output Cost: 0.000072 | Audio Output Cost: 0.000400 | Total Input Cost: 0.001080 | Total Output Cost: 0.000472 | Total Cost: 0.001552"


def test_record_logs_completion_multiline(log_writer, realtime_model, text_realtime_result_multiline, token_logger_realtime, fake_realtime_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_realtime.record(realtime_model, text_realtime_result_multiline, fake_realtime_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == 'Model: gpt-realtime-mini | Result: Ireland has a rich history and culture.\\nThe capital of Ireland is Dublin.\\nIt is known for its literary heritage and vibrant city life. | Input Tokens: 165 | Input Text Tokens: 50 | Input Audio Tokens: 100 | Input Image Tokens: 10 | Cached Text Tokens: 5 | Cached Audio Tokens: 0 | Cached Image Tokens: 0 | Output Tokens: 50 | Output Text Tokens: 30 | Output Audio Tokens: 20 | Total Tokens: 215 | Input Text Cost: 0.000030 | Input Audio Cost: 0.001000 | Input Image Cost: 0.000050 | Cached Text Cost: 0.000000 | Cached Audio Cost: 0.000000 | Cached Image Cost: 0.000000 | Text Output Cost: 0.000072 | Audio Output Cost: 0.000400 | Total Input Cost: 0.001080 | Total Output Cost: 0.000472 | Total Cost: 0.001552'


def test_compute_costs_realtime_transcribe(token_logger_realtime_transcribe, fake_audio_transcription_usage, realtime_transcribe_pricing, transcribe_model):
    costs: RealtimeTranscribeModel = token_logger_realtime_transcribe.compute_costs(fake_audio_transcription_usage, transcribe_model)
    pricing = realtime_transcribe_pricing.pricing[transcribe_model]
    expected_text_cost = (1 * pricing["text_in"]) / TOKENS_PER_PRICE
    expected_audio_cost = (101 * pricing["audio_in"]) / TOKENS_PER_PRICE
    expected_output_text = (7 * pricing["text_out"]) / TOKENS_PER_PRICE

    expected_input_total = (
        expected_text_cost
        + expected_audio_cost
    )
    expected_total = expected_input_total + expected_output_text

    assert costs.input_text_cost == pytest.approx(expected_text_cost)
    assert costs.input_audio_cost == pytest.approx(expected_audio_cost)

    assert costs.output_text_cost == pytest.approx(expected_output_text)

    assert costs.total_cost == pytest.approx(expected_total)


def test_record_logs_realtime_transcribe(log_writer, transcribe_model, realtime_transcription_result, token_logger_realtime_transcribe, fake_audio_transcription_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_realtime_transcribe.record(transcribe_model, realtime_transcription_result, fake_audio_transcription_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: gpt-4o-mini-transcribe | Result: What is the capital of Ireland? | Input Text Tokens: 1 | Input Audio Tokens: 101 | Output Text Tokens: 7 | Total Tokens: 109 | Input Text Cost: 0.000001 | Input Audio Cost: 0.000303 | Output Text Cost: 0.000035 | Total Cost: 0.000339"


def test_compute_costs_text_completion(
    token_logger_text_completion,
    fake_text_completion_usage,
    text_completion_pricing,
    text_completion_model
):
    costs: ChatCompletionModel = token_logger_text_completion.compute_costs(fake_text_completion_usage, text_completion_model)

    pricing = text_completion_pricing.pricing[text_completion_model]

    expected_text = (165 * pricing["text_in"]) / TOKENS_PER_PRICE
    expected_cached_text = (5 * pricing["cached_text_in"]) / TOKENS_PER_PRICE
    expected_output_text = (50 * pricing["text_out"]) / TOKENS_PER_PRICE

    expected_total = expected_text + expected_cached_text + expected_output_text

    assert costs.input_text_cost == pytest.approx(expected_text)
    assert costs.cached_text_cost == pytest.approx(expected_cached_text)
    assert costs.output_text_cost == pytest.approx(expected_output_text)
    assert costs.total_cost == pytest.approx(expected_total)

    assert costs.input_text_tokens == 165
    assert costs.cached_text_tokens == 5
    assert costs.output_text_tokens == 50


def test_record_logs_text_completion(log_writer, text_completion_model, text_completion_result, token_logger_text_completion, fake_text_completion_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_text_completion.record(text_completion_model, text_completion_result, fake_text_completion_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: gpt-5-mini | Result: The capital of Ireland is Dublin | Input Text Tokens: 165 | Cached Text Tokens: 5 | Output Text Tokens: 50 | Total Tokens: 215 | Input Text Cost: 0.000041 | Cached Text Cost: 0.000000 | Output Text Cost: 0.000100 | Total Cost: 0.000141"


def test_compute_costs_gemini(
    token_logger_gemini,
    fake_gemini_usage,
    gemini_pricing,
    gemini_model
):
    costs: GeminiModel = token_logger_gemini.compute_costs(fake_gemini_usage, gemini_model)

    pricing = gemini_pricing.pricing[gemini_model]

    expected_text = (533 * pricing["text_in"]) / TOKENS_PER_PRICE
    expected_audio = (1 * pricing["audio_in"]) / TOKENS_PER_PRICE
    expected_output_audio = (26 * pricing["text_out"]) / TOKENS_PER_PRICE
    expected_thinking = (42 * pricing["thinking"]) / TOKENS_PER_PRICE

    expected_total = expected_text + expected_audio + expected_output_audio + expected_thinking

    assert costs.input_text_cost == pytest.approx(expected_text)
    assert costs.input_audio_cost == pytest.approx(expected_audio)
    assert costs.audio_output_cost == pytest.approx(expected_output_audio)
    assert costs.thinking_cost == pytest.approx(expected_thinking)
    assert costs.total_cost == pytest.approx(expected_total)

    assert costs.input_text_tokens == 533
    assert costs.input_audio_tokens == 1
    assert costs.output_audio_tokens == 26
    assert costs.thinking_tokens == 42


def test_record_logs_gemini(log_writer, gemini_model, gemini_result, token_logger_gemini, fake_gemini_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_gemini.record(gemini_model, gemini_result, fake_gemini_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: gemini-2.5-flash-native-audio-preview-12-2025 | Result: The capital of Ireland is Dublin | Input Tokens: 534 | Input Text Tokens: 533 | Input Audio Tokens: 1 | Input Image Tokens: 0 | Input Video Tokens: 0 | Input Document Tokens: 0 | Cached Text Tokens: 0 | Cached Audio Tokens: 0 | Cached Image Tokens: 0 | Cached Video Tokens: 0 | Cached Document Tokens: 0 | Output Tokens: 26 | Output Text Tokens: 0 | Output Audio Tokens: 26 | Output Image Tokens: 0 | Output Video Tokens: 0 | Output Document Tokens: 0 | Thinking Tokens: 42 | Total Tokens: 602 | Input Text Cost: 0.000053 | Input Audio Cost: 0.000000 | Input Image Cost: 0.000000 | Input Video Cost: 0.000000 | Input Document Cost: 0.000000 | Cached Text Cost: 0.000000 | Cached Audio Cost: 0.000000 | Cached Image Cost: 0.000000 | Cached Video Cost: 0.000000 | Cached Document Cost: 0.000000 | Text Output Cost: 0.000000 | Audio Output Cost: 0.000010 | Image Output Cost: 0.000000 | Video Output Cost: 0.000000 | Document Output Cost: 0.000000 | Total Input Cost: 0.000054 | Total Output Cost: 0.000010 | Thinking Cost: 0.000017 | Total Cost: 0.000081"


def test_compute_costs_anthropic(
    token_logger_anthropic,
    fake_anthropic_usage,
    anthropic_pricing,
    anthropic_model
):
    costs: AnthropicModel = token_logger_anthropic.compute_costs(fake_anthropic_usage, anthropic_model)

    pricing = anthropic_pricing.pricing[anthropic_model]

    expected_input = (13 * pricing["all_in"]) / TOKENS_PER_PRICE
    expected_output = (21 * pricing["all_out"]) / TOKENS_PER_PRICE

    expected_total = expected_input + expected_output

    assert costs.input_cost == pytest.approx(expected_input)
    assert costs.output_cost == pytest.approx(expected_output)
    assert costs.cached_input_cost == 0
    assert costs.cache_1h_cost == 0
    assert costs.cache_5m_cost == 0
    assert costs.total_cost == expected_total

    assert costs.input_tokens == 13
    assert costs.cache_creation_tokens == 0
    assert costs.cache_read_input_tokens == 0
    assert costs.output_tokens == 21


def test_record_logs_anthropic(log_writer, anthropic_model, anthropic_result, token_logger_anthropic, fake_anthropic_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_anthropic.record(anthropic_model, anthropic_result, fake_anthropic_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: claude-sonnet-4-5 | Result: The capital of Ireland is Dublin | Input Tokens: 13 | Cache Creation Tokens: 0 | Cache Read Input Tokens: 0 | Output Tokens: 21 | Total Tokens: 34 | Input Cost: 0.000039 | Cached Input Cost: 0.000000 | Cache 5M Cost: 0.000000 | Cache 1H Cost: 0.000000 | Output Cost: 0.000315 | Total Cost: 0.000354"


def test_compute_costs_grok_timed(
    token_logger_timed,
    fake_timed_usage,
    grok_pricing,
    grok_model
):
    costs: TimedIntervalModel = token_logger_timed.compute_costs(fake_timed_usage, grok_model)

    assert costs.start_time == fake_timed_usage.start_time
    assert costs.end_time == fake_timed_usage.end_time
    assert costs.minutes == 90.5
    assert costs.total_cost == 4.525


def test_record_logs_grok_timed(log_writer, grok_model, token_logger_timed, fake_timed_usage, caplog):
    with caplog.at_level(logging.INFO):
        token_logger_timed.record_timed(grok_model, fake_timed_usage)

    assert len(caplog.records) == 1
    msg = caplog.records[0].message

    assert msg == "Model: grok-4 | Start Time: 2026-07-01 16:00:00 | End Time: 2026-07-01 17:30:30 | Minutes: 90.500000 | Total Cost: 4.525000"


def test_close_is_noop(log_writer):
    # Should not raise
    log_writer.close()
