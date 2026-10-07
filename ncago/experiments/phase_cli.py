import argparse
from .run import execute
from .common import ROOT
import yaml


def task_main(phase):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile",choices=["smoke","full"],default="smoke")
    parser.add_argument("--config",type=str)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT/"configs"/f"{args.profile}.yaml" if not args.config else ROOT/args.config).read_text())
    execute(config,[phase])
