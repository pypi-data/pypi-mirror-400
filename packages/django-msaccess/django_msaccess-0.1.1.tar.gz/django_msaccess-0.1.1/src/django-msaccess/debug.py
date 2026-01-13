#
# Debug: output
#

#from . import __init__ as pkg
import sys
pkg = sys.modules[__package__]


def _DebugOutput(fnm,*args,**kwargs):
    if not pkg.__debug_output__:
        if not ('force' in kwargs):
            return
    st=fnm+'\t'
    for item in args:
        st=st + item + '\t'
    st.rstrip('\t')
    for k, v in kwargs.items():
        if k == 'force':
            continue
        st=st + f'{k}={v}' + '\t'
    st.rstrip('\t')
    print(st)


