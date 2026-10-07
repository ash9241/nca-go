"""Bounded line protocols for optional local GTP and KataGo analysis engines."""
import json
import queue
import subprocess
import threading
from pathlib import Path
import uuid
import numpy as np
from .rules import Position


def coordinate(point):
    if point is None:
        return "pass"
    r,c = point
    alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if c < len(alphabet):
        return alphabet[c]+str(r+1)
    return f"({c},{r})"


def parse_coordinate(value,size):
    value = value.strip().upper()
    if value in ("PASS","RESIGN"):
        return None
    if value.startswith("("):
        c,r = map(int,value.strip("()").split(","))
        return r,c
    alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    c,r = alphabet.index(value[0]),int(value[1:])-1
    if not 0 <= r < size or c >= size:
        raise ValueError("Engine returned an outside-board coordinate")
    return r,c


class LineProcess:
    def __init__(self,arguments,log,timeout=120):
        self.timeout = timeout
        self.stderr = Path(log).open("w")
        self.process = subprocess.Popen(arguments,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
        self.lines = queue.Queue()
        def consume():
            for line in self.process.stdout:
                self.lines.put(line)
            self.lines.put(None)
        self.thread = threading.Thread(target=consume,daemon=True)
        self.thread.start()

    def send(self,value):
        self.process.stdin.write(value+"\n")
        self.process.stdin.flush()

    def read(self):
        try:
            line = self.lines.get(timeout=self.timeout)
        except queue.Empty as error:
            raise TimeoutError("Engine response timed out") from error
        if line is None:
            raise RuntimeError(f"Engine exited with {self.process.poll()}")
        return line

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)
        self.stderr.close()

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()


class GTP(LineProcess):
    def command(self,command):
        self.send(command)
        response = []
        while True:
            line = self.read().rstrip("\n")
            if not line and response:
                break
            if line:
                response.append(line)
        if not response[0].startswith("="):
            raise RuntimeError("\n".join(response))
        return "\n".join(response)[1:].strip()

    def set_position(self,position):
        self.command(f"boardsize {len(position.board)}")
        self.command("clear_board")
        self.command("komi 7.5")
        for r,c in np.argwhere(position.board != 0):
            self.command(f"play {'B' if position.board[r,c] == 1 else 'W'} {coordinate((r,c))}")


class KataAnalysis(LineProcess):
    def analyze(self,position,moves=(),visits=1,history_start=None):
        n = len(position.board)
        initial = position.board if not moves else history_start
        if initial is None:
            initial = np.zeros_like(position.board)
        request = {"id":uuid.uuid4().hex,"moves":[["B" if c == 1 else "W",coordinate(p)] for c,p in moves],
            "initialStones":[["B" if initial[r,c] == 1 else "W",coordinate((r,c))] for r,c in np.argwhere(initial != 0)],
            "initialPlayer":"B" if (moves[0][0] if moves else position.to_move) == 1 else "W",
            "rules":"tromp-taylor","komi":7.5,"boardXSize":n,"boardYSize":n,"maxVisits":visits,
            "includeOwnership":True,"includePolicy":True,"overrideSettings":{"reportAnalysisWinratesAs":"BLACK"}}
        self.send(json.dumps(request))
        while True:
            reply = json.loads(self.read())
            if reply.get("id") == request["id"] and not reply.get("isDuringSearch",False):
                if "error" in reply:
                    raise RuntimeError(reply["error"])
                return reply


def teacher_arrays(reply,size):
    policy = np.asarray(reply["policy"],np.float32)
    policy = np.maximum(policy,0)
    if policy.shape != (size*size+1,) or policy.sum() <= 0:
        raise ValueError("Invalid teacher policy shape or mass")
    policy /= policy.sum()
    # KataGo arrays start at top-left; our rows start at the bottom.
    policy[:-1] = policy[:-1].reshape(size,size)[::-1].ravel()
    ownership = np.asarray(reply["ownership"],np.float32).reshape(size,size)[::-1].copy()
    root = reply["rootInfo"]
    return policy,ownership,float(root["scoreLead"]),float(root["winrate"])
