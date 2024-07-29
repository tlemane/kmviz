from executor import execute, ExternalCommandFailed
from kmviz.core.io import KmVizInvalidQuery

def make_cmd(executable: str, subcmd: str, *args, **kwargs):
    cmd = executable

    if subcmd:
        cmd += f" {subcmd}"

    for k, v in kwargs.items():
        if v is not None:
            cmd += f" {k} {v}"
        else:
            cmd += f" {k}"

    for e in args:
        cmd += f" {args}"

    return cmd

def exec_cmd(cmd: str, **options):
    try:
        return execute(cmd, **options)
    except ExternalCommandFailed as ec:
        raise KmVizInvalidQuery(str(ec))