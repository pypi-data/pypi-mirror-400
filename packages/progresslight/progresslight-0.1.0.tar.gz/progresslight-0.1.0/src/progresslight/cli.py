import argparse
import time

from .log import Logger
from .progress import ProgressBar


def run_demo(total: int, delay: float) -> None:
    logger = Logger()
    logger.info("progress demo start")

    bar = ProgressBar(description="Working", total_size=total, item="items")
    for _ in range(total):
        time.sleep(delay)
        bar.update(1)
    bar.done()

    logger.info("progress demo done")
    logger.warn("this is a warning")
    logger.error("this is an error")


def main() -> None:
    parser = argparse.ArgumentParser(prog="progresslight")
    sub = parser.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo", help="run a short progress/log demo")
    demo.add_argument("--total", type=int, default=50)
    demo.add_argument("--delay", type=float, default=0.02)

    args = parser.parse_args()

    if args.cmd == "demo":
        run_demo(args.total, args.delay)


if __name__ == "__main__":
    main()
