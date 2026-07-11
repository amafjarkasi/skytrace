#!/usr/bin/env python
"""Download public under-shot + overhead + drone samples for the demo."""

from skytrace.samples import ensure_all_samples


def main() -> None:
    result = ensure_all_samples()
    for key, paths in result.items():
        for path in paths:
            print(f"[{key}] {path}")


if __name__ == "__main__":
    main()
