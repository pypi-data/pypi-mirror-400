import asyncio
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple


_forward_re = re.compile(r"Forwarding from 127\.0\.0\.1:(\d+) to host port (\d+)\.")


async def _stream_and_map(proc: asyncio.subprocess.Process, kci: Dict[str, Any], km: Any, tunneled_ports: List[int]):
    """Stream devtunnel output and map remote ports to local forwarded ports.

    This inspects lines like:
      "SSH: Forwarding from 127.0.0.1:51047 to host port 51042."
    and updates `km` ports accordingly.
    """
    async def _read(pipe, label):
        if pipe is None:
            return
        try:
            while True:
                line = await pipe.readline()
                if not line:
                    break
                try:
                    text = line.decode("utf8", "replace").rstrip()
                except Exception:
                    text = repr(line)
                print(f"[devtunnel {label}] {text}")

                m = _forward_re.search(text)
                if m:
                    local_port = int(m.group(1))
                    remote_port = int(m.group(2))
                    # map remote_port to kernel manager ports
                    if int(kci.get("shell_port")) == remote_port:
                        km.shell_port = local_port
                        tunneled_ports.append(local_port)
                    elif int(kci.get("iopub_port")) == remote_port:
                        km.iopub_port = local_port
                        tunneled_ports.append(local_port)
                    elif int(kci.get("stdin_port")) == remote_port:
                        km.stdin_port = local_port
                        tunneled_ports.append(local_port)
                    elif int(kci.get("hb_port")) == remote_port:
                        km.hb_port = local_port
                        tunneled_ports.append(local_port)
                    elif int(kci.get("control_port")) == remote_port:
                        km.control_port = local_port
                        tunneled_ports.append(local_port)

        except asyncio.CancelledError:
            return

    out_task = asyncio.create_task(_read(proc.stdout, "out"))
    err_task = asyncio.create_task(_read(proc.stderr, "err"))
    # return tasks so caller can cancel if needed
    return out_task, err_task


async def start_devtunnel(tunnel_id: str, token: str, kci: Dict[str, Any], km: Any) -> Tuple[asyncio.subprocess.Process, List[int]]:
    """Start devtunnel connect and return (proc, tunneled_ports).

    The returned `tunneled_ports` list is mutated as forwardings are discovered.
    """
    devtunnel_path = shutil.which("devtunnel")
    if not devtunnel_path:
        raise FileNotFoundError("devtunnel binary not found on PATH. Install from https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started")

    cmd = [devtunnel_path, "connect", tunnel_id, "--access-token", token]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    tunneled_ports: List[int] = []
    # start streaming tasks that will populate tunneled_ports and update km
    await _stream_and_map(proc, kci, km, tunneled_ports)

    print(f"devtunnel started (pid={proc.pid})")
    return proc, tunneled_ports


async def stop_devtunnel(proc: asyncio.subprocess.Process, timeout: float = 5.0) -> None:
    """Terminate the devtunnel process and wait for it to exit."""
    if proc is None:
        return
    if proc.returncode is not None:
        return
    try:
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
