import os.path

VERSION = (1, 0, 0, 'dev')


def get_version():
    """
    Return the version as a string. If this is flagged as a development
    release and mercurial can be loaded the specifics about the changeset
    will be appended to the version string. 
    """
    if 'dev' in VERSION:
        try:
            from mercurial import hg, ui
    
            repo_path = os.path.join(os.path.dirname(__file__), '..')
            repo = hg.repository(ui.ui(), repo_path)
            ctx = repo['tip']
            build_info = 'dev %s %s:%s' % (ctx.branch(), ctx.rev(), str(ctx))
        except:
            # mercurial module missing or repository not found
            build_info = 'dev-unknown'
    v = VERSION[:VERSION.index('dev')] + (build_info,)
    return '.'.join(map(str, v))
