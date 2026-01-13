"""Merges transcription results from multiple chunks."""

from video_to_text.core.chunker import AudioChunk
from video_to_text.core.transcriber import TranscriptionResult
from video_to_text.models import Segment


class MergerError(Exception):
    """Raised when merging fails."""

    pass


class Merger:
    """Merges chunk transcription results into a single transcript."""

    def __init__(self, overlap_threshold: float = 0.5):
        """Initialize merger.

        Args:
            overlap_threshold: Time threshold in seconds for detecting
                             duplicate segments in overlap regions.
        """
        self.overlap_threshold = overlap_threshold

    def merge(
        self,
        chunks: list[AudioChunk],
        results: list[TranscriptionResult],
    ) -> list[Segment]:
        """Merge multiple transcription results.

        Args:
            chunks: List of audio chunks (for timing info).
            results: List of transcription results corresponding to chunks.

        Returns:
            Merged list of segments with corrected timestamps.

        Raises:
            MergerError: If chunks and results don't match.
        """
        if len(chunks) != len(results):
            raise MergerError(
                f"Mismatch: {len(chunks)} chunks but {len(results)} results"
            )

        if not chunks:
            return []

        # Single chunk - no merging needed
        if len(chunks) == 1:
            return results[0].segments

        merged_segments: list[Segment] = []

        for i, (chunk, result) in enumerate(zip(chunks, results)):
            chunk_segments = result.segments

            if i == 0:
                # First chunk - add all segments
                merged_segments.extend(chunk_segments)
            else:
                # Subsequent chunks - handle overlap
                filtered = self._filter_overlap(merged_segments, chunk_segments)
                merged_segments.extend(filtered)

        return merged_segments

    def _filter_overlap(
        self,
        existing: list[Segment],
        new_segments: list[Segment],
    ) -> list[Segment]:
        """Filter out duplicate segments from overlap region.

        Args:
            existing: Already merged segments.
            new_segments: New segments to add.

        Returns:
            Filtered new segments without duplicates.
        """
        if not existing or not new_segments:
            return new_segments

        last_existing = existing[-1]
        filtered: list[Segment] = []

        for segment in new_segments:
            # Skip if segment starts before or at the last existing segment's end
            # This handles the overlap region
            if segment.start_time <= last_existing.end_time + self.overlap_threshold:
                # Check if it's a duplicate by comparing text similarity
                if self._is_duplicate(last_existing, segment):
                    continue

            filtered.append(segment)

        return filtered

    def _is_duplicate(self, seg1: Segment, seg2: Segment) -> bool:
        """Check if two segments are duplicates.

        Uses time overlap and text similarity.
        """
        # Check time overlap
        time_overlap = (
            seg1.start_time <= seg2.end_time and seg2.start_time <= seg1.end_time
        )

        if not time_overlap:
            return False

        # Check text similarity (simple contains check)
        text1 = seg1.text.lower().strip()
        text2 = seg2.text.lower().strip()

        # If one contains the other or they're very similar
        if text1 in text2 or text2 in text1:
            return True

        # Check word overlap
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return False

        intersection = words1 & words2
        smaller_set = min(len(words1), len(words2))

        # If more than 70% words overlap, consider duplicate
        return len(intersection) / smaller_set > 0.7 if smaller_set > 0 else False
