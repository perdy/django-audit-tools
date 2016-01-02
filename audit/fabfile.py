import os

from fabric.api import run, settings, env, cd
from fabric.contrib import files

# env.hosts = ['localhost']


def local():
    env.hosts = ['localhost']


def _get_src_from_github(repo, src_path, local_path, app_name, dist_path=None, tag=None):
    js_path = os.path.join(local_path, app_name, 'js')
    fonts_path = os.path.join(local_path, app_name, 'fonts')
    css_path = os.path.join(local_path, app_name, 'css')
    img_path = os.path.join(local_path, app_name, 'img')

    if not dist_path:
        dist_path = os.path.join(src_path, app_name)

    with settings(warn_only=True):
        # Create the source directory if it doesn't exist
        if not files.exists(src_path):
            run('mkdir {}'.format(src_path))

        # Clone the project if we don't have a local copy of the repo
        if not files.exists('{}/{}'.format(src_path, app_name)):
            with cd(src_path):
                run('git clone {} {}'.format(repo, app_name))

        # Pull down updates
        with cd('{}'.format(dist_path)):
            run('git pull origin master')

            # Checkout to tag if specified
            if tag:
                run('git checkout {}'.format(tag))

            dirs = zip(('js', 'css', 'img', 'fonts'), (js_path, css_path, img_path, fonts_path))

            for d, path in dirs:
                if files.exists(d):
                    # Remove dir
                    run('rm -vR {}'.format(path))
                    # Create dir
                    run('mkdir -p {}'.format(path))
                    # Copy the updated files into the project
                    run('cp -vfR {}/* {}'.format(d, path))


def update_bootstrap(tag=None):
    """
    Update Bootstrap files to tag version. If a tag isn't specified just
    get latest version.
    """
    repo = 'https://github.com/twbs/bootstrap'
    src_path = '~/Desarrollo/src'
    local_path = os.path.join(os.path.dirname(__file__), 'static', 'audit')
    app_name = 'bootstrap'
    dist_path = os.path.join(src_path, app_name, 'dist')

    _get_src_from_github(repo, src_path, local_path, app_name, dist_path, tag)


def update_font_awesome(tag=None):
    """
    Update FontAwesome files to tag version. If a tag isn't specified just
    get latest version.
    """
    repo = 'https://github.com/FortAwesome/Font-Awesome'
    src_path = '~/Desarrollo/src'
    local_path = os.path.join(os.path.dirname(__file__), 'static', 'audit')
    app_name = 'fontawesome'

    _get_src_from_github(repo, src_path, local_path, app_name, tag)


def update_bootstrap_form_helpers(tag=None):
    repo = 'https://github.com/winmarkltd/BootstrapFormHelpers'
    src_path = '~/Desarrollo/src'
    local_path = os.path.join(os.path.dirname(__file__), 'static', 'audit')
    app_name = 'bootstrapformhelpers'
    dist_path = os.path.join(src_path, app_name, 'dist')

    _get_src_from_github(repo, src_path, local_path, app_name, dist_path, tag)


def update_underscore():
    local_path = os.path.join(os.path.dirname(__file__), 'static', 'audit', 'js')
    with cd(local_path):
        run('rm -f underscore-min.js')
        run('rm -f underscore-min.map')
        run('rm -f underscore.js')
        run('wget http://underscorejs.org/underscore-min.js')
        run('wget http://underscorejs.org/underscore-min.map')
        run('wget http://underscorejs.org/underscore.js')


def update_jquery():
    local_path = os.path.join(os.path.dirname(__file__), 'static', 'audit', 'js')
    with cd(local_path):
        run('rm -f jquery-2.1.1.min.js')
        run('wget http://code.jquery.com/jquery-2.1.1.min.js')


def update_all(tag=None):
    update_bootstrap(tag)
    update_font_awesome(tag)
    update_bootstrap_form_helpers(tag)
    update_jquery()
    update_underscore()