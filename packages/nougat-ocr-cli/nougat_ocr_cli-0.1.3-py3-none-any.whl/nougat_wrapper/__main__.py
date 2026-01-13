"""Allow running as `python -m nougat_wrapper`."""

from nougat_wrapper.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
