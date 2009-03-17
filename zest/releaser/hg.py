import zest.releaser.utils

class Hg(zest.releaser.utils.BaseVersionControl):
    """Command proxy for Mercurial"""
    internal_filename = '.hgrc'
