import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


MODULE_PATH = Path(__file__).parents[1] / "helpers" / "transcribe.py"
SPEC = importlib.util.spec_from_file_location("video_use_transcribe", MODULE_PATH)
assert SPEC and SPEC.loader
transcribe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transcribe)


class LoadApiKeyOptionalTests(unittest.TestCase):
    def test_returns_none_when_key_is_missing_everywhere(self):
        with patch.object(Path, "exists", return_value=False):
            with patch.dict(transcribe.os.environ, {}, clear=True):
                result = transcribe.load_api_key_optional()
        self.assertIsNone(result)

    def test_reads_key_from_env_var_when_no_env_file(self):
        with patch.dict(transcribe.os.environ, {"ELEVENLABS_API_KEY": "sk-test-123"}, clear=True):
            with patch.object(Path, "exists", return_value=False):
                result = transcribe.load_api_key_optional()
        self.assertEqual(result, "sk-test-123")


class TranscribeOneBackendSelectionTests(unittest.TestCase):
    def _run_transcribe_one(self, api_key, scribe_side_effect=None):
        with tempfile.TemporaryDirectory() as tmp:
            edit_dir = Path(tmp) / "edit"
            video = Path(tmp) / "clip.mp4"
            video.write_bytes(b"fake video bytes")

            def fake_extract_audio(video_path, dest, audio_track=0):
                dest.write_bytes(b"fake wav bytes")

            with (
                patch.object(transcribe, "count_audio_tracks", return_value=1),
                patch.object(transcribe, "extract_audio", side_effect=fake_extract_audio),
                patch.object(transcribe, "peak_dbfs", return_value=-20.0),
                patch.object(
                    transcribe, "call_scribe",
                    side_effect=scribe_side_effect,
                    return_value={"text": "hello world", "words": []},
                ) as scribe_mock,
                patch.object(
                    transcribe, "call_whisper_fallback",
                    return_value={"text": "hello world", "words": [], "language_code": "en"},
                ) as whisper_mock,
            ):
                out_path = transcribe.transcribe_one(
                    video=video, edit_dir=edit_dir, api_key=api_key, verbose=False,
                )
                payload = json.loads(out_path.read_text())
            return payload, scribe_mock, whisper_mock

    def test_uses_scribe_when_api_key_present_and_call_succeeds(self):
        payload, scribe_mock, whisper_mock = self._run_transcribe_one(api_key="sk-real-key")
        self.assertEqual(payload["transcription_source"], "elevenlabs")
        scribe_mock.assert_called_once()
        whisper_mock.assert_not_called()

    def test_falls_back_to_whisper_when_no_api_key(self):
        payload, scribe_mock, whisper_mock = self._run_transcribe_one(api_key=None)
        self.assertEqual(payload["transcription_source"], "whisper")
        scribe_mock.assert_not_called()
        whisper_mock.assert_called_once()

    def test_falls_back_to_whisper_when_scribe_call_fails(self):
        payload, scribe_mock, whisper_mock = self._run_transcribe_one(
            api_key="sk-real-key",
            scribe_side_effect=RuntimeError("Scribe returned 500: internal error"),
        )
        self.assertEqual(payload["transcription_source"], "whisper")
        scribe_mock.assert_called_once()
        whisper_mock.assert_called_once()


class CallWhisperFallbackErrorTests(unittest.TestCase):
    def test_raises_clear_error_when_model_weights_unreachable(self):
        fake_module = MagicMock()
        fake_module.WhisperModel.side_effect = OSError(
            "couldn't connect to 'https://huggingface.co'"
        )
        with patch.dict(sys.modules, {"faster_whisper": fake_module}):
            with self.assertRaises(RuntimeError) as ctx:
                transcribe.call_whisper_fallback(Path("audio.wav"))
        self.assertIn("huggingface.co", str(ctx.exception))

    def test_raises_clear_error_when_package_not_installed(self):
        with patch.dict(sys.modules, {"faster_whisper": None}):
            with self.assertRaises(RuntimeError) as ctx:
                transcribe.call_whisper_fallback(Path("audio.wav"))
        self.assertIn("uv sync --extra fallback", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
