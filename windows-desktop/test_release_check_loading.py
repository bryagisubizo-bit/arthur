"""Regression checks for the visible manual release-check progress text."""

import unittest

from release_check_loading import LOADING_FRAMES, release_check_loading_text


class ReleaseCheckLoadingTests(unittest.TestCase):
    def test_loading_text_cycles_through_all_frames(self):
        frames = [release_check_loading_text(index) for index in range(len(LOADING_FRAMES))]
        self.assertEqual(len(set(frames)), len(LOADING_FRAMES))
        self.assertTrue(all(text.startswith("Checking GitHub release metadata") for text in frames))

    def test_loading_text_wraps_after_the_final_frame(self):
        self.assertEqual(release_check_loading_text(0), release_check_loading_text(len(LOADING_FRAMES)))


if __name__ == "__main__":
    unittest.main()
