# -*- coding: utf-8; -*-

import os
import shutil
import tempfile
from unittest import TestCase

from wuttjamaican.conf import WuttaConfig
from wuttjamaican.testing import ConfigTestCase, DataTestCase

try:
    import sqlalchemy as sa
    from sqlalchemy import orm
    from sqlalchemy.engine import Engine
    from sqlalchemy.pool import NullPool
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig
    from alembic.script import ScriptDirectory
    from wuttjamaican.db import conf
    from wuttjamaican.db import conf as mod
except ImportError:
    pass
else:

    class TestGetEngines(TestCase):

        def setUp(self):
            self.tempdir = tempfile.mkdtemp()

        def tearDown(self):
            shutil.rmtree(self.tempdir)

        def write_file(self, filename, content):
            path = os.path.join(self.tempdir, filename)
            with open(path, "wt") as f:
                f.write(content)
            return path

        def test_no_default(self):
            myfile = self.write_file("my.conf", "")
            config = WuttaConfig([myfile])
            self.assertEqual(conf.get_engines(config, "wuttadb"), {})

        def test_default(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [wuttadb]
    default.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "wuttadb")
            self.assertEqual(len(result), 1)
            self.assertIn("default", result)
            engine = result["default"]
            self.assertEqual(engine.dialect.name, "sqlite")

        def test_default_fallback(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [wuttadb]
    sqlalchemy.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "wuttadb")
            self.assertEqual(len(result), 1)
            self.assertIn("default", result)
            engine = result["default"]
            self.assertEqual(engine.dialect.name, "sqlite")

        def test_other(self):
            myfile = self.write_file(
                "my.conf",
                """\
    [otherdb]
    keys = first, second
    first.url = sqlite://
    second.url = sqlite://
    """,
            )
            config = WuttaConfig([myfile])
            result = conf.get_engines(config, "otherdb")
            self.assertEqual(len(result), 2)
            self.assertIn("first", result)
            self.assertIn("second", result)

    class TestGetSetting(TestCase):

        def setUp(self):
            Session = orm.sessionmaker()
            engine = sa.create_engine("sqlite://")
            self.session = Session(bind=engine)
            self.session.execute(
                sa.text(
                    """
            create table setting (
                    name varchar(255) primary key,
                    value text
            );
            """
                )
            )

        def tearDown(self):
            self.session.close()

        def test_basic_value(self):
            self.session.execute(sa.text("insert into setting values ('foo', 'bar');"))
            value = conf.get_setting(self.session, "foo")
            self.assertEqual(value, "bar")

        def test_missing_value(self):
            value = conf.get_setting(self.session, "foo")
            self.assertIsNone(value)

    class TestMakeEngineFromConfig(TestCase):

        def test_basic(self):
            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertIsInstance(engine, Engine)

        def test_poolclass(self):

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertNotIsInstance(engine.pool, NullPool)

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                    "sqlalchemy.poolclass": "sqlalchemy.pool:NullPool",
                }
            )
            self.assertIsInstance(engine.pool, NullPool)

        def test_pool_pre_ping(self):

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                }
            )
            self.assertFalse(engine.pool._pre_ping)

            engine = conf.make_engine_from_config(
                {
                    "sqlalchemy.url": "sqlite://",
                    "sqlalchemy.pool_pre_ping": "true",
                }
            )
            self.assertTrue(engine.pool._pre_ping)

    class TestMakeAlembicConfig(ConfigTestCase):

        def test_defaults(self):

            # without config file
            self.assertFalse(self.config.files_read)
            alembic = mod.make_alembic_config(self.config)
            self.assertIsInstance(alembic, AlembicConfig)
            self.assertIsNone(alembic.config_file_name)
            self.assertIsNone(alembic.get_main_option("script_location"))
            self.assertIsNone(alembic.get_main_option("version_locations"))

            # with config file
            path = self.write_file("test.ini", "[alembic]")
            self.config.files_read = [path]
            alembic = mod.make_alembic_config(self.config)
            self.assertIsInstance(alembic, AlembicConfig)
            self.assertEqual(alembic.config_file_name, path)
            self.assertIsNone(alembic.get_main_option("script_location"))
            self.assertIsNone(alembic.get_main_option("version_locations"))

        def test_configured(self):
            self.config.setdefault("alembic.script_location", "wuttjamaican.db:alembic")
            self.config.setdefault(
                "alembic.version_locations", "wuttjamaican.db:alembic/versions"
            )

            alembic = mod.make_alembic_config(self.config)
            self.assertIsInstance(alembic, AlembicConfig)
            self.assertEqual(
                alembic.get_main_option("script_location"), "wuttjamaican.db:alembic"
            )
            self.assertEqual(
                alembic.get_main_option("version_locations"),
                "wuttjamaican.db:alembic/versions",
            )

    class TestGetAlembicScriptdir(ConfigTestCase):

        def test_basic(self):
            self.config.setdefault("alembic.script_location", "wuttjamaican.db:alembic")
            self.config.setdefault(
                "alembic.version_locations", "wuttjamaican.db:alembic/versions"
            )

            # can provide alembic config
            alembic = mod.make_alembic_config(self.config)
            script = mod.get_alembic_scriptdir(self.config, alembic)
            self.assertIsInstance(script, ScriptDirectory)

            # but also can omit it
            script = mod.get_alembic_scriptdir(self.config)
            self.assertIsInstance(script, ScriptDirectory)

    class TestCheckAlembicCurrent(DataTestCase):

        def make_config(self, **kwargs):
            sqlite_path = self.write_file("test.sqlite", "")
            self.sqlite_engine_url = f"sqlite:///{sqlite_path}"

            config_path = self.write_file(
                "test.ini",
                f"""
[wutta.db]
default.url = {self.sqlite_engine_url}

[alembic]
script_location = wuttjamaican.db:alembic
version_locations = wuttjamaican.db:alembic/versions
""",
            )

            return super().make_config([config_path], **kwargs)

        def test_basic(self):
            alembic = mod.make_alembic_config(self.config)
            self.assertIsNotNone(alembic.get_main_option("script_location"))
            self.assertIsNotNone(alembic.get_main_option("version_locations"))

            # false by default, since tests use MetaData.create_all()
            # instead of migrations for setup
            self.assertFalse(mod.check_alembic_current(self.config, alembic))

            # and to further prove the point, alembic_version table is missing
            self.assertEqual(
                self.session.execute(sa.text("select count(*) from person")).scalar(),
                0,
            )
            self.assertRaises(
                sa.exc.OperationalError,
                self.session.execute,
                sa.text("select count(*) from alembic_version"),
            )

            # but we can 'stamp' the DB to declare its current revision
            alembic_command.stamp(alembic, "heads")

            # now the alembic_version table exists
            self.assertEqual(
                self.session.execute(
                    sa.text("select count(*) from alembic_version")
                ).scalar(),
                1,
            )

            # and now Alembic knows we are current
            self.assertTrue(mod.check_alembic_current(self.config, alembic))
