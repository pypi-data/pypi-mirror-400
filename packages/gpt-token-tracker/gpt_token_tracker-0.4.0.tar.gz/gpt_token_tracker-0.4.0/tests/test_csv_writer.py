import csv
from gpt_token_tracker.token_logger import TokenLogger
from gpt_token_tracker.writers.csv_writer import CSVWriter


# -----------------------------
# Realtime CSV tests
# -----------------------------

def test_csv_writer_realtime(
    csv_token_logger_realtime,
    fake_realtime_usage,
    realtime_model,
    realtime_result,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_realtime.record(
        realtime_model,
        realtime_result,
        fake_realtime_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == "Timestamp,Model,Result,Input Tokens,Input Text Tokens,Input Audio Tokens,Input Image Tokens,Cached Text Tokens,Cached Audio Tokens,Cached Image Tokens,Output Tokens,Output Text Tokens,Output Audio Tokens,Total Tokens,Input Text Cost,Input Audio Cost,Input Image Cost,Cached Text Cost,Cached Audio Cost,Cached Image Cost,Text Output Cost,Audio Output Cost,Total Input Cost,Total Output Cost,Total Cost\n"
    assert value_row == f'{fixed_timestamp},gpt-realtime-mini,The capital of Ireland is Dublin,165,50,100,10,5,0,0,50,30,20,215,3e-05,0.001,5e-05,3e-07,0.0,0.0,7.2e-05,0.0004,0.0010803,0.00047200000000000003,0.0015523\n'


def test_csv_writer_realtime_multiline_result(
    csv_token_logger_realtime,
    fake_realtime_usage,
    realtime_model,
    text_realtime_result_multiline,
    csv_writer_path,
    fixed_timestamp,
):
    csv_token_logger_realtime.record(
        realtime_model,
        text_realtime_result_multiline,
        fake_realtime_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == "Timestamp,Model,Result,Input Tokens,Input Text Tokens,Input Audio Tokens,Input Image Tokens,Cached Text Tokens,Cached Audio Tokens,Cached Image Tokens,Output Tokens,Output Text Tokens,Output Audio Tokens,Total Tokens,Input Text Cost,Input Audio Cost,Input Image Cost,Cached Text Cost,Cached Audio Cost,Cached Image Cost,Text Output Cost,Audio Output Cost,Total Input Cost,Total Output Cost,Total Cost\n"
    assert value_row == (
        f"{fixed_timestamp},gpt-realtime-mini,Ireland has a rich history and culture.\\nThe capital of Ireland is Dublin.\\nIt is known for its literary heritage and vibrant city life.,165,50,100,10,5,0,0,50,30,20,215,3e-05,0.001,5e-05,3e-07,0.0,0.0,7.2e-05,0.0004,0.0010803,0.00047200000000000003,0.0015523\n"
    )


# -----------------------------
# Text realtime transcribe CSV tests
# -----------------------------

def test_csv_writer_transcribe_realtime(
    csv_token_logger_realtime_transcribe,
    fake_audio_transcription_usage,
    transcribe_model,
    realtime_transcription_result,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_realtime_transcribe.record(
        transcribe_model,
        realtime_transcription_result,
        fake_audio_transcription_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == 'Timestamp,Model,Result,Input Text Tokens,Input Audio Tokens,Output Text Tokens,Total Tokens,Input Text Cost,Input Audio Cost,Output Text Cost,Total Cost\n'
    assert value_row == f'{fixed_timestamp},gpt-4o-mini-transcribe,What is the capital of Ireland?,1,101,7,109,1.25e-06,0.000303,3.5e-05,0.00033925\n'


# -----------------------------
# Text completion CSV tests
# -----------------------------

def test_csv_writer_text_completion(
    csv_token_logger_text_completion,
    fake_text_completion_usage,
    text_completion_model,
    text_completion_result,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_text_completion.record(
        text_completion_model,
        text_completion_result,
        fake_text_completion_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == 'Timestamp,Model,Result,Input Text Tokens,Cached Text Tokens,Output Text Tokens,Total Tokens,Input Text Cost,Cached Text Cost,Output Text Cost,Total Cost\n'
    assert value_row == f"{fixed_timestamp},gpt-5-mini,The capital of Ireland is Dublin,165,5,50,215,4.125e-05,1.25e-07,0.0001,0.000141375\n"


def test_csv_writer_gemini(
    csv_token_logger_gemini,
    fake_gemini_usage,
    gemini_model,
    gemini_result,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_gemini.record(
        gemini_model,
        gemini_result,
        fake_gemini_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == "Timestamp,Model,Result,Input Tokens,Input Text Tokens,Input Audio Tokens,Input Image Tokens,Input Video Tokens,Input Document Tokens,Cached Text Tokens,Cached Audio Tokens,Cached Image Tokens,Cached Video Tokens,Cached Document Tokens,Output Tokens,Output Text Tokens,Output Audio Tokens,Output Image Tokens,Output Video Tokens,Output Document Tokens,Thinking Tokens,Total Tokens,Input Text Cost,Input Audio Cost,Input Image Cost,Input Video Cost,Input Document Cost,Cached Text Cost,Cached Audio Cost,Cached Image Cost,Cached Video Cost,Cached Document Cost,Text Output Cost,Audio Output Cost,Image Output Cost,Video Output Cost,Document Output Cost,Total Input Cost,Total Output Cost,Thinking Cost,Total Cost\n"
    assert value_row == f"{fixed_timestamp},gemini-2.5-flash-native-audio-preview-12-2025,The capital of Ireland is Dublin,534,533,1,0,0,0,0,0,0,0,0,26,0,26,0,0,0,42,602,5.33e-05,3e-07,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.04e-05,0.0,0.0,0.0,5.36e-05,1.04e-05,1.6800000000000002e-05,8.08e-05\n"


def test_csv_writer_anthropic(
    csv_token_logger_anthropic,
    fake_anthropic_usage,
    anthropic_model,
    anthropic_result,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_anthropic.record(
        anthropic_model,
        anthropic_result,
        fake_anthropic_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == 'Timestamp,Model,Result,Input Tokens,Cache Creation Tokens,Cache Read Input Tokens,Output Tokens,Total Tokens,Input Cost,Cached Input Cost,Cache 5M Cost,Cache 1H Cost,Output Cost,Total Cost\n'
    assert value_row == f"{fixed_timestamp},claude-sonnet-4-5,The capital of Ireland is Dublin,13,0,0,21,34,3.9e-05,0.0,0.0,0.0,0.000315,0.00035400000000000004\n"


def test_csv_writer_timed_usage_grok(
    csv_token_logger_timed,
    fake_timed_usage,
    grok_model,
    csv_writer_path,
    fixed_timestamp
):

    csv_token_logger_timed.record_timed(
        grok_model,
        fake_timed_usage,
    )

    with csv_writer_path.open() as f:
        header_row = f.readline()
        value_row = f.readline()

    assert header_row == 'Timestamp,Model,Start Time,End Time,Minutes,Total Cost\n'
    assert value_row == '2026-01-04T12:09:20.638929,grok-4,2026-07-01 16:00:00,2026-07-01 17:30:30,90.5,4.525\n'


# -----------------------------
# Append behavior
# -----------------------------

def test_csv_writer_appends_rows(
    csv_token_logger_text_completion,
    fake_text_completion_usage,
    text_completion_model,
    text_completion_result,
    csv_writer_path,
):

    csv_token_logger_text_completion.record(
        text_completion_model,
        text_completion_result,
        fake_text_completion_usage,
    )
    csv_token_logger_text_completion.record(
        text_completion_model,
        text_completion_result,
        fake_text_completion_usage,
    )

    with csv_writer_path.open() as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2


def test_csv_writer_reinit_does_not_duplicate_header(
    csv_writer_path,
    fake_text_completion_usage,
    text_completion_model,
    text_completion_result,
    text_completion_pricing,
):

    assert not csv_writer_path.exists()
    # First writer instance
    CSVWriter(csv_writer_path)
    assert csv_writer_path.exists()
    assert csv_writer_path.stat().st_size == 0

    # Second writer instance (simulates new process / restart)
    writer2 = CSVWriter(csv_writer_path)
    logger2 = TokenLogger(writer2, text_completion_pricing)

    logger2.record(
        text_completion_model,
        text_completion_result,
        fake_text_completion_usage,
    )

    with csv_writer_path.open(newline="") as f:
        lines = f.readlines()

    header_lines = [line for line in lines if line.startswith("Timestamp,")]
    data_lines = lines[1:]

    assert len(header_lines) == 1
    assert len(data_lines) == 1

  # Second writer instance (simulates new process / restart)
    writer3 = CSVWriter(csv_writer_path)
    logger3 = TokenLogger(writer3, text_completion_pricing)

    logger3.record(
        text_completion_model,
        text_completion_result,
        fake_text_completion_usage,
    )

    with csv_writer_path.open(newline="") as f:
        lines = f.readlines()

    header_lines = [line for line in lines if line.startswith("Timestamp,")]
    data_lines = lines[1:]

    assert len(header_lines) == 1
    assert len(data_lines) == 2
