import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import unittest
from loop_analyzer import analyze_source, bounded_deterministic_monitor

class AnalyzerTests(unittest.TestCase):
    def test_constant_true_without_break(self):
        r = analyze_source("while True:\n    print('x')\n")
        self.assertEqual(r["status"], "HIGH_RISK_PATTERN")

    def test_unchanged_condition_variable(self):
        r = analyze_source("i = 0\nwhile i < 10:\n    print(i)\n")
        self.assertEqual(r["status"], "POTENTIAL_RISK")

    def test_counter_update_not_flagged(self):
        r = analyze_source("i = 0\nwhile i < 10:\n    i += 1\n")
        self.assertEqual(r["status"], "NO_PATTERN_FOUND")

    def test_syntax_error(self):
        r = analyze_source("while True\n print('x')")
        self.assertEqual(r["status"], "INVALID_SYNTAX")

    def test_cycle_detection(self):
        r = bounded_deterministic_monitor(0, lambda x: (x + 1) % 3, 20)
        self.assertEqual(r["status"], "CYCLE_DETECTED")
        self.assertEqual(r["cycle_length"], 3)

    def test_termination(self):
        r = bounded_deterministic_monitor(0, lambda x: x + 1 if x < 3 else None, 10)
        self.assertEqual(r["status"], "TERMINATED")

if __name__ == "__main__":
    unittest.main()
