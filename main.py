import sys

from runner import Runner

HELP_TEXT = """My Notifier
Simply wrap the command with arguments needed to run your long running process.
Example: my_notifier python my_long_running_process.py --arg1=value1 --arg2=value2
"""

if __name__ == "__main__":
    print("Starting with my notifier")
    args = sys.argv[1:]
    if len(args) == 1 and (args[0] == "--help" or args[0] == "-h"):
        print(HELP_TEXT)
    else:
        print("Passed in arguments: ", args)
        runner = Runner(args)
        runner.run()
        print("Process finished")
