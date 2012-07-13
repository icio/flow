from flow import *
from datetime import datetime
from argparse import ArgumentParser

from time import sleep
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

parser = ArgumentParser(prog="flow", description="Snapshot flow visualiser")
parser.add_argument("-m", "--monitor", action="store_true", help="Monitor the file structure")
parser.add_argument("-H", "--highlight", nargs="+", default=[], help="Patterns of jobs and output to highlight")
parser.add_argument("-f", "--format", default="dot", help="File type")
parser.add_argument("-i", "--ignore", action="store_true")
parser.add_argument("base", help="Base tree structure")
parser.add_argument("output", help="Output file")

args = parser.parse_args()


def write(tree, output, format):
    try:
        tree.parse()
        tree.write(output, format=format)
    except ValueError as e:
        print "Error: Could not find dependency of %s: %s" % e.args


def write_interactive(tree, output, format):

    write(tree, output, format)

    class WatchdogHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            write(tree, output, format)

    observer = Observer()
    observer.schedule(WatchdogHandler(), path=tree.path, recursive=True)
    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


tree = Tree(args.base, args.highlight, args.ignore)
(write_interactive if args.monitor else write)(tree, args.output, args.format)
