from fabric.api import require, env, local, warn, settings, cd
import os

from buedafab.operations import run, exists, conditional_rm, sed, sudo
from buedafab import environments, deploy, utils

def setup():
    environments.localhost()
    local('git submodule init')
    local('git submodule update')
    with settings(virtualenv=None):
        for package in deploy.packages._read_private_requirements():
            deploy.packages._install_private_package(*package)
    deploy.packages._install_pip_requirements(env.root_dir)

def enable():
    env.toggle = True

def disable():
    env.toggle = False

def maintenancemode():
    require('toggle', provided_by=[enable, disable])
    require('settings')
    require('path')
    require('current_release_path')
    require('settings')

    settings_file = os.path.join(utils.absolute_release_path(), env.settings)
    if exists(settings_file):
        sed(settings_file, '(MAINTENANCE_MODE = )(False|True)',
                '\\1%(toggle)s' % env)
        restart_webserver()
    else:
        warn('Settings file %s could not be found' % settings_file)

def rollback():
    """
    Swaps the current and previous release that was deployed.
    """
    require('path')
    with cd(os.path.join(env.path, env.releases_root)):
        previous_link = deploy.release.alternative_release_path()
        conditional_rm(env.current_release_symlink)
        run('ln -s %s %s' % (previous_link, env.current_release_symlink))
    deploy.cron.conditional_install_crontab(utils.absolute_release_path(),
            env.crontab, env.deploy_user)
    restart_webserver()

def restart_webserver(hard_reset=False):
    """
    Restart the Django application webserver
    """
    if hard_reset:
        sudo('apache2ctl graceful')
    else:
        require('path')
        require('wsgi')
        run('touch %s' % os.path.join(utils.absolute_release_path(), env.wsgi))