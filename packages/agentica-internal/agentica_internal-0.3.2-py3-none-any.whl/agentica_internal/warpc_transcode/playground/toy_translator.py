from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from typing import Deque, Optional

import msgspec
import msgspec.json
from agentica_internal.core.print import tprint
from agentica_internal.warpc.messages import DefinitionMsg, RPCMsg
from agentica_internal.warpc_transcode.py_to_uni import py_to_uni_rpc
from agentica_internal.warpc_transcode.uni_msgs import (
    RpcUniMsg,
    json_to_def_uni,
    json_to_rpc_uni,
    uni_to_json,
)
from agentica_internal.warpc_transcode.uni_to_py import uni_to_py, uni_to_py_rpc


def _find_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(10):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


class Translator:
    ctx: dict
    init: dict[str, DefinitionMsg]

    def __init__(
        self,
        in_path: Optional[str] = None,
        out_path: Optional[str] = None,
        base_dir: Optional[str] = None,
    ) -> None:
        here = Path(__file__).resolve()
        repo = _find_repo_root(here.parent.parent.parent.parent)
        ipc_dir = Path(base_dir) if base_dir else repo / ".logs"
        ipc_dir.mkdir(parents=True, exist_ok=True)

        self.inbox = Path(in_path) if in_path else ipc_dir / "client_to_server.json"
        self.outbox = Path(out_path) if out_path else ipc_dir / "server_to_client.json"
        self.inbox.touch(exist_ok=True)

        self.in_transl_log = self.inbox.with_suffix(".transl.jsonl")
        self.out_transl_log = self.outbox.with_suffix(".transl.jsonl")

        self._msg_counter = 0
        self._in_queue: Deque[RPCMsg] = deque()

        self._json_enc = msgspec.json.Encoder()

        # Initialize context/init maps
        self.ctx = {}
        self.init = {}

        # Expect first non-empty line to be mapping var->DefUniMsg
        blob = self.inbox.read_text()
        lines = [ln for ln in blob.splitlines() if ln.strip()]
        if not lines:
            raise RuntimeError("translator inbox empty; expected init defs line")
        first = lines[0]
        init_decoder = msgspec.json.Decoder(dict[str, msgspec.Raw])
        raw_map = init_decoder.decode(first)
        for name, raw in raw_map.items():
            if name == "":
                raise ValueError("empty name in init defs")
            # decode each entry using the single-def decoder
            defmsg = json_to_def_uni(raw)
            if defmsg.uid not in self.ctx:
                self.ctx[defmsg.uid] = defmsg
            native = uni_to_py(defmsg, self.ctx)
            if not isinstance(native, DefinitionMsg):
                raise RuntimeError("init contained non-resource def")
            self.init[name] = native
        # mark first line consumed
        self._msg_counter = 1

    # Receiving: uni JSON -> native Python RPCMsg
    def poll_inbound(self) -> None:
        blob = self.inbox.read_text()
        if not blob:
            return
        lines = [ln for ln in blob.splitlines() if ln.strip()]
        if len(lines) < self._msg_counter:
            raise RuntimeError("inbound file truncated")
        for idx in range(self._msg_counter, len(lines)):
            raw = lines[idx]
            try:
                uni: RpcUniMsg = json_to_rpc_uni(raw)
                # Add defs to self.ctx
                for d in getattr(uni, 'defs', []) or []:
                    if d.uid not in self.ctx:
                        self.ctx[d.uid] = d
                # Decode to Python
                py_msg: RPCMsg = uni_to_py_rpc(uni, self.ctx)
                tprint("Received Python RPCMsg:", py_msg)
                self._in_queue.append(py_msg)
                self._append_native_log(self.in_transl_log, py_msg)
            except Exception as e:
                raise RuntimeError(f"error processing msg {idx}: {e}") from e
        self._msg_counter = len(lines)

    def recv_py_rpc(self, poll_ms: int = 100, timeout_s: Optional[float] = None) -> RPCMsg:
        start = time.time()
        while True:
            tprint("Polling inbound TS msg...")
            if not self._in_queue:
                self.poll_inbound()
            if self._in_queue:
                tprint("Returning Python RPCMsg:", self._in_queue[0])
                return self._in_queue.popleft()
            if timeout_s is not None and (time.time() - start) > timeout_s:
                raise RuntimeError("recv timeout")
            time.sleep(poll_ms / 1000.0)

    def send_py_rpc(self, msg: RPCMsg) -> None:
        try:
            tprint("Sending Python RPCMsg:", msg)
            uni = py_to_uni_rpc(msg, self.ctx)
            json_bytes = uni_to_json(uni)
            tprint("Converted to Uni JSON:", json_bytes.decode("utf-8"))
            with self.outbox.open("a") as f:
                f.write(json_bytes.decode("utf-8"))
                f.write("\n")
            self._append_native_log(self.out_transl_log, msg)
            tprint("Sent Python RPCMsg!")
            # Add emitted defs to ctx
            for d in getattr(uni, 'defs', []) or []:
                if d.uid not in self.ctx:
                    self.ctx[d.uid] = d
        except Exception as e:
            tprint("Error sending Python RPCMsg:", msg, e)
            pass

    def _append_native_log(self, path: Path, py_msg: RPCMsg) -> None:
        try:
            record = py_msg
            with path.open("a") as f:
                f.write(self._json_enc.encode(record).decode("utf-8"))
                f.write("\n")
        except Exception:
            pass
