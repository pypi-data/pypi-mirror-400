import asyncio

from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from tortoise import Tortoise

from database import init_database
from grabber.controllers.base import Base

# configuration defaults
CONFIG = init_defaults("grabber")


class MyAppError(Exception):
    """Generic errors."""

    pass


class MyApp(App):
    """A simple python command line utility to download images"""

    class Meta:
        label = "grabber"

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            "colorlog",
            "jinja2",
        ]

        # set the log handler
        log_handler = "colorlog"

        # set the output handler
        output_handler = "jinja2"

        # register handlers
        handlers = [
            Base,
        ]


class MyAppTest(TestApp, MyApp):
    """A sub-class of MyApp that is better suited for testing."""

    class Meta:
        label = "test"


async def start():
    with MyApp() as app:
        try:
            app.run()

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except MyAppError as e:
            print("MyAppError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print("\n%s" % e)
            app.exit_code = 0


def main() -> None:
    asyncio.run(start())
