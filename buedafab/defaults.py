"""Set sane default values for many of the keys required by buedafab's commands
and utilities. Any of these can be overridden by setting a custom value in a
project's fabfile that uses buedafab.
"""
from fabric.api import env, warn
import datetime
import os

env.time_now = datetime.datetime.now().strftime("%H%M%S-%d%m%Y")
env.version_pattern = r'^v\d+(\.\d+)+?$'
env.pip_install_command = 'pip install -i http://d.pypi.python.org/simple'

# Within the target directory on the remote server, subdirectory for the a/b
# releases directory.
env.releases_root = 'releases'

# Name of the symlink to the current release
env.current_release_symlink = 'current'
env.current_release_path = os.path.join(env.releases_root,
        env.current_release_symlink)

# Names of the directories to alternate between in the releases directory
env.release_paths = ('a', 'b',)

# Name of the virtualenv to create within each release directory
env.virtualenv = 'env'

# Default SSH port for all servers
env.ssh_port = 22

# Default commit ID to deploy if none is specificed, e.g. fab development deploy
env.default_revision = 'HEAD'

# User and group that owns the deployed files - you probably want to change this
env.deploy_user = 'ubuntu'
env.deploy_group = 'ubuntu'

env.master_remote = 'origin'
env.settings = "settings.py"
env.extra_fixtures = ["permissions"]

# To avoid using hasattr(env, 'the_attr') everywhere, set some blank defaults
env.private_requirements = []
env.package_installation_scripts = []
env.crontab = None
env.updated_db = False
env.migrated = False
env.celeryd = None
env.celeryd_beat_option = "-B"
env.celeryd_options = "-E"
env.hoptoad_api_key = None
env.campfire_token = None
env.sha_url_template = None
env.deployed_version = None
env.scm_url_template = None
env.extra_deploy_tasks = []
env.extra_setup_tasks = []

# TODO open source the now deleted upload_to_s3 utils
if 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
    try:
        import boto.ec2
        import boto.ec2.elb
        import boto.s3
        import boto.s3.connection
        import boto.s3.key
    except ImportError:
        warn('boto not installed -- required to use S3 or EC2. '
                'Try running "fab setup" from the root of the ops repo')
    else:
        env.aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
        env.aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
        env.elb_connection = boto.ec2.elb.ELBConnection(
                env.aws_access_key, env.aws_secret_key)
        env.ec2_connection = boto.ec2.EC2Connection(
                    env.aws_access_key, env.aws_secret_key)
        # TODO this recently became required as a workaround?
        env.ec2_connection.SignatureVersion = '1'
        _s3_connection = boto.s3.connection.S3Connection(env.aws_access_key,
                env.aws_secret_key)

#        env.s3_bucket_name = 'noshly.deploy'
#        _bucket = _s3_connection.get_bucket(env.s3_bucket_name)
#        env.s3_key = boto.s3.connection.Key(_bucket)
else:
    warn('No S3 key set. To use S3 or EC2 for deployment, '
        'you will need to set one -- '
        'see https://github.com/bueda/buedaweb/wikis/deployment-with-fabric')
