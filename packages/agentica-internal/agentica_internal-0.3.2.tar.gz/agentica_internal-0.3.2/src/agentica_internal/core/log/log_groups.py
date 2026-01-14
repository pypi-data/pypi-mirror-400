# fmt: off

__all__ = [
    'LOG_GROUPS',
    'GROUP_NAMES',
    'GROUP_EXPAND'
]

###############################################################################

LOG_GROUPS: dict[str, str] = {
    'short': 'send+recv+repl+virt',
    'codec': 'encr+decr',
    'virtual': 'decr+rsrc+virt',
    'core': 'rsrc+repl+virt+ts',
    'server': 'pywasmrunner+sandbox+sessionmanager',
    'sandbox': 'sandbox+pywasmrunner+agentworld+agentrepl',
    'agent': 'agentworld+agentrepl+virt+decr',
    'sdk': 'sdkworld+agent+agenticfunction+virt+frame+csm',
}

GROUP_NAMES = tuple(LOG_GROUPS.keys())
GROUP_EXPAND = LOG_GROUPS.__getitem__
