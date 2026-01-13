#!/usr/bin/env python3

"""
pingy - realtime ping monitoring with sparklines (default) or classic toilet display

Default mode: multi-host sparklines (blue=reply, red=miss)
  Usage: pingy google.com 8.8.8.8
  Usage: pingy --config  # read from ~/.ssh/config

Classic mode: single-host with toilet display
  Usage: pingy --classic google.com
"""

import sys
import asyncio
import shutil
import re
from collections import deque
from time import monotonic
import os
import click
import subprocess as sp
import time
import random

from jusfltuls.check_new_version import is_there_new_version
from importlib.metadata import version as pkg_version

# Sparkline mode constants
PING_RE = re.compile(r"time[=<]\s*([\d.]+)\s*ms", re.I)
SPARK = "▁▂▃▄▅▆▇█"  # 8 levels
BLUE = "\033[94m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
PURPLE = "\033[95m"
RESET = "\033[0m"
CLEAR = "\033[H\033[J"
INIT = object()

# Classic mode constants
MIN60 = 60
lastp = []
lastp2 = []
lastp3 = []


def get_uni(i, leng=False):
    """For classic mode bar display"""
    uni=['\u2583','\u2584',
         '\u2585','\u2586',
         '\u2586','\u2587']
    if leng:
        r = random.randint(0,len(uni)-2)+1
        return r
    k=i
    return uni[k].encode("utf16","surrogatepass").decode("utf16")


def ping_classic(who="192.168.0.1"):
    """Classic mode: one ping"""
    global lastp,lastp2,lastp3
    CMD = "ping -w 1 -i 1 "+who
    l = get_uni(0, leng=True)
    try:
        res = sp.check_output(CMD.split()).decode("utf8")
        ok = "green"
        lastp.append(l)
        lastp2.append(l)
        lastp3.append(l)
    except:
        time.sleep(1)
        ok = "red"
        lastp.append(0)
        lastp2.append(0)
        lastp3.append(0)
    return who,ok


def bar_classic(n=10):
    """Classic mode: display bars"""
    global lastp,lastp2,lastp3
    while len(lastp)>n:
        lastp.pop(0)
    i = 0
    for color in lastp:
        i+=1
        if color==0:
            print('\033[0;31m', end="", flush=True)
        else:
            print('\033[0;32m', end="", flush=True)
        CHAR = get_uni(color)
        print(CHAR, flush=True, end="")
        if i>n: break
    print()

    # second bar
    i = 0
    suma = 0
    while len(lastp2)>MIN60*MIN60:
        lastp2.pop(0)
    for color in lastp2:
        i+=1
        if color!=0:color=1
        suma+= color
        if i>=MIN60:
            if suma==0:
                print('\033[0;31m', end="", flush=True)
            elif suma>=MIN60:
                print('\033[0;32m', end="", flush=True)
            else:
                print('\033[0;35m', end="", flush=True)
            CHAR = get_uni(1)
            print(CHAR, end="", flush=True)
            i = 0
            suma=0
    print()

    # 3rd bar
    i = 0
    suma = 0
    while len(lastp3)>MIN60*MIN60*MIN60:
        lastp3.pop(0)
    for color in lastp3:
        i+=1
        if color!=0:color=1
        suma+= color
        if i>=MIN60*MIN60:
            if suma==0:
                print('\033[0;31m', end="", flush=True)
            elif suma==MIN60:
                print('\033[0;32m', end="", flush=True)
            else:
                print('\033[0;35m', end="", flush=True)
            CHAR = get_uni(3)
            print(CHAR, end="", flush=True)
            i = 0
            suma=0
    print()


def output_classic(text="192.168.0.111", color="green"):
    """Classic mode: one shot ping with toilet"""
    CMD = "toilet -f mono9 "+text
    CMD = "toilet -f pagga "+text
    if color=="red":
        print('\033[0;31m', end="", flush = True)
        CMD = CMD + " f"
    if color=="green":
        print('\033[0;32m', end="", flush = True)
        CMD = CMD + " +"
    res = sp.check_call(CMD.split())
    print('\033[0m', end="")


CONFF = os.path.expanduser("~/.ssh/config")


def parse_ssh_config(path=CONFF):
    """Parse ~/.ssh/config and return list of IPs"""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf8") as f:
        lines = f.readlines()

    blocks = []
    current = []
    for ln in lines:
        if re.match(r"^\s*Host\s+", ln, flags=re.I):
            if current:
                blocks.append(current)
            current = [ln]
        else:
            if current:
                current.append(ln)
    if current:
        blocks.append(current)

    out = []
    seen = set()
    for block in blocks:
        host_line = block[0].strip()
        m = re.match(r"(?i)Host\s+(.+)", host_line)
        if not m:
            continue
        aliases = m.group(1).split()
        alias = next((a for a in aliases if not re.search(r"[*?\[\]]", a)), aliases[0]).strip()

        hostname = None
        for ln in block[1:]:
            m2 = re.match(r"(?i)\s*HostName\s+(.+)", ln)
            if m2:
                hostname = m2.group(1).split()[0].strip().strip('"').strip("'")
                break

        value = hostname if hostname else alias
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


async def ping_once(host, ping_cmd, timeout):
    """Async ping for sparkline mode"""
    proc = await asyncio.create_subprocess_exec(*ping_cmd, host,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        try:
            await proc.communicate()
        except Exception:
            pass
        return None
    txt = (out + err).decode(errors="ignore")
    m = PING_RE.search(txt)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None


def make_ping_command(is_windows):
    """Build ping command for OS"""
    if is_windows:
        return ["ping", "-n", "1"]
    else:
        return ["ping", "-c", "1"]


def map_to_level(rtt, max_rtt):
    """Map RTT to sparkline level"""
    if rtt is None:
        return None
    r = min(rtt, max_rtt) / max_rtt
    idx = int(r * (len(SPARK) - 1) + 0.5)
    return max(0, min(len(SPARK) - 1, idx))


def render(hosts, history, max_rtt, stats):
    """Render sparkline display"""
    cols = shutil.get_terminal_size().columns

    name_w = max(len(h) for h in hosts) + 2
    spark_w = max(10, cols - name_w - 1)
    out_lines = [CLEAR]
    header = f"pingy - {len(hosts)} hosts  max_rtt={max_rtt}ms  "
    out_lines.append(header)
    for h in hosts:
        dq = history[h]
        if len(dq) < spark_w:
            dq.extendleft([None] * (spark_w - len(dq)))
        elif len(dq) > spark_w:
            for _ in range(len(dq) - spark_w):
                dq.popleft()
        line = ""
        if stats[h]['last'] is not None:
            line = GREEN + h.ljust(name_w) + RESET
        else:
            line = RED + h.ljust(name_w) + RESET

        s = []
        for val in dq:
            if val is INIT:
                s.append(" ")
            else:
                lvl = map_to_level(val, max_rtt)
                if lvl is None:
                    s.append(RED + "█" + RESET)
                else:
                    s.append(BLUE + SPARK[lvl] + RESET)

        rtt_text = f"{stats[h]['last']:.1f}ms" if stats[h]['last'] is not None else "timeout"
        loss = stats[h]['loss'] * 100.0
        line += "".join(s) + " " + f"{rtt_text} loss={loss:.0f}% "
        out_lines.append(line)
    return "\n".join(out_lines)


async def async_main_sparkline(hosts, interval, timeout, max_rtt, config):
    """Main loop for sparkline mode"""
    if config:
        hosts = parse_ssh_config()

    if hosts is None or len(hosts) == 0:
        print("No hosts to ping. Use --config or provide host addresses.")
        return

    is_windows = sys.platform.startswith("win")
    ping_cmd = make_ping_command(is_windows)

    history = {h: deque(maxlen=600) for h in hosts}
    stats = {h: {"last": None, "sent": 0, "lost": 0, "loss": 0.0} for h in hosts}

    cols = shutil.get_terminal_size().columns
    name_w = max(len(h) for h in hosts) + 2
    spark_w = max(10, cols - name_w - 1)
    for h in hosts:
        history[h].extend([INIT] * spark_w)

    try:
        while True:
            t0 = monotonic()
            tasks = {h: asyncio.create_task(ping_once(h, ping_cmd, timeout)) for h in hosts}
            results = {}
            for h, task in tasks.items():
                try:
                    r = await task
                except Exception:
                    r = None
                results[h] = r
                stats[h]["sent"] += 1
                if r is None:
                    stats[h]["lost"] += 1
                stats[h]["loss"] = stats[h]["lost"] / stats[h]["sent"]
                stats[h]["last"] = r if r is not None else None
                history[h].append(r)
            print(render(hosts, history, max_rtt, stats), flush=True)
            dt = interval - (monotonic() - t0)
            if dt > 0:
                await asyncio.sleep(dt)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nExiting.", flush=True)


def main_classic(addr):
    """Main loop for classic mode"""
    rang = MIN60
    for i in range(3600*24*7):
        time.sleep(0.1)
        who, ok = ping_classic(addr)
        os.system("clear")
        print('\033[1;1H')
        output_classic(who, ok)
        bar_classic(n=rang)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    print(f"pingy {pkg_version('jusfltuls')}")
    is_there_new_version(package="jusfltuls", printit=True, printall=True)
    ctx.exit()


@click.command()
@click.argument("hosts", nargs=-1, required=False)
@click.option("-v", "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True, help="Show version and exit")
@click.option("--classic", is_flag=True, default=False, help="Use classic single-host mode with toilet display")
@click.option("-i", "--interval", type=float, default=1.0, help="Seconds between samples")
@click.option("-t", "--timeout", type=float, default=1.0, help="Ping timeout in seconds")
@click.option("-m", "--max-rtt", type=float, default=200.0, help="Max RTT (ms) mapped to sparkline")
@click.option("-c", "--config", is_flag=True, default=False, help="Read hosts from ~/.ssh/config")
def main(hosts, classic, interval, timeout, max_rtt, config):
    """
    Ping monitoring tool with two modes:

    Default (sparkline): Multi-host realtime sparklines
      pingy google.com 8.8.8.8
      pingy --config

    Classic mode: Single-host with toilet display
      pingy --classic google.com
    """
    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    if classic:
        # Classic mode - single host with toilet
        if not hosts or len(hosts) == 0:
            print("Usage: pingy --classic <host>")
            sys.exit(1)
        addr = hosts[0]
        try:
            main_classic(addr)
        except KeyboardInterrupt:
            pass
    else:
        # Default sparkline mode - multi-host
        try:
            asyncio.run(async_main_sparkline(hosts, interval, timeout, max_rtt, config))
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
