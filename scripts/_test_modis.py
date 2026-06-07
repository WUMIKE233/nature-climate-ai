import os, requests, re
os.environ["no_proxy"] = ".nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov"
token = open(r"W:\Nature\.edl_token").read().strip()
s = requests.Session(); s.verify = False
url = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD13Q1/2020/033/"
r = s.get(url, headers={"Authorization": "Bearer " + token}, timeout=30)
for tile in ["h31v11"]:
    pat = "MOD13Q1.A2020033." + tile + ".061.[^\s<>\"]+.hdf"
    matches = re.findall(pat, r.text)
    print(f"{tile}: {matches}")
    if matches:
        fname = matches[0]
        url2 = f"https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD13Q1/2020/033/{fname}"
        r2 = s.get(url2, headers={"Authorization": "Bearer " + token}, timeout=120)
        print(f"Download: HTTP {r2.status_code}, size={len(r2.content)} bytes")
        is_html = b"<!DOCTYPE" in r2.content[:100]
        print(f"Is HTML: {is_html}")
