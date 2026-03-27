#!/bin/python3
import os
from argparse import ArgumentParser
import subprocess as sp
import re
import curses
import sys

STATUS_RE = re.compile(
    r'(?P<status>(run)|(down)|(fail)): (?P<name>[/\w-]+):( \(pid (?P<pid>\d+)\))? (?P<runtime>\d+)s(, (?P<info>[\w\s,]+))?'
)

# TODO rework all sp calls to use svdir and svsrc


class Status:

    def __init__(self, status: str, pid: int, uptime: int, info: str) -> None:
        self.status = status
        self.pid = pid
        self.uptime = uptime
        self.info = info

    def __str__(self) -> str:
        return f'STATUS(pid={self.pid}, uptime={self.uptime}, info="{self.info}")'


def checkStatus(link: str) -> list[Status]:
    if not os.path.islink(link):
        return [Status("off", 0, 0, "")]

    ret = sp.run(["sv", "status", link], capture_output=True)
    if ret.returncode in (2, 151):
        return [Status("off", 0, 0, "")]

    out: list[Status] = []

    for sv in ret.stdout.decode().split(";"):
        m = STATUS_RE.fullmatch(sv.strip())
        if m is None:
            continue
        out.append(Status(m.group("status"), int(m.group("pid") or 0), int(m.group("runtime")), m.group("info") or ""))

    if len(out) == 0:
        return [Status("off", 0, 0, "")]

    return out


class Service:

    def __init__(self, name: str, path: str, link: str):
        self.name = name
        self.path = path
        self.link = link
        self.enabled = os.path.exists(link)
        self.status = []
        self.checkStatus()

    def checkStatus(self):
        self.status = checkStatus(self.link)
        self.enabled = self.status[0].status in ("run", "down")

    def disable(self):
        if os.path.exists(self.link) and os.path.islink(self.link):
            os.remove(self.link)

    def enable(self):
        os.symlink(self.path, self.link)

    def __str__(self) -> str:
        return f'SV("{self.name}", enabled={self.enabled}, status={self.status[0]})'


ACTION_ENABLE = 0
ACTION_RUN = 1
MAX_OPTIONS = 2

OPT_NO = 0
OPT_YES = 1


def showYesNo(text: str) -> bool:
    width = len(text) + 2
    height = 4
    win = curses.newwin(height, width, curses.LINES // 2 - height // 2, curses.COLS // 2 - width // 2)
    win.border()
    win.keypad(True)
    selectedOpt = 0
    out = False
    while True:
        win.move(1, 1)
        win.addstr(text)
        attrs = curses.A_BOLD
        if selectedOpt == OPT_NO:
            attrs |= curses.A_UNDERLINE

        win.move(2, width // 2 - 3)
        win.addstr("No", attrs)

        attrs = curses.A_BOLD
        if selectedOpt == OPT_YES:
            attrs |= curses.A_UNDERLINE

        win.move(2, width // 2)
        win.addstr("Yes", attrs)

        c = win.getch()
        if c == ord("n"):
            break
        elif c == ord("y"):
            out = True
            break
        elif c in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            selectedOpt = (selectedOpt + 1) % 2
        elif c in (ord('\n'), curses.KEY_ENTER):
            out = selectedOpt == OPT_YES
            break
    win.clear()
    return out


def processAction(service: Service, action: int):
    if action == ACTION_ENABLE or not service.enabled:
        if showYesNo(f"{'Disable' if service.enabled else 'Enable'} service {service.name}?"):
            if service.enabled:
                service.disable()
            else:
                service.enable()

    elif action == ACTION_RUN:
        offline = service.status[0].status == "down"
        if showYesNo(f"{'Start' if offline else 'Stop'} service {service.name}?"):
            cmd = "up" if offline else "down"
            sp.run(["sv", cmd, service.name])


def main(stdscr: curses.window) -> int:
    parser = ArgumentParser()
    parser.add_argument(
        "--svdir", required=False, help="Service dir to use, defaults to $SVDIR if unspecified, or the cwd"
    )
    parser.add_argument(
        "--src",
        required=False,
        help="Directory of service folders that can be symlinked to svdir, defaults to $SVSRC if unspecified"
    )

    args = parser.parse_args()

    if args.svdir is None:
        try:
            svdir = os.environ["SVDIR"]
        except KeyError:
            svdir = os.curdir
    else:
        svdir = str(args.svdir)

    if args.src is None:
        try:
            srcdir = os.environ["SVSRC"]
        except KeyError:
            print("Please set either $SVSRC or use the --src argument")
            parser.print_usage()
            return -1
    else:
        srcdir = args.src

    availableServices = os.listdir(srcdir)
    enabledServices = set(os.listdir(svdir))

    services: list[Service] = []

    for sv in availableServices:
        if sv.startswith("."):
            continue
        path = os.path.join(srcdir, sv)
        link = os.path.join(svdir, sv)
        services.append(Service(sv, path, link))

    for sv in services:
        print(sv)

    curses.curs_set(False)

    selectedSv = 0
    drawStart = 0

    curses.use_default_colors()
    curses.halfdelay(5)

    GREEN = 1
    curses.init_pair(GREEN, curses.COLOR_GREEN, -1)
    RED = 2
    curses.init_pair(RED, curses.COLOR_RED, -1)

    selectedAct = ACTION_RUN

    try:
        while True:
            stdscr.move(0, 0)
            drawEnd = drawStart + curses.LINES - 1
            for i in range(curses.LINES - 1):
                stdscr.clrtoeol()
                y, x = stdscr.getyx()
                idx = drawStart + i

                if idx >= len(services):
                    break
                if idx == selectedSv:
                    stdscr.addstr(">")
                else:
                    stdscr.addstr(" ")
                stdscr.addch(" ")
                sv = services[idx]
                sv.checkStatus()
                stdscr.addstr(sv.name)
                stdscr.move(y, 30)
                attrs = curses.A_BOLD
                if idx == selectedSv and selectedAct == ACTION_ENABLE:
                    attrs |= curses.A_UNDERLINE

                if sv.enabled:
                    stdscr.addstr("Enabled", curses.color_pair(GREEN) | attrs)
                else:
                    stdscr.addstr("Disabled", curses.color_pair(RED) | attrs)
                stdscr.move(y, 40)

                attrs = curses.A_BOLD
                if idx == selectedSv and selectedAct == ACTION_RUN:
                    attrs |= curses.A_UNDERLINE

                if sv.status[0].status == "run":
                    stdscr.addstr(sv.status[0].status, curses.color_pair(GREEN) | attrs)
                else:
                    stdscr.addstr(sv.status[0].status, curses.color_pair(RED) | attrs)

                stdscr.move(y, 45)
                stdscr.addstr(str(sv.status[0].uptime))
                stdscr.addstr("s ")
                stdscr.addstr(sv.status[0].info)

                stdscr.move(y + 1, 0)

            c = stdscr.getch()
            if c == ord('q'):
                break
            elif c == curses.KEY_DOWN:
                selectedSv = min(len(services) - 1, selectedSv + 1)
            elif c == curses.KEY_UP:
                selectedSv = max(0, selectedSv - 1)
            elif c == curses.KEY_LEFT:
                selectedAct = (selectedAct - 1) % MAX_OPTIONS
            elif c == curses.KEY_RIGHT:
                selectedAct = (selectedAct + 1) % MAX_OPTIONS
            elif c == curses.KEY_ENTER or c == ord("\n"):
                processAction(services[selectedSv], selectedAct)
                stdscr.clear()

            if selectedSv >= drawEnd:
                drawEnd += 1
                drawStart += 1
                stdscr.clear()
            elif selectedSv < drawStart:
                drawStart -= 1
                drawEnd -= 1
                stdscr.clear()

    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    curses.wrapper(main)
