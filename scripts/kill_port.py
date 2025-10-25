import argparse, socket
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=5555)
args = parser.parse_args()

# Best-effort: open/close; on Unix suggest fuser/lsof
print(f"If stuck, try: lsof -i :{args.port} | awk 'NR>1 {{print $2}}' | xargs kill -9")
