#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

'''
    Q&D script to setup rsms apps, mvp way.

** What does it do ?

    * clone and/or update your main rapidsms fork
    * clone and/or update other rapidsms forks
    * links your third-parties apps into your fork

** How it works

    1. Create a config file (install.ini)
    2. launch the script
    done.

** Config file

    * INI file format
    * each [section] represent a repository
    * [main] section represent __your__ main fork (target)
    * [main] is mandatory
    * [self] section (optional) relates to the rapidsms-impl folder.
    * [sections] accepts several options.

    Options:
    * url (mandatory string): the URL of the git repository to clone
    * name (recommended string): the name used to refer to that repository.
    * rev (optional int): the revision to pull
    * install (optional boolean): whether or not to install app (setup.py)
    * patch (optional string): target repository (section name) and patch file
    separated by a comma. Example: pygsm, pygsm.patch
    * patchs (optional string): list of patch-formated instructions (see above)
    separated by a pipe.
    Example: rapidsms, email-backend.patch | pygsm, patchs/pygsm-ussd.patch
    * filecopy (optional string): repository (section name), file, destination
    separated by commas. Example: rapidsms, patchs/new.py, lib/rapidsms
    * filecopies (optional string): list of filecopy-formated instructions
    (see above) separated by a pipe.
    Example: rapidsms, new.py, lib/rapidsms | pygsm, patchs/gsm.py, lib/gsm

** Script usage

    1. Go to the parent of your soon-to-be rapidsms folder
    2. write or copy your config file as install.ini
    3. launch: chmod +x deploy.py
    4. launch: ./deploy.py

    * If you have repositories with install=True,
      sudo will prompt for password (after downloads)

    * script accepts two optional parameters:

    -c filename : specify a config file instead of install.ini
    -t path : specify a target path instead of .

'''

import sys
import os
import copy
import getopt
from ConfigParser import ConfigParser, NoOptionError


SELF_PATH = sys.path[0]


class Repository(object):
    ''' holds repository information '''

    isself = False
    ident = None
    url = None
    name = None
    branch = None
    rev = None
    tag = None
    install = False
    patch = None
    patchs = None
    filecopies = None
    patch_target = None
    fcopy = None
    fcopy_target = None
    fcopy_ftarget = None

    def __init__(self, url=None, name=None):

        if url and isinstance(url, str):
            self.url = url

        if name and isinstance(name, str):
            self.name = name

    def get_rev(self):
        ''' return command-line friendly revision string '''

        if self.rev == None:
            return ""
        else:
            return self.rev

    def __str__(self):
        return "%s/%s" % (self.name, self.url)

    def __unicode__(self):
        return self.__str__()


class FeederRepository(Repository):
    ''' Repository which holds apps to link '''

    apps = []

    def __init__(self, url=None, name=None):
        super(FeederRepository, self).__init__(url, name)
        self.apps = []

    def add_app(self, name):
        ''' add named app to the list '''

        self.apps.append(name)


class GitCommander(object):
    ''' grab, updates and links repositories based on configuration '''

    main = None
    others = []
    root = None
    others_dir_name = 'sources'
    others_dir = None

    def __init__(self, main=None, others=None):

        # Add main repository
        if main and isinstance(main, Repository):
            self.main = main

        if others and isinstance(others, (list, tuple)):
            for other in others:
                self.others.append(other)

        self.root = os.getcwd()

    def build(self):
        ''' launchs all build steps sequencialy '''

        # make paths
        self.make_paths()

        # clone repositories
        self.clone_repos()

        # apply patchs
        self.apply_patchs()

        # copy additions
        self.copy_additions()

        # create symlinks
        self.make_symlinks()

        # install repositories
        self.install_repos()

    def make_paths(self):
        ''' creates sources placeholder '''

        print "Creating paths"

        # make folder for others
        try:
            os.mkdir(self.others_dir_name)
        except OSError, e:
            if e.errno == 17:
                print "  Path %s already exists." % self.others_dir_name
                pass
            else:
                raise

        # store repo folders
        self.others_dir = os.path.join(self.root, self.others_dir_name)
        self.main_dir = os.path.join(self.root, self.main.name)

    def make_symlinks(self):
        ''' creates symlinks in main repo to others' apps '''

        main_apps_dir = os.path.join(self.main_dir, 'apps')

        for rep in self.others:
            if rep.apps.__len__() == 0:
                continue

            print " Linkings apps from %s" % rep.name

            rep_dir = os.path.join(self.others_dir, rep.name)
            apps_dir = os.path.join(rep_dir, 'apps')

            for app in rep.apps:
                app_dir = os.path.join(apps_dir, app)
                dst_dir = os.path.join(main_apps_dir, app)

                try:
                    os.unlink(dst_dir)
                except:
                    pass

                try:
                    os.symlink(app_dir, dst_dir)
                except OSError, e:
                    # simlink exist
                    if e.errno == 17:
                        print " symlink %s exists." % app
                    else:
                        raise

    def clone_repos(self):
        ''' clones referenced repositories '''

        repos = copy.copy(self.others)
        repos.append(self.main)

        for rep in repos:

            if rep.isself:
                continue

            print "Entering repository %s" % rep.name

            init_dir = os.getcwd()

            # move to others folder
            if isinstance(rep, FeederRepository):
                os.chdir(self.others_dir)

            # update repo if exists
            if not os.path.exists(rep.name):
                print " Cloning git repository"
                os.system("git clone %(url)s %(dir)s" % {'url': rep.url, \
                'dir': rep.name})
            else:
                print " repository %s exists." % rep.name

            print " Updating repository"
            GitCommander.update_repo(os.path.join(os.getcwd(), rep.name), \
            rep.get_rev(), rep.tag, rep.branch)

            # move back
            os.chdir(init_dir)

    def install_repos(self):

        for rep in self.others:
            if rep.install:
                folder = os.path.join(self.others_dir, rep.name)
                GitCommander.install(folder)

    def apply_patchs(self):

        for rep in self.others:
            if rep.patch and rep.patch_target:
                target = self.repo_by_ident(rep.patch_target)
                if target == None:
                    print " Error with patch location."
                    continue
                folder = os.path.join(self.others_dir, target.name)
                rep_dir = os.path.join(self.others_dir, rep.name)
                GitCommander.patch(folder, os.path.join(rep_dir, rep.patch))

            if rep.patchs:
                print " Applying multiple patchs (%s)" % rep.patchs.__len__()
                for patch_target, patch in rep.patchs:
                    target = self.repo_by_ident(patch_target)
                    if target == None:
                        print " Error with patch location."
                        continue
                    folder = os.path.join(self.others_dir, target.name)
                    if rep.isself:
                        rep_dir = SELF_PATH
                    else:
                        rep_dir = os.path.join(self.others_dir, rep.name)
                    GitCommander.patch(folder, os.path.join(rep_dir, patch))

    def copy_additions(self):

        for rep in self.others:
            if rep.fcopy and rep.fcopy_target and rep.fcopy_ftarget:
                target = self.repo_by_ident(rep.fcopy_target)
                if target == None:
                    print " Error with filecopy location."
                    continue
                folder = os.path.join(self.others_dir, target.name)
                if rep.isself:
                    rep_dir = SELF_PATH
                else:
                    rep_dir = os.path.join(self.others_dir, rep.name)
                GitCommander.copy(rep_dir, rep.fcopy, \
                                  os.path.join(folder, rep.fcopy_ftarget))

            if rep.filecopies:
                print " Copying %s additions" % rep.filecopies.__len__()
                for ffcopy, ffcopy_target, ffcopy_ftarget in rep.filecopies:
                    target = self.repo_by_ident(ffcopy_target)
                    if target == None:
                        print " Error with filecopy location."
                        continue
                    folder = os.path.join(self.others_dir, target.name)
                    if rep.isself:
                        rep_dir = SELF_PATH
                    else:
                        rep_dir = os.path.join(self.others_dir, rep.name)
                    GitCommander.copy(rep_dir, ffcopy, \
                                      os.path.join(folder, ffcopy_ftarget))

    @classmethod
    def install(cls, folder):

        init_dir = os.getcwd()

        os.chdir(folder)

        print " Installing repository at %s" % folder

        os.system("sudo python ./setup.py install")

        os.chdir(init_dir)

    @classmethod
    def patch(cls, folder, patch):

        init_dir = os.getcwd()

        os.chdir(folder)

        print " Patching repository at %s" % folder

        os.system("patch -p1 < %s" % patch)

        os.chdir(init_dir)

    @classmethod
    def copy(cls, folder, source, target):

        init_dir = os.getcwd()

        os.chdir(folder)

        print " Copy %s at %s" % (source, target)

        os.system("cp -rv %s %s/" % (source, target))

        os.chdir(init_dir)

    @classmethod
    def update_repo(cls, folder, rev, tag=None, branch=None):
        ''' pulls new changes from a git repository '''

        init_dir = os.getcwd()

        os.chdir(folder)

        # reset in case it's an existing repo

        # retrieve tags
        os.system("git fetch --tags --keep")

        # select branch if applicable
        if branch:
            os.system("git checkout --track -b %(branch)s origin/%(branch)s" \
                % {'branch': branch})

        if rev:
            os.system("git checkout -b %(rev)s %(rev)s" % {'rev': rev})

        if tag:
            os.system("git checkout -b %(tag)s %(tag)s" % {'tag': tag})

        os.system("git reset --hard")

        os.chdir(init_dir)

    def repo_by_ident(self, ident):
        for rep in self.others:
            if rep.ident == ident:
                return rep
        return None


class GitConfig(ConfigParser):
    ''' configures respositories from a config file '''

    def __init__(self, path=None):
        ConfigParser.__init__(self)

        self.repos = []
        self.main_repo = None

        if path:
            self.readfp(open(path))
            self.config_repos()

    def config_repos(self):
        ''' configures reposotory objects based on config '''

        for repo_name in self.sections():
            ismain = repo_name == 'main'

            repo = self.config_repo(repo_name, ismain)

            if ismain:
                self.main_repo = repo
            else:
                self.repos.append(repo)

    def config_repo(self, ident, main=False):
        ''' configure a named repository '''

        # get name ; if none, default to section name
        try:
            name = self.get(ident, 'name')
        except NoOptionError:
            name = ident

        # url is mandatory
        try:
            url = self.get(ident, 'url', None)
        except:
            if not name == 'self':
                raise
            url = None

        # revision is optional
        try:
            rev = self.getint(ident, 'rev')
        except (NoOptionError, ValueError):
            #rev = self.get(ident, 'rev')
            rev = None

        # install is optional
        try:
            install = self.getboolean(ident, 'install')
        except NoOptionError:
            install = False

        # apps is optional (feeder only)
        try:
            apps = self.get(ident, 'apps')
            apps = apps.replace(' ', '').split(',')
        except:
            apps = []

        # patch is optional
        try:
            patch = self.get(ident, 'patch')
            patch_target, patch = patch.replace(' ', '').split(',')
        except:
            patch = None
            patch_target = None

        # fcopy is optional
        try:
            fcopy = self.get(ident, 'filecopy')
            fcopy_target, fcopy, fcopy_ftarget = \
                                              fcopy.replace(' ', '').split(',')
        except:
            fcopy = None
            fcopy_target = None
            fcopy_ftarget = None

        # patchs is optional
        try:
            patchs = self.get(ident, 'patchs')
            patchst = []
            for tu in patchs.replace(' ', '').split('|'):
                x = tu.split(',')
                patchst.append((x[0], x[1]))
        except:
            patchst = None

        # filecopies is optional
        try:
            filecopies = self.get(ident, 'filecopies')
            filecopiesst = []
            for tu in filecopies.replace(' ', '').split('|'):
                x = tu.split(',')
                filecopies.append((x[0], x[1], x[2]))
        except:
            filecopiesst = None

        if main:
            repo = Repository(url=url, name=name)
        else:
            repo = FeederRepository(url=url, name=name)

        if name == 'self':
            repo.isself = True
        repo.ident = ident
        repo.rev = rev
        repo.install = install
        repo.patch = patch
        repo.patch_target = patch_target
        repo.patchs = patchst
        repo.fcopy = fcopy
        repo.fcopy_target = fcopy_target
        repo.fcopy_ftarget = fcopy_ftarget
        repo.filecopies = filecopiesst

        try:
            repo.apps = apps
        except:
            pass

        return repo


def usage(me):
    print u"Usage:  %s [-c file, --config=file, -t path, --target=path] \n\n \
\
    -c, --config=   Use provided configuration file \n \
    -t, -target=    Use provided path as home for repositories \
" % me


def main():

    config_file = 'install.ini'
    target = os.getcwd()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:t:", \
                                                ["help", "config=", "target="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
        elif o in ("-c", "--config"):
            config_file = a
        elif o in ("-t", "--target"):
            target = a
        else:
            assert False, "Unhandled option"

    if not os.path.exists(config_file) or not os.path.exists(target):
        print "Error. File does not exist."
        sys.exit(1)

    # read config file
    config = GitConfig(config_file)

    # build folder and clones and everything
    commander = GitCommander(main=config.main_repo, others=config.repos)
    commander.build()

if __name__ == '__main__':
    main()
