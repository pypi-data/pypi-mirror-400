# -*- coding: utf-8; -*-

import os
import sys
from unittest.mock import patch, MagicMock

import pytest
from mako.lookup import TemplateLookup

from wuttjamaican import install as mod
from wuttjamaican.testing import ConfigTestCase


class TestInstallHandler(ConfigTestCase):
    def make_handler(self, **kwargs):
        return mod.InstallHandler(self.config, **kwargs)

    def test_constructor(self):
        handler = self.make_handler()
        self.assertEqual(handler.pkg_name, "poser")
        self.assertEqual(handler.app_title, "poser")
        self.assertEqual(handler.pypi_name, "poser")
        self.assertEqual(handler.egg_name, "poser")

    def test_run(self):
        handler = self.make_handler()
        with patch.object(handler, "show_welcome") as show_welcome:
            with patch.object(handler, "sanity_check") as sanity_check:
                with patch.object(handler, "do_install_steps") as do_install_steps:
                    handler.run()
                    show_welcome.assert_called_once_with()
                    sanity_check.assert_called_once_with()
                    do_install_steps.assert_called_once_with()

    def test_show_welcome(self):
        handler = self.make_handler()
        with patch.object(mod, "sys") as sys:
            with patch.object(handler, "rprint") as rprint:
                with patch.object(handler, "prompt_bool") as prompt_bool:
                    # user continues
                    prompt_bool.return_value = True
                    handler.show_welcome()
                    self.assertFalse(sys.exit.called)

                    # user aborts
                    prompt_bool.return_value = False
                    handler.show_welcome()
                    sys.exit.assert_called_once_with(1)

    def test_sanity_check(self):
        handler = self.make_handler()
        with patch.object(mod, "sys") as sys:
            with patch.object(mod, "os") as os:
                with patch.object(handler, "rprint") as rprint:
                    # pretend appdir does not exist
                    os.path.exists.return_value = False
                    handler.sanity_check()
                    self.assertFalse(sys.exit.called)

                    # pretend appdir does exist
                    os.path.exists.return_value = True
                    handler.sanity_check()
                    sys.exit.assert_called_once_with(2)

    def test_do_install_steps(self):
        handler = self.make_handler()
        db_url = f"sqlite:///{self.tempdir}/poser.sqlite"

        with patch.object(handler, "prompt_user_for_context") as prompt_user:
            prompt_user.return_value = {"db_url": db_url, "wants_continuum": False}
            with patch.object(handler, "make_appdir") as make_appdir:
                with patch.object(handler, "install_db_schema") as install_schema:

                    # nb. just for sanity/coverage
                    self.assertFalse(handler.schema_installed)
                    install_schema.return_value = True
                    handler.do_install_steps()
                    prompt_user.assert_called_once()
                    make_appdir.assert_called_once()
                    install_schema.assert_called_once_with(db_url)
                    self.assertTrue(handler.schema_installed)

    def test_prompt_user_for_context(self):
        db_url = f"sqlite:///{self.tempdir}/poser.sqlite"
        with patch.object(mod.InstallHandler, "get_db_url", return_value=db_url):

            # should prompt for continuum by default
            handler = self.make_handler()
            with patch.object(handler, "prompt_bool") as prompt_bool:
                prompt_bool.return_value = True
                context = handler.prompt_user_for_context()
                prompt_bool.assert_called_once_with(
                    "use continuum for data versioning?", default=False
                )
                self.assertEqual(context, {"db_url": db_url, "wants_continuum": True})

            # should not prompt if continuum flag already true
            handler = self.make_handler()
            with patch.object(handler, "wants_continuum", new=True):
                with patch.object(handler, "prompt_bool") as prompt_bool:
                    context = handler.prompt_user_for_context()
                    prompt_bool.assert_not_called()
                    self.assertEqual(
                        context, {"db_url": db_url, "wants_continuum": True}
                    )

            # should not prompt if continuum flag already false
            handler = self.make_handler()
            with patch.object(handler, "wants_continuum", new=False):
                with patch.object(handler, "prompt_bool") as prompt_bool:
                    context = handler.prompt_user_for_context()
                    prompt_bool.assert_not_called()
                    self.assertEqual(
                        context, {"db_url": db_url, "wants_continuum": False}
                    )

            # should not prompt if continuum pkg missing...
            handler = self.make_handler()
            with patch("builtins.__import__", side_effect=ImportError):
                with patch.object(handler, "prompt_bool") as prompt_bool:
                    context = handler.prompt_user_for_context()
                    prompt_bool.assert_not_called()
                    self.assertEqual(
                        context, {"db_url": db_url, "wants_continuum": False}
                    )

    def test_get_db_url(self):
        try:
            import sqlalchemy
            from wuttjamaican.db.util import SA2
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        handler = self.make_handler()

        # url from dbinfo is returned, if present
        dbinfo = {"db_url": "sqlite:///"}
        with patch.object(handler, "get_dbinfo", return_value=dbinfo):
            db_url = handler.get_db_url()
            self.assertEqual(db_url, "sqlite:///")

        # or url will be assembled from dbinfo parts
        dbinfo = {
            "dbtype": "postgresql",
            "dbhost": "localhost",
            "dbport": 5432,
            "dbname": "poser",
            "dbuser": "poser",
            "dbpass": "seekrit",
        }
        with patch.object(handler, "get_dbinfo", return_value=dbinfo):
            with patch.object(handler, "test_db_connection", return_value=None):
                db_url = handler.get_db_url()
                seekrit = "***" if SA2 else "seekrit"
                self.assertEqual(
                    str(db_url),
                    f"postgresql+psycopg2://poser:{seekrit}@localhost:5432/poser",
                )

        # now we test the "test db connection" feature
        dbinfo = {"db_url": "sqlite:///"}
        with patch.object(handler, "get_dbinfo", return_value=dbinfo):
            with patch.object(handler, "test_db_connection") as test_db_connection:
                with patch.object(handler, "rprint") as rprint:
                    with patch.object(mod, "sys") as sys:

                        # pretend user gave bad dbinfo; should exit
                        test_db_connection.return_value = "bad dbinfo"
                        sys.exit.side_effect = RuntimeError
                        self.assertRaises(RuntimeError, handler.get_db_url)
                        sys.exit.assert_called_once_with(1)

                        # pretend user gave good dbinfo
                        sys.exit.reset_mock()
                        test_db_connection.return_value = None
                        db_url = handler.get_db_url()
                        self.assertFalse(sys.exit.called)
                        rprint.assert_called_with("[bold green]good[/bold green]")
                        self.assertEqual(str(db_url), "sqlite:///")

    def test_get_dbinfo(self):
        try:
            import sqlalchemy
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        from wuttjamaican.db.util import SA2

        handler = self.make_handler()

        def prompt_generic(info, default=None, is_password=False):
            if info in ("db name", "db user"):
                return "poser"
            if is_password:
                return "seekrit"
            return default

        with patch.object(handler, "prompt_generic", side_effect=prompt_generic):

            dbinfo = handler.get_dbinfo()
            self.assertEqual(
                dbinfo,
                {
                    "dbtype": "postgresql",
                    "dbhost": "localhost",
                    "dbport": "5432",
                    "dbname": "poser",
                    "dbuser": "poser",
                    "dbpass": "seekrit",
                },
            )

    def test_make_db_url(self):
        try:
            import sqlalchemy
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        from wuttjamaican.db.util import SA2

        handler = self.make_handler()
        seekrit = "***" if SA2 else "seekrit"

        url = handler.make_db_url(
            dict(
                dbtype="postgresql",
                dbhost="localhost",
                dbport="5432",
                dbname="poser",
                dbuser="poser",
                dbpass="seekrit",
            )
        )
        self.assertEqual(
            str(url), f"postgresql+psycopg2://poser:{seekrit}@localhost:5432/poser"
        )

        url = handler.make_db_url(
            dict(
                dbtype="mysql",
                dbhost="localhost",
                dbport="3306",
                dbname="poser",
                dbuser="poser",
                dbpass="seekrit",
            )
        )
        self.assertEqual(
            str(url), f"mysql+mysqlconnector://poser:{seekrit}@localhost:3306/poser"
        )

    def test_test_db_connection(self):
        try:
            import sqlalchemy as sa
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        handler = self.make_handler()

        # db does not exist
        result = handler.test_db_connection("sqlite:///bad/url/should/not/exist")
        self.assertIn("unable to open database file", result)

        # db is setup
        url = f"sqlite:///{self.tempdir}/db.sqlite"
        engine = sa.create_engine(url)
        with engine.begin() as cxn:
            cxn.execute(sa.text("create table whatever (id int primary key);"))
        self.assertIsNone(handler.test_db_connection(url))

    def test_make_template_context(self):
        handler = self.make_handler()

        # can handle dburl as string
        db_url = "sqlite:///poser.sqlite"
        context = handler.make_template_context(db_url=db_url)
        self.assertEqual(context["envdir"], sys.prefix)
        self.assertEqual(context["pkg_name"], "poser")
        self.assertEqual(context["app_title"], "poser")
        self.assertEqual(context["pypi_name"], "poser")
        self.assertEqual(context["egg_name"], "poser")
        self.assertEqual(context["appdir"], os.path.join(sys.prefix, "app"))
        self.assertEqual(context["db_url"], "sqlite:///poser.sqlite")

        try:
            import sqlalchemy as sa
        except ImportError:
            pytest.skip("remainder of test is not relevant without sqlalchemy")

        # but also can handle dburl as object
        db_url = sa.create_engine("sqlite:///poser.sqlite").url
        context = handler.make_template_context(db_url=db_url)
        self.assertEqual(context["envdir"], sys.prefix)
        self.assertEqual(context["pkg_name"], "poser")
        self.assertEqual(context["app_title"], "poser")
        self.assertEqual(context["pypi_name"], "poser")
        self.assertEqual(context["egg_name"], "poser")
        self.assertEqual(context["appdir"], os.path.join(sys.prefix, "app"))
        self.assertEqual(context["db_url"], "sqlite:///poser.sqlite")

    def test_make_appdir(self):
        handler = self.make_handler()
        handler.templates = TemplateLookup(
            directories=[
                self.app.resource_path("wuttjamaican:templates/install"),
            ]
        )
        db_url = "sqlite:///poser.sqlite"
        context = handler.make_template_context(db_url=db_url)
        handler.make_appdir(context, appdir=self.tempdir)
        wutta_conf = os.path.join(self.tempdir, "wutta.conf")
        with open(wutta_conf, "rt") as f:
            self.assertIn("default.url = sqlite:///poser.sqlite", f.read())

    def test_install_db_schema(self):
        try:
            import sqlalchemy as sa
        except ImportError:
            pytest.skip("test is not relevant without sqlalchemy")

        handler = self.make_handler()
        db_url = f"sqlite:///{self.tempdir}/poser.sqlite"

        wutta_conf = self.write_file(
            "wutta.conf",
            f"""
[wutta.db]
default.url = {db_url}
""",
        )

        # convert to proper URL object
        db_url = sa.create_engine(db_url).url

        with patch.object(mod, "subprocess") as subprocess:
            # user declines offer to install schema
            with patch.object(handler, "prompt_bool", return_value=False):
                self.assertFalse(handler.install_db_schema(db_url, appdir=self.tempdir))

            # user agrees to install schema
            with patch.object(handler, "prompt_bool", return_value=True):
                self.assertTrue(handler.install_db_schema(db_url, appdir=self.tempdir))
                subprocess.check_call.assert_called_once_with(
                    [
                        os.path.join(sys.prefix, "bin", "alembic"),
                        "-c",
                        wutta_conf,
                        "upgrade",
                        "heads",
                    ]
                )

    def test_show_goodbye(self):
        handler = self.make_handler()
        with patch.object(handler, "rprint") as rprint:
            handler.schema_installed = True
            handler.show_goodbye()
            rprint.assert_any_call(
                "\n\t[bold green]initial setup is complete![/bold green]"
            )
            rprint.assert_any_call("\t[blue]bin/wutta -c app/web.conf webapp -r[/blue]")

    def test_require_prompt_toolkit_installed(self):
        # nb. this assumes we *do* have prompt_toolkit installed
        handler = self.make_handler()
        with patch.object(mod, "subprocess") as subprocess:
            handler.require_prompt_toolkit(answer="Y")
            self.assertFalse(subprocess.check_call.called)

    def test_require_prompt_toolkit_missing(self):
        handler = self.make_handler()
        orig_import = __import__
        stuff = {"attempts": 0}

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "prompt_toolkit":
                # nb. pretend this is not installed
                raise ImportError
            return orig_import(name, globals, locals, fromlist, level)

        # prompt_toolkit not installed, and user declines offer to install
        with patch("builtins.__import__", side_effect=mock_import):
            with patch.object(mod, "subprocess") as subprocess:
                with patch.object(mod, "sys") as sys:
                    sys.exit.side_effect = RuntimeError
                    self.assertRaises(
                        RuntimeError, handler.require_prompt_toolkit, answer="N"
                    )
                    self.assertFalse(subprocess.check_call.called)
                    sys.stderr.write.assert_called_once_with(
                        "prompt_toolkit is required; aborting\n"
                    )
                    sys.exit.assert_called_once_with(1)

    def test_require_prompt_toolkit_missing_then_installed(self):
        handler = self.make_handler()
        orig_import = __import__
        stuff = {"attempts": 0}

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "prompt_toolkit":
                stuff["attempts"] += 1
                if stuff["attempts"] == 1:
                    # nb. pretend this is not installed
                    raise ImportError
                return orig_import("prompt_toolkit")
            return orig_import(name, globals, locals, fromlist, level)

        # prompt_toolkit not installed, and user declines offer to install
        with patch("builtins.__import__", side_effect=mock_import):
            with patch.object(mod, "subprocess") as subprocess:
                with patch.object(mod, "sys") as sys:
                    sys.executable = "python"
                    handler.require_prompt_toolkit(answer="Y")
                    subprocess.check_call.assert_called_once_with(
                        ["python", "-m", "pip", "install", "prompt_toolkit"]
                    )
                    self.assertFalse(sys.exit.called)
                    self.assertEqual(stuff["attempts"], 2)

    def test_prompt_generic(self):
        handler = self.make_handler()
        style = handler.get_prompt_style()
        orig_import = __import__
        mock_prompt = MagicMock()

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "prompt_toolkit":
                if fromlist == ("prompt",):
                    return MagicMock(prompt=mock_prompt)
            return orig_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=mock_import):
            with patch.object(handler, "get_prompt_style", return_value=style):
                with patch.object(handler, "rprint") as rprint:
                    # no input or default value
                    mock_prompt.return_value = ""
                    result = handler.prompt_generic("foo")
                    self.assertIsNone(result)
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", ": ")],
                        style=style,
                        is_password=False,
                    )

                    # fallback to default value
                    mock_prompt.reset_mock()
                    mock_prompt.return_value = ""
                    result = handler.prompt_generic("foo", default="baz")
                    self.assertEqual(result, "baz")
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", " [baz]: ")],
                        style=style,
                        is_password=False,
                    )

                    # text input value
                    mock_prompt.reset_mock()
                    mock_prompt.return_value = "bar"
                    result = handler.prompt_generic("foo")
                    self.assertEqual(result, "bar")
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", ": ")],
                        style=style,
                        is_password=False,
                    )

                    # bool value (no default; true input)
                    mock_prompt.reset_mock()
                    mock_prompt.return_value = "Y"
                    result = handler.prompt_generic("foo", is_bool=True)
                    self.assertTrue(result)
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", ": ")],
                        style=style,
                        is_password=False,
                    )

                    # bool value (no default; false input)
                    mock_prompt.reset_mock()
                    mock_prompt.return_value = "N"
                    result = handler.prompt_generic("foo", is_bool=True)
                    self.assertFalse(result)
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", ": ")],
                        style=style,
                        is_password=False,
                    )

                    # bool value (default; no input)
                    mock_prompt.reset_mock()
                    mock_prompt.return_value = ""
                    result = handler.prompt_generic("foo", is_bool=True, default=True)
                    self.assertTrue(result)
                    mock_prompt.assert_called_once_with(
                        [("", "\n"), ("class:bold", "foo"), ("", " [Y]: ")],
                        style=style,
                        is_password=False,
                    )

                    # bool value (bad input)
                    mock_prompt.reset_mock()
                    counter = {"attempts": 0}

                    def omg(*args, **kwargs):
                        counter["attempts"] += 1
                        if counter["attempts"] == 1:
                            # nb. bad input first time we ask
                            return "doesnotmakesense"
                        # nb. but good input after that
                        return "N"

                    mock_prompt.side_effect = omg
                    result = handler.prompt_generic("foo", is_bool=True)
                    self.assertFalse(result)
                    # nb. user was prompted twice
                    self.assertEqual(mock_prompt.call_count, 2)

                    # Ctrl+C
                    mock_prompt.reset_mock()
                    mock_prompt.side_effect = KeyboardInterrupt
                    with patch.object(mod, "sys") as sys:
                        sys.exit.side_effect = RuntimeError
                        self.assertRaises(RuntimeError, handler.prompt_generic, "foo")
                        sys.exit.assert_called_once_with(1)

                    # Ctrl+D
                    mock_prompt.reset_mock()
                    mock_prompt.side_effect = EOFError
                    with patch.object(mod, "sys") as sys:
                        sys.exit.side_effect = RuntimeError
                        self.assertRaises(RuntimeError, handler.prompt_generic, "foo")
                        sys.exit.assert_called_once_with(1)

                    # missing required value
                    mock_prompt.reset_mock()
                    counter = {"attempts": 0}

                    def omg(*args, **kwargs):
                        counter["attempts"] += 1
                        if counter["attempts"] == 1:
                            # nb. no input first time we ask
                            return ""
                        # nb. but good input after that
                        return "bar"

                    mock_prompt.side_effect = omg
                    result = handler.prompt_generic("foo", required=True)
                    self.assertEqual(result, "bar")
                    # nb. user was prompted twice
                    self.assertEqual(mock_prompt.call_count, 2)

    def test_prompt_bool(self):
        handler = self.make_handler()
        orig_import = __import__
        mock_prompt = MagicMock()

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "prompt_toolkit":
                if fromlist == ("prompt",):
                    return MagicMock(prompt=mock_prompt)
            return orig_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=mock_import):
            with patch.object(handler, "rprint") as rprint:
                # no default; true input
                mock_prompt.reset_mock()
                mock_prompt.return_value = "Y"
                result = handler.prompt_bool("foo")
                self.assertTrue(result)
                mock_prompt.assert_called_once()

                # no default; false input
                mock_prompt.reset_mock()
                mock_prompt.return_value = "N"
                result = handler.prompt_bool("foo")
                self.assertFalse(result)
                mock_prompt.assert_called_once()

                # default; no input
                mock_prompt.reset_mock()
                mock_prompt.return_value = ""
                result = handler.prompt_bool("foo", default=True)
                self.assertTrue(result)
                mock_prompt.assert_called_once()

                # bad input
                mock_prompt.reset_mock()
                counter = {"attempts": 0}

                def omg(*args, **kwargs):
                    counter["attempts"] += 1
                    if counter["attempts"] == 1:
                        # nb. bad input first time we ask
                        return "doesnotmakesense"
                    # nb. but good input after that
                    return "N"

                mock_prompt.side_effect = omg
                result = handler.prompt_bool("foo")
                self.assertFalse(result)
                # nb. user was prompted twice
                self.assertEqual(mock_prompt.call_count, 2)
