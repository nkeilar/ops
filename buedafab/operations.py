from fabric.api import (run as fabric_run, local, sudo as fabric_sudo, hide,
        put as fabric_put, settings, env, require)
from fabric.contrib.files import (exists as fabric_exists, sed as fabric_sed)
import os

def chmod(path, mode, recursive=True, use_sudo=False):
    cmd = 'chmod %(mode)s %(path)s' % locals()
    if recursive:
        cmd += ' -R'
    _conditional_sudo(cmd, use_sudo)

def chgrp(path, group, recursive=True, use_sudo=False):
    cmd = 'chgrp %(group)s %(path)s' % locals()
    if recursive:
        cmd += ' -R'
    _conditional_sudo(cmd, use_sudo)

def chown(path, user, recursive=True, use_sudo=False):
    cmd = 'chown %(user)s %(path)s' % locals()
    if recursive:
        cmd += ' -R'
    _conditional_sudo(cmd, use_sudo)

def _conditional_sudo(cmd, use_sudo):
    if use_sudo:
        sudo(cmd)
    else:
        run(cmd)

def put(local_path, remote_path, mode=None):
    require('hosts')
    if 'localhost' in env.hosts:
        if (os.path.isdir(remote_path) and
                (os.path.join(remote_path, os.path.basename(local_path)))
                == local_path):
            return 0
        result = local('cp -R %s %s' % (local_path, remote_path))
        if mode:
            local('chmod -R %o %s' % (mode, remote_path))
        return result
    else:
        return fabric_put(local_path, remote_path, mode)

def run(command, shell=True, pty=False, capture=False, forward_agent=False):
    require('hosts')
    if 'localhost' in env.hosts:
        return local(command, capture)
    elif forward_agent:
        return sshagent_run(command)
    else:
        return fabric_run(command, shell, pty)

def sshagent_run(command):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.
    
    Note:: Fabric (and paramiko) can't forward your SSH agent. 
    This helper uses your system's ssh to do so.
    """

    cwd = env.get('cwd', '')
    if cwd:
        cwd = 'cd %s && ' % cwd
    real_command = cwd + command

    with settings(cwd=''):
        for h in env.hosts:
            try:
                # catch the port number to pass to ssh
                host, port = h.split(':')
                local('ssh -p %s -A %s "%s"' % (port, host, real_command))
            except ValueError:
                local('ssh -A %s "%s"' % (h, real_command))

def sudo(command, shell=True, user=None, pty=False):
    require('hosts')
    if 'localhost' in env.hosts:
        command = 'sudo %s' % command
        return local(command, capture=False)
    else:
        return fabric_sudo(command, shell, user, pty)

def exists(path, use_sudo=False, verbose=False):
    require('hosts')
    if 'localhost' in env.hosts:
        capture = not verbose
        command = 'test -e "%s"' % path
        func = use_sudo and sudo or run
        with settings(hide('everything'), warn_only=True):
            return not func(command, capture=capture).failed
    else:
        return fabric_exists(path, use_sudo, verbose)

def sed(filename, before, after, limit='', use_sudo=False, backup='.back'):
    require('hosts')
    if 'localhost' in env.hosts:
        # Code copied from Fabric - is there a better way to have Fabric's sed()
        # use our sudo and run functions?
        expr = r"sed -i%s -r -e '%ss/%s/%s/g' %s"
        # Characters to be escaped in both
        for char in "/'":
            before = before.replace(char, r'\%s' % char)
            after = after.replace(char, r'\%s' % char)
        # Characters to be escaped in replacement only (they're useful in
        # regexe in the 'before' part)
        for char in "()":
            after = after.replace(char, r'\%s' % char)
        if limit:
            limit = r'/%s/ ' % limit
        command = expr % (backup, limit, before, after, filename)
        func = use_sudo and sudo or run
        return func(command)
    else:
        return fabric_sed(filename, before, after, limit, use_sudo, backup)

def conditional_mv(source, destination):
    if exists(source):
        run('mv %(source)s %(destination)s' % locals())

def conditional_rm(path, recursive=False):
    if exists(path):
        cmd = 'rm'
        if recursive:
            cmd += ' -rf'
        run('%(cmd)s %(path)s' % locals())

def conditional_mkdir(path, group=None, mode=None, use_local=False,
        use_sudo=False):
    cmd = 'mkdir -p %(path)s' % locals()
    if not exists(path):
        if use_local:
            local(cmd)
        elif use_sudo:
            sudo(cmd)
        else:
            run(cmd)
    if group:
        chgrp(path, group, use_sudo=True)
    if mode:
        chmod(path, mode, use_sudo=True)