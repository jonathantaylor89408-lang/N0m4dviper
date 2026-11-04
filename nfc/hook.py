def hook(r):
    r["_seen"] = r.get("_seen", 0) + 1
    return r
