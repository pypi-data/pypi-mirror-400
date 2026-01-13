#!/usr/bin/env python3


# -----------  jsut checking number of parameters.
# --- this script is called from py wrapper
# --- and paramters are passed using sys.argv
# --- and compatible with uv uvx
#

import subprocess as sp
import shlex
import os
import sys
import click

from jusfltuls.check_new_version import is_there_new_version
from importlib.metadata import version as pkg_version

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    print(f"distcheck {pkg_version('jusfltuls')}")
    is_there_new_version(package="jusfltuls", printit=True, printall=True)
    ctx.exit()

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Show version and exit')
def main():
    is_there_new_version(package="jusfltuls", printit=True, printall=True)
    command=f"distcheck.sh"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("D... ...", script_dir)
    full_command = os.path.join(script_dir, command)
    print("D... ...", full_command)
    CMD = shlex.split(full_command)
    # it is interactive... FULL INTERACTIVITY
    result = sp.run( CMD )#, capture_output=True, text=True )
    #if result.returncode != 0:
    #    print("X... error calling", command)
    #print(result.stdout ) ####   REPOERT THE OUTPUT
    return

if __name__ == "__main__":
    main()
