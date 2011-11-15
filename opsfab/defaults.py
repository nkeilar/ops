"""
Environment defaults for ops deployment fabfile.
"""
#!/usr/bin/env python
from fabric.api import env

env.unit = "chef"
env.scm = "git@github.com:bueda/chef"

env.security_groups = ["default", "ssh"]
env.key_name = "noshly.pem"
env.region = 'us-east-1a'
env.chef_roles = ["base"]
