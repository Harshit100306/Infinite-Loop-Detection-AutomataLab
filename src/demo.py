from loop_analyzer import analyze_source, bounded_deterministic_monitor
import json

examples = {
    "constant_true": "while True:\n    print('running')\n",
    "unchanged_condition": "i = 0\nwhile i < 5:\n    print(i)\n",
    "counter_updates": "i = 0\nwhile i < 5:\n    i += 1\n",
    "break_exit": "while True:\n    if ready():\n        break\n",
}
for name, source in examples.items():
    print(f"\n--- {name} ---")
    print(json.dumps(analyze_source(source), indent=2))

print("\n--- finite-state cycle monitor ---")
result = bounded_deterministic_monitor(0, lambda x: (x + 1) % 4, max_steps=20)
print(json.dumps(result, indent=2))
