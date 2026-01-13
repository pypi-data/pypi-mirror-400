# coding=utf-8
#
# Copyright © Splunk, Inc. All Rights Reserved.

from __future__ import absolute_import, division, print_function, unicode_literals
import sys

from builtins import object

from inspect import getmembers, isclass
from os import path

from .. utils import SlimLogger, encode_filename, encode_series, slim_configuration

if sys.version_info < (3, 0):
    import imp
else:
    import importlib.util as imp


class AppConfigurationValidationPlugin(object):

    def fix_up(self, stanza, placement, position):
        declarations = stanza.setting_declarations
        try:
            disabled = declarations['disabled']
        except KeyError:
            from ._configuration_spec import AppConfigurationSettingDeclaration  # nopep8, pylint: disable=import-outside-toplevel
            disabled = AppConfigurationSettingDeclaration.Section('disabled', '<bool>', placement, position)
            declarations['disabled'] = disabled
        else:
            disabled._placement = placement  # pylint: disable=protected-access

    @staticmethod
    def _load_module(name, path_name):
        """Load a module using importlib."""
        try:
            if sys.version_info < (3, 0):
                # Python 2 use the deprecated "imp" module.
                return imp.load_source(name, path_name)
            else:
                spec = imp.spec_from_file_location(name, path_name)
                if spec is None:
                    raise ImportError("Could not find module spec for {}".format(name))

                module = imp.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            raise ImportError("Failed to load module {}: {}".format(name, str(e)))

    @staticmethod
    def get(configuration, app_root):  # pylint: disable=inconsistent-return-statements
        """ Returns the app configuration validation plugin for the named configuration object.

        The search for a plugin proceeds from `{app_root}/README` to `{slim_home}/config/conf-specs`. If no specific
        plugin is found, the default plugin represented by this class is returned. The default plugin ensures that
        the `disabled` setting is added to each stanza in the named `configuration`.

        :param configuration: Configuration object name.
        :type configuration: string

        :param app_root: App root directory name.
        :type app_root: string

        :return: app configuration validation plugin for the named configuration object.
        :rtype: AppConfigurationValidationPlugin

        """
        cls = AppConfigurationValidationPlugin  # pylint: disable=inconsistent-return-statements

        try:
            plugin = cls._instances[configuration]  # pylint: disable=protected-access

        except KeyError:
            plugin_path = [path.join(app_root, 'README'), slim_configuration.configuration_spec_path]
            plugin = None

            for search_path in plugin_path:
                module_path = path.join(search_path, "{0}.py".format(configuration))
                if path.exists(module_path):
                    try:
                        plugin_name = 'slim.app.configuration_validation_plugin.' + configuration
                        plugin_module = cls._load_module(plugin_name, module_path)

                        def predicate(member):
                            return isclass(member) and issubclass(member, cls) and member.__module__ == plugin_name

                        plugins = getmembers(plugin_module, predicate)

                        if len(plugins) == 0:
                            SlimLogger.fatal(
                                'Expected to find an AppConfigurationValidation-derived class in ',
                                plugin_name, ' at ',
                                encode_filename(module_path)
                            )
                            return  # SlimLogger.fatal does not return, but this quiets pylint

                        if len(plugins) >= 2:
                            SlimLogger.fatal(
                                'Expected to find a single AppConfigurationValidation-derived class in ',
                                plugin_name, ' at ',
                                encode_filename(module_path), ', not ', len(plugins), ': ',
                                encode_series(plugin[0] for plugin in plugins)
                            )
                            return  # SlimLogger.fatal does not return, but this quiets pylint

                        plugin_class = plugins[0][1]
                        plugin = plugin_class()
                        break

                    except ImportError as error:
                        SlimLogger.fatal(
                            'Could not load ', plugin_name, ' from ',
                            encode_filename(module_path), ': ', error
                        )
                        return

            if plugin is None:
                plugin = cls._default

            cls._instances[configuration] = plugin

        return plugin

    _instances = dict()
    _default = None

AppConfigurationValidationPlugin._default = AppConfigurationValidationPlugin()  # pylint: disable=protected-access
