# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttJamaican -  database configuration
"""

from collections import OrderedDict

import sqlalchemy as sa
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext

from wuttjamaican.util import load_object, parse_bool, parse_list


def get_engines(config, prefix):
    """
    Construct and return all database engines defined for a given
    config prefix.

    For instance if you have a config file with:

    .. code-block:: ini

       [wutta.db]
       keys = default, host
       default.url = sqlite:///tmp/default.sqlite
       host.url = sqlite:///tmp/host.sqlite

    And then you call this function to get those DB engines::

       get_engines(config, 'wutta.db')

    The result of that will be like::

       {'default': Engine(bind='sqlite:///tmp/default.sqlite'),
        'host': Engine(bind='sqlite:///tmp/host.sqlite')}

    :param config: App config object.

    :param prefix: Prefix for the config "section" which contains DB
       connection info.

    :returns: A dictionary of SQLAlchemy engines, with keys matching
       those found in config.
    """
    keys = config.get(f"{prefix}.keys", usedb=False)
    if keys:
        keys = parse_list(keys)
    else:
        keys = ["default"]

    make_engine = config.get_engine_maker()

    engines = OrderedDict()
    cfg = config.get_dict(prefix)
    for key in keys:
        key = key.strip()
        try:
            engines[key] = make_engine(cfg, prefix=f"{key}.")
        except KeyError:
            if key == "default":
                try:
                    engines[key] = make_engine(cfg, prefix="sqlalchemy.")
                except KeyError:
                    pass
    return engines


def get_setting(session, name):
    """
    Get a setting value from the DB.

    Note that this assumes (for now?) the DB contains a table named
    ``setting`` with ``(name, value)`` columns.

    :param session: App DB session.

    :param name: Name of the setting to get.

    :returns: Setting value as string, or ``None``.
    """
    sql = sa.text("select value from setting where name = :name")
    return session.execute(sql, params={"name": name}).scalar()


def make_engine_from_config(config_dict, prefix="sqlalchemy.", **kwargs):
    """
    Construct a new DB engine from configuration dict.

    This is a wrapper around upstream
    :func:`sqlalchemy:sqlalchemy.engine_from_config()`.  For even
    broader context of the SQLAlchemy
    :class:`~sqlalchemy:sqlalchemy.engine.Engine` and their
    configuration, see :doc:`sqlalchemy:core/engines`.

    The purpose of the customization is to allow certain attributes of
    the engine to be driven by config, whereas the upstream function
    is more limited in that regard.  The following in particular:

    * ``poolclass``
    * ``pool_pre_ping``

    If these options are present in the configuration dict, they will
    be coerced to appropriate Python equivalents and then passed as
    kwargs to the upstream function.

    An example config file leveraging this feature:

    .. code-block:: ini

       [wutta.db]
       default.url = sqlite:///tmp/default.sqlite
       default.poolclass = sqlalchemy.pool:NullPool
       default.pool_pre_ping = true

    Note that if present, the ``poolclass`` value must be a "spec"
    string, as required by :func:`~wuttjamaican.util.load_object()`.
    """
    config_dict = dict(config_dict)

    # convert 'poolclass' arg to actual class
    key = f"{prefix}poolclass"
    if key in config_dict and "poolclass" not in kwargs:
        kwargs["poolclass"] = load_object(config_dict.pop(key))

    # convert 'pool_pre_ping' arg to boolean
    key = f"{prefix}pool_pre_ping"
    if key in config_dict and "pool_pre_ping" not in kwargs:
        kwargs["pool_pre_ping"] = parse_bool(config_dict.pop(key))

    engine = sa.engine_from_config(config_dict, prefix, **kwargs)

    return engine


##############################
# alembic functions
##############################


def make_alembic_config(config):
    """
    Make and return a new Alembic config object, based on current app
    config.

    This tries to set the following on the Alembic config:

    * :attr:`~alembic:alembic.config.Config.config_file_name` - set to
      app's primary config file
    * main option ``script_location``
    * main option ``version_locations``

    The latter 2 are read normally from app config, then set on the
    Alembic config via
    :meth:`~alembic:alembic.config.Config.set_main_option()`.

    .. note::

       IIUC, Alembic should not need to attempt to read config values
       from file, as long as we're able to set the above explicitly.
       However we set the ``config_file_name`` "just in case" Alembic
       needs it, but also to ensure it is discoverable from within the
       ``env.py`` script...

       When a migration script runs, code within ``env.py`` will call
       :func:`make_config()` using the filename which it inspects from
       the Alembic config.

       (Confused yet?!)

    :returns: :class:`alembic:alembic.config.Config` instance
    """
    alembic_config = AlembicConfig()

    # TODO: not sure what we can do here besides assume the "primary"
    # config file should be used?
    if config.files_read:
        alembic_config.config_file_name = config.get_prioritized_files()[0]

    if script_location := config.get("alembic.script_location", usedb=False):
        alembic_config.set_main_option("script_location", script_location)

    if version_locations := config.get("alembic.version_locations", usedb=False):
        alembic_config.set_main_option("version_locations", version_locations)

    return alembic_config


def get_alembic_scriptdir(config, alembic_config=None):
    """
    Get a "Script Directory" object for Alembic.

    This allows for inspection of the migration scripts.

    :param config: App config object.

    :param alembic_config: Alembic config object, if you have one.
       Otherwise :func:`make_alembic_config()` will be called.

    :returns: :class:`~alembic:alembic.script.ScriptDirectory` instance
    """
    if not alembic_config:
        alembic_config = make_alembic_config(config)
    return ScriptDirectory.from_config(alembic_config)


def check_alembic_current(config, alembic_config=None):
    """
    Compare the current revisions in the :term:`app database` to those
    found in the migration scripts.

    :param config: App config object.

    :param alembic_config: Alembic config object, if you have one.
       Otherwise :func:`make_alembic_config()` will be called.

    :returns: ``True`` if the DB already has all migrations applied;
       ``False`` if not.
    """
    script = get_alembic_scriptdir(config, alembic_config)
    with config.appdb_engine.begin() as conn:
        context = MigrationContext.configure(conn)
        return set(context.get_current_heads()) == set(script.get_heads())
