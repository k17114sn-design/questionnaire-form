"""同時接続の負荷検証用スクリプト（本番アプリには含めない開発用ツール）

指定した人数ぶんの「20問回答→結果表示」の一連の流れを同時に実行し、
成功率と所要時間を計測する。
"""

import argparse
import concurrent.futures
import http.cookiejar
import time
import urllib.request


def simulate_user(base_url: str, total_questions: int) -> tuple[bool, float]:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    start = time.time()
    try:
        opener.open(urllib.request.Request(f"{base_url}/start", method="POST"), timeout=15).read()
        for n in range(1, total_questions + 1):
            opener.open(
                urllib.request.Request(
                    f"{base_url}/question/{n}", data=b"value=3", method="POST"
                ),
                timeout=15,
            ).read()
        resp = opener.open(f"{base_url}/result", timeout=15)
        body = resp.read()
        ok = resp.status == 200 and b"hero-name" in body
    except Exception:
        ok = False
    return ok, time.time() - start


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--questions", type=int, default=20)
    args = parser.parse_args()

    overall_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.users) as executor:
        results = list(
            executor.map(lambda _: simulate_user(args.url, args.questions), range(args.users))
        )
    overall_elapsed = time.time() - overall_start

    successes = [t for ok, t in results if ok]
    failures = args.users - len(successes)

    print(f"users: {args.users}")
    print(f"success: {len(successes)} / {args.users}  (failures: {failures})")
    print(f"total wall time for batch: {overall_elapsed:.2f}s")
    if successes:
        print(f"per-user time: avg={sum(successes)/len(successes):.2f}s max={max(successes):.2f}s min={min(successes):.2f}s")


if __name__ == "__main__":
    main()
