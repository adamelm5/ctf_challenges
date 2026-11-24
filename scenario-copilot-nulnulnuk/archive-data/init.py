from pathlib import Path


source = Path("/run/secrets/ctf_flag")
destination = Path("/data/flag")
flag = source.read_text(encoding="utf-8").strip()
if not flag:
    raise SystemExit("Flag input is empty")
if destination.exists():
    if destination.read_text(encoding="utf-8").strip() != flag:
        raise SystemExit(
            "Archive volume already contains different data; reset it with docker compose down -v"
        )
    print("Archive data already initialized")
    raise SystemExit(0)
destination.write_text(flag + "\n", encoding="utf-8")
destination.chmod(0o444)
print("Archive data initialized")
