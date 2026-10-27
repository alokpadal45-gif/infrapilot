import json
import math
import sys
import urllib.parse
import urllib.request

PROMETHEUS = "http://localhost:9090"
QUERY = (
    "histogram_quantile(0.95, "
    'rate(shop_http_request_duration_seconds_bucket{path="/checkout"}[1m]))'
)
THRESHOLD_SECONDS = 1.0


def query_prometheus(promql):
    url = PROMETHEUS + "/api/v1/query?" + urllib.parse.urlencode({"query": promql})
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)


def main():
    data = query_prometheus(QUERY)
    results = data["data"]["result"]

    if not results:
        print("NO DATA: Prometheus has no /checkout numbers yet")
        return 2

    value = float(results[0]["value"][1])
    if math.isnan(value):
        print("NO DATA: no /checkout requests in the last minute")
        return 2

    if value > THRESHOLD_SECONDS:
        print(f"SLOW: p95 latency is {value:.2f}s (limit {THRESHOLD_SECONDS}s)")
        return 1

    print(f"HEALTHY: p95 latency is {value:.3f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())