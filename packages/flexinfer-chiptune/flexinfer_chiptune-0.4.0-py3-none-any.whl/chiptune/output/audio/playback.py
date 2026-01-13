"""Real-time audio playback for previewing compositions.

Requires optional 'sounddevice' dependency for playback.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel


class AudioPlayer(BaseModel):
    """Real-time audio playback for previewing compositions.

    Requires optional 'sounddevice' dependency:
        pip install py-chiptune[audio]

    Example:
        ```python
        from chiptune import ChiptuneComposer
        from chiptune.output.audio import AudioExporter, AudioPlayer

        composer = ChiptuneComposer.create()
        composer.add_melody(length_bars=4)
        track = composer.build()

        exporter = AudioExporter()
        audio = exporter.render_track(track)

        player = AudioPlayer()
        player.play(audio)  # Blocking
        player.play_async(audio)  # Non-blocking
        player.stop()
        ```
    """

    sample_rate: int = 44100

    def play(self, samples: NDArray[np.float32], blocking: bool = True) -> None:
        """Play audio samples.

        Args:
            samples: Stereo audio as (N, 2) float32 array
            blocking: Wait for playback to complete
        """
        try:
            import sounddevice as sd
        except ImportError as e:
            raise ImportError(
                "sounddevice not installed. Install with: pip install py-chiptune[audio]"
            ) from e

        sd.play(samples, self.sample_rate)
        if blocking:
            sd.wait()

    def play_async(self, samples: NDArray[np.float32]) -> None:
        """Play audio without blocking."""
        self.play(samples, blocking=False)

    def stop(self) -> None:
        """Stop any playing audio."""
        try:
            import sounddevice as sd

            sd.stop()
        except ImportError:
            pass

    @staticmethod
    def is_available() -> bool:
        """Check if real-time playback is available."""
        try:
            import sounddevice  # noqa: F401

            return True
        except ImportError:
            return False
