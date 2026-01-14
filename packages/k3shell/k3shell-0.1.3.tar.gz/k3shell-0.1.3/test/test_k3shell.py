#!/usr/bin/env python2
# conding: utf-8

import os
import unittest
import logging
import sys
import k3shell

# Python 3.10+ changed argparse help text from "optional arguments:" to "options:"
OPTARGS = "options:\n" if sys.version_info >= (3, 10) else "optional arguments:\n"


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.out_buf = os.path.join(os.getcwd(), "out_buf")
        self.backup_argv = sys.argv
        sys.argv = ["python"]

        logging.basicConfig(level=logging.DEBUG, filename="/home/kanade/testshell.log", filemode="w")

    def tearDown(self):
        sys.argv = self.backup_argv
        try:
            os.remove(self.out_buf)
        except EnvironmentError as e:
            sys.stderr.write(repr(e))

    def execute_test(self, arguments, argv, out_str, exit_code):
        sys.argv.extend(argv)

        backup_stderr = sys.stderr
        backup_stdout = sys.stdout

        with open(self.out_buf, "w") as fw:
            sys.stderr = fw
            sys.stdout = fw

            try:
                k3shell.command(**arguments)
            except SystemExit as e:
                if len(e.args) > 0:
                    self.assertEqual(exit_code, e.args[0])

        sys.stderr = backup_stderr
        sys.stdout = backup_stdout

        with open(self.out_buf, "r") as fr:
            s = fr.read()
            self.assertTrue(s.startswith(out_str))

        sys.argv = sys.argv[:1]

    def test_command_no_such_command(self):
        testcases = (
            (
                {"echo": lambda *x: sys.stderr.write(repr(x))},
                [],
                "No such command: ",
                2,
            ),
            (
                {"echo": lambda *x: sys.stderr.write(repr(x))},
                ["echoo"],
                "No such command: echoo",
                2,
            ),
            (
                {"call": "not_callable"},
                ["call"],
                "No such command: call",
                2,
            ),
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.execute_test(arguments, argv, out_str, exit_code)

    def test_command_execute_error(self):
        # Note: Lambda names in error messages include qualified path in Python 3.10+
        # e.g., "TestCommand.test_command_execute_error.<locals>.<lambda>()"
        # So we only check for the error type prefix
        testcases = (
            (
                {"divi": lambda x, y: int(x) / int(y)},
                ["divi"],
                'TypeError("',
                1,
            ),
            (
                {
                    "mod": {
                        "mod_2": lambda x: int(x) % 2,
                    },
                },
                ["mod", "mod_2"],
                'TypeError("',
                1,
            ),
            (
                {"divi": lambda x, y: int(x) / int(y)},
                ["divi", "7", "0"],
                "ZeroDivisionError('division by zero'",
                1,
            ),
            (
                {"divi": lambda x, y: int(x) / int(y)},
                ["divi", "string", "number"],
                '''ValueError("invalid literal for int() with base 10: \'string\'"''',
                1,
            ),
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.execute_test(arguments, argv, out_str, exit_code)

    def test_command_execute_normal(self):
        testcases = (
            (
                {"echo_repr": lambda *x: sys.stderr.write(repr(x))},
                ["echo_repr", "hello_world"],
                "('hello_world',)",
                1,
            ),
            (
                {"divi": lambda x, y: int(x) / int(y)},
                ["divi", "7", "3"],
                "",
                1,
            ),
            (
                {
                    "mod": {
                        "mod_2": lambda x: int(x) % 2,
                    }
                },
                ["mod", "mod_2", "3"],
                "",
                1,
            ),
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.execute_test(arguments, argv, out_str, exit_code)

    def test_command_help_message(self):
        commands = {
            "echo_repr": (
                lambda x: sys.stdout.write(repr(x)),
                ("x", {"nargs": "+", "help": "just an input message"}),
            ),
            "foo": {
                "bar": lambda: sys.stdout.write("bar"),
                "bob": {
                    "plus": (
                        lambda x, y: sys.stdout.write(str(x + y)),
                        ("x", {"type": int, "help": "an int is needed"}),
                        ("y", {"type": int, "help": "an int is needed"}),
                    ),
                },
            },
            "__add_help__": {
                ("echo_repr",): "output what is input.",
                (
                    "foo",
                    "bar",
                ): 'print a "bar".',
                (
                    "foo",
                    "bob",
                    "plus",
                ): "do addition operation with 2 numbers.",
            },
            "__description__": "this is an example command.",
        }

        testcases = (
            (
                ["-h"],
                "usage: python [-h] {echo_repr,foo bar,foo bob plus} ...\n"
                + "\n"
                + "this is an example command.\n"
                + "\n"
                + "positional arguments:\n"
                + "  {echo_repr,foo bar,foo bob plus}\n"
                + "                        command(s) to select ...\n"
                + "    echo_repr           output what is input.\n"
                + '    foo bar             print a "bar".\n'
                + "    foo bob plus        do addition operation with 2 numbers.\n"
                + "\n"
                + OPTARGS
                + "  -h, --help            show this help message and exit\n",
                0,
                "use -h to get help message",
            ),
            (
                ["echo_repr", "-h"],
                "usage: python echo_repr [-h] x [x ...]\n"
                + "\n"
                + "positional arguments:\n"
                + "  x           just an input message\n"
                + "\n"
                + OPTARGS
                + "  -h, --help  show this help message and exit\n",
                0,
                "use valid command and -h to get parameter help message",
            ),
            (
                ["foo", "bar", "-h"],
                "usage: python foo bar [-h]\n" + "\n" + OPTARGS + "  -h, --help  show this help message and exit\n",
                0,
                "use valid command and -h to get parameter help message when no parameter setted.",
            ),
            (
                ["foo", "bob", "plus", "-h"],
                "usage: python foo bob plus [-h] x y\n"
                + "\n"
                + "positional arguments:\n"
                + "  x           an int is needed\n"
                + "  y           an int is needed\n"
                + "\n"
                + OPTARGS
                + "  -h, --help  show this help message and exit\n",
                0,
                "use valid command and -h to get parameter help message when many parameters setted.",
            ),
            (
                ["echo_repr", "hello", "world"],
                "['hello', 'world']",
                1,
                "run with help message setted.",
            ),
            (
                ["foo", "bar"],
                "bar",
                1,
                "run with help message setted and no parameter help message setted.",
            ),
            (
                ["foo", "bob", "plus", "1", "2"],
                "3",
                1,
                "run with help message setted and many parameter help messages setted.",
            ),
            (
                ["foo", "bar", "error"],
                "usage: python [-h] {echo_repr,foo bar,foo bob plus} ...\n"
                + "python: error: unrecognized arguments: error\n",
                2,
                "error when use extra arguments.",
            ),
            (
                ["foo", "bob", "plus", "1", "string"],
                "usage: python foo bob plus [-h] x y\n"
                + "python foo bob plus: error: argument y: invalid int value: 'string'\n",
                2,
                "error when arguments has invalid type as required.",
            ),
        )

        for argv, out_str, exit_code, msg in testcases:
            self.execute_test(commands, argv, out_str, exit_code)
