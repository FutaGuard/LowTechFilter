"""移除 hosts.txt 中已失效（NXDOMAIN）的黑名單網域。

只看 `||domain^` 規則；白名單 `@@`、含萬用字元或格式不符的規則一律保留。
判定與 TW165 workflow 相同：只有 NXDOMAIN 視為失效，逾時或其他錯誤都保留。

用法：
    python AutoBuild/prune_dead.py                 # 直接改寫 hosts.txt
    python AutoBuild/prune_dead.py --dry-run       # 只列出結果
    python AutoBuild/prune_dead.py nofarm.txt -r 1.1.1.1
"""

import argparse
import random
import re
import socket
import struct
import sys
from concurrent.futures import ThreadPoolExecutor

RULE_PATTERN = re.compile(
    r"^\|\|((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63})\^?$",
    re.IGNORECASE,
)

RCODE_NOERROR = 0
RCODE_NXDOMAIN = 3
QTYPE_A = 1
QCLASS_IN = 1


def build_query(qid: int, domain: str) -> bytes:
    header = struct.pack("!HHHHHH", qid, 0x0100, 1, 0, 0, 0)  # RD=1, QDCOUNT=1
    qname = b"".join(
        bytes([len(label)]) + label for label in domain.encode("idna").split(b".")
    )
    return header + qname + b"\x00" + struct.pack("!HH", QTYPE_A, QCLASS_IN)


def query_rcode(domain: str, resolver: str, timeout: float, retry: int) -> int | None:
    """回傳 DNS RCODE；重試後仍無回應則回傳 None。SERVFAIL 等暫時性錯誤會重試。"""
    rcode = None
    for _ in range(retry):
        qid = random.getrandbits(16)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((resolver, 53))
                sock.send(build_query(qid, domain))
                while True:
                    data = sock.recv(4096)
                    if len(data) < 12:
                        continue
                    rid, flags = struct.unpack("!HH", data[:4])
                    if rid == qid and flags & 0x8000:  # QR=1
                        break
            except OSError:  # socket.timeout 也是 OSError
                continue
        rcode = flags & 0x000F
        if rcode in (RCODE_NOERROR, RCODE_NXDOMAIN):
            break
    return rcode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", nargs="?", default="hosts.txt")
    parser.add_argument("-r", "--resolver", default="8.8.8.8")
    parser.add_argument("-w", "--workers", type=int, default=32)
    parser.add_argument("-t", "--timeout", type=float, default=3.0)
    parser.add_argument("--retry", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", help="只輸出結果，不改檔")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()

    rule_domain: dict[int, str] = {}
    for i, line in enumerate(lines):
        m = RULE_PATTERN.match(line.strip())
        if m:
            rule_domain[i] = m.group(1).lower()
    domains = sorted(set(rule_domain.values()))
    print(f"檢查 {len(domains)} 個網域（resolver {args.resolver}）…", file=sys.stderr)

    with ThreadPoolExecutor(args.workers) as pool:
        rcodes = dict(
            zip(
                domains,
                pool.map(
                    lambda d: query_rcode(d, args.resolver, args.timeout, args.retry),
                    domains,
                ),
            )
        )

    dead = {d for d, rc in rcodes.items() if rc == RCODE_NXDOMAIN}
    unknown = {d: rc for d, rc in rcodes.items() if rc not in (RCODE_NOERROR, RCODE_NXDOMAIN)}

    removed = {i for i, d in rule_domain.items() if d in dead}
    # 夾在規則之間、緊接被刪規則的註解是該規則的附註（例如 archive 連結），一起刪
    for i, line in enumerate(lines):
        prev = lines[i - 1].strip() if i else ""
        if line.startswith("!") and prev and not prev.startswith("!") and i + 1 in removed:
            removed.add(i)

    # 以空行分段；某段的規則被刪光、只剩註解時，整段（分類標題）一起刪
    blocks: list[list[int]] = []
    for i, line in enumerate(lines):
        if not line.strip():
            blocks.append([])
        elif blocks:
            blocks[-1].append(i)
        else:
            blocks.append([i])
    kept_blocks: list[list[str]] = []
    dropped_headers: list[str] = []
    for block in filter(None, blocks):
        rest = [i for i in block if i not in removed]
        if len(rest) < len(block) and all(lines[i].startswith("!") for i in rest):
            dropped_headers.extend(lines[i] for i in rest)
        else:
            kept_blocks.append([lines[i] for i in rest])

    for d in sorted(dead):
        print(f"NXDOMAIN\t{d}")
    for d, rc in sorted(unknown.items()):
        print(f"{'TIMEOUT' if rc is None else f'RCODE={rc}'}\t{d}\t(保留)")
    for line in dropped_headers:
        print(f"刪除空分類\t{line}")
    print(
        f"共 {len(domains)}，NXDOMAIN {len(dead)}，無法判定 {len(unknown)}，"
        f"刪除規則與附註 {len(removed)} 行、空分類標題 {len(dropped_headers)} 行",
        file=sys.stderr,
    )

    if not args.dry_run and dead:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(
                "\n\n".join("\n".join(b) for b in kept_blocks)
                + ("\n" if text.endswith("\n") else "")
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
