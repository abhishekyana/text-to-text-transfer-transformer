# Copyright 2019 The T5 Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for t5.evaluation.metrics."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest
from t5.evaluation import metrics


class MetricsTest(absltest.TestCase):

  def assertDictClose(self, a, b, delta=None):
    self.assertCountEqual(a.keys(), b.keys())
    for k in a:
      try:
        self.assertAlmostEqual(a[k], b[k], delta=delta)
      except AssertionError as e:
        raise AssertionError(str(e) + " for key '%s'" % k)

  def test_same_bleu(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.bleu([ref, ref], [ref, ref]),
        {"bleu": 100})

  def test_different_bleu(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.bleu([ref, ref], ["", ""]),
        {"bleu": 0})

  def test_same_rouge(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.rouge([ref, ref], [ref, ref]),
        {"rouge1": 100, "rouge2": 100, "rougeLsum": 100})

  def test_different_rouge(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.rouge([ref, ref], ["", ""]),
        {"rouge1": 0, "rouge2": 0, "rougeLsum": 0})

  def test_rouge_bytes(self):
    ref = b"this \x7e is a string"
    self.assertDictClose(
        metrics.rouge([ref, ref], [ref, ref]),
        {"rouge1": 100, "rouge2": 100, "rougeLsum": 100})

  def test_same_qa(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.qa([["", ref], [ref, ref]], [ref, ref]), {
            "em": 100,
            "f1": 100,
        })

  def test_different_qa(self):
    ref = "this is a string"
    self.assertDictClose(
        metrics.qa([[ref, ref], [ref, ref]], ["", ""]), {
            "em": 0,
            "f1": 0
        })

  def test_qa_bytes(self):
    ref = b"this is a string"
    self.assertDictClose(
        metrics.qa([["", ref], [ref, ref]], [ref, ref]), {
            "em": 100,
            "f1": 100
        })

  def test_qa_big(self):
    self.assertDictClose(
        metrics.qa(
            [
                ["big moose", "hippo"],
                ["correct1"],
                ["correct2.1", "correct2.2"],
                ["a", "b"],
            ],
            [
                "a big  Moose!",
                "wrong",
                "correct2.2",
                "c",
            ],
        ),
        {"em": 50., "f1": 50.},
    )

  def test_qa_small(self):
    self.assertDictClose(
        metrics.qa([["abc abd", "$$$$"]], ["abd"]),
        {"f1": 100 * 2.0 / 3.0, "em": 0.},
    )

  def test_span_qa(self):
    ref = "a string"
    ans_span = "start:2 end:3"
    context = "this is a string! it has the answer."
    self.assertDictClose(
        metrics.span_qa(
            [{"answers": ["", ref], "context": context},
             {"answers": [ref, ref], "context": context}],
            [ans_span, ans_span]),
        {"em": 100, "f1": 100})

  def test_span_qa_bytes(self):
    ref = b"a string"
    ans_span = b"start:2 end:3"
    context = b"this is a string! it has the answer."

    self.assertDictClose(
        metrics.span_qa(
            [{"answers": ["", ref], "context": context},
             {"answers": [ref, ref], "context": context}],
            [ans_span, ans_span]),
        {"em": 100, "f1": 100})

  def test_span_qa_one_word(self):
    ref = "answer"
    ans_span = "start:1 end:1"
    context = "the answer"

    self.assertDictClose(
        metrics.span_qa([{
            "answers": [ref],
            "context": context
        }], [ans_span]), {"em": 100, "f1": 100})

  def test_span_qa_non_numbers(self):

    ref = "answer"
    ans_span = "start:test end:why"
    context = "the answer"

    self.assertDictClose(
        metrics.span_qa([{
            "answers": [ref],
            "context": context
        }], [ans_span]), {"em": 0, "f1": 0})

  def test_sequence_accuracy(self):
    s1 = "this is a string."
    s2 = "this is a completely different string."
    self.assertDictEqual(
        metrics.sequence_accuracy([s1, s2], [s1, s1]),
        {"sequence_accuracy": 50})

  def test_multiclass_f1(self):
    self.assertDictClose(
        metrics.mean_multiclass_f1(num_classes=3)([0, 1, 1, 2], [0, 0, 2, 2]),
        {"mean_3class_f1": 44.44444444444444})

  def test_exact_match(self):
    self.assertDictEqual(
        metrics.exact_match([0, 1], [0, 1]), {"exact_match": 100.0})
    self.assertDictEqual(
        metrics.exact_match([0, 1], [0, 2]), {"exact_match": 0.0})

  def test_pearson_corrcoef(self):
    self.assertDictClose(
        metrics.pearson_corrcoef([0, 2], [0, 1]),
        {"pearson_corrcoef": 100.0})

  def test_spearman_corrcoef(self):
    self.assertDictClose(
        metrics.spearman_corrcoef([0, 2, 1], [0, 1, 2]),
        {"spearman_corrcoef": 50.})

  def test_matthews_corrcoef(self):
    self.assertDictClose(
        metrics.matthews_corrcoef([0, 0, 2, 1], [0, 1, 2, 1]),
        {"matthews_corrcoef": 70.})

  def test_f1_score_with_invalid(self):
    self.assertDictClose(
        metrics.f1_score_with_invalid([0, 1, 1, 0], [0, 1, 2, 2]),
        {"f1": 50.})

  def test_accuracy(self):
    self.assertDictClose(
        metrics.accuracy([0, 0, 2, 1], [0, 1, 2, 1]),
        {"accuracy": 75.})

  def test_mean_group_metric(self):
    metric_fn = metrics.mean_group_metric(metrics.accuracy)
    self.assertDictClose(
        metric_fn(
            [{"group": "a", "value": 0},
             {"group": "a", "value": 1},
             {"group": "b", "value": 0}],
            [{"value": 0},
             {"value": 0},
             {"value": 1}]),
        {"accuracy": 25.})


if __name__ == "__main__":
  absltest.main()
