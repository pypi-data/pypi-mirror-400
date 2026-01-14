# Copyright (c) 2024-2025 Or Posener
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Test utilities for VoicegroundObserver tests."""

from collections.abc import Sequence

from pipecat.frames.frames import EndFrame, StartFrame
from pipecat.observers.base_observer import FramePushed
from pipecat.processors.filters.identity_filter import IdentityFilter
from pipecat.processors.frame_processor import FrameDirection


async def run_observer_test(
    observer,
    frames_to_send: Sequence[FramePushed],
    auto_start: bool = True,
    auto_end: bool = True,
):
    """Run a sequence of FramePushed objects through an observer.

    Similar to pipecat's run_test, but works directly with FramePushed objects
    and an observer instead of a pipeline.

    Args:
        observer: The VoicegroundObserver instance.
        frames_to_send: Sequence of FramePushed objects to process.
        auto_start: Whether to automatically push StartFrame at the beginning. Defaults to True.
        auto_end: Whether to automatically push EndFrame at the end. Defaults to True.

    Returns:
        The observer instance (for accessing reporters).
    """
    identity = IdentityFilter()

    if auto_start:
        start_frame = FramePushed(
            source=identity,
            destination=identity,
            frame=StartFrame(),
            direction=FrameDirection.DOWNSTREAM,
            timestamp=0,
        )
        await observer.on_push_frame(start_frame)

    for frame_pushed in frames_to_send:
        await observer.on_push_frame(frame_pushed)

    if auto_end:
        end_frame = FramePushed(
            source=identity,
            destination=identity,
            frame=EndFrame(),
            direction=FrameDirection.DOWNSTREAM,
            timestamp=0,
        )
        await observer.on_push_frame(end_frame)

    return observer
