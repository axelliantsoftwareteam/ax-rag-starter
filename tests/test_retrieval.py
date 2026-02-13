"""Unit tests for retrieval scoring (reciprocal rank fusion)."""

from __future__ import annotations

from ax_rag.retrieval.hybrid import reciprocal_rank_fusion


class TestReciprocalRankFusion:
    def test_single_list(self):
        scores = reciprocal_rank_fusion([["a", "b", "c"]], k=60)
        assert scores["a"] > scores["b"] > scores["c"]

    def test_two_lists_boost_overlap(self):
        list1 = ["a", "b", "c"]
        list2 = ["c", "a", "d"]
        scores = reciprocal_rank_fusion([list1, list2], k=60)
        # "a" appears in both lists at good positions — should score highest
        assert scores["a"] > scores["d"]
        # "c" appears in both but at worse positions in list1
        assert scores["a"] > scores["c"]

    def test_empty_lists(self):
        scores = reciprocal_rank_fusion([[], []])
        assert scores == {}

    def test_k_parameter_affects_scores(self):
        lists = [["a", "b"]]
        scores_low_k = reciprocal_rank_fusion(lists, k=1)
        scores_high_k = reciprocal_rank_fusion(lists, k=1000)
        # With lower k, the score difference between ranks is larger
        diff_low = scores_low_k["a"] - scores_low_k["b"]
        diff_high = scores_high_k["a"] - scores_high_k["b"]
        assert diff_low > diff_high
