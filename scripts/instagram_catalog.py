#!/usr/bin/env python3
"""Vale & Rossy: prepara foto JPEG e pubblica il catalogo tramite Instagram Login API.

Nessun servizio terzo. Per pubblicare: token IG_ACCESS_TOKEN nei GitHub Secrets,
workflow manuale con conferma PUBBLICA_22_ORA.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "img"
OUTPUT = ROOT / "assets" / "instagram"
LEDGER = ROOT / "instagram_pubblicati.json"
SITE = "https://vale-rossy.pages.dev"
RAW = "https://raw.githubusercontent.com/Robyboscia/Vale-Rossy/main"
API = "https://graph.facebook.com/v25.0"  # Meta Unified Login (SUAT), NON Instagram Login classico
EXPECTED = "ticonciamoperlefeste2026"
EXPECTED_IG_ID = "17841480799194797"  # Identificativo account Vale & Rossy mostrato da Meta Developers


def catalog():
    source = (ROOT / "products.js").read_text(encoding="utf-8")
    match = re.search(r"window\.VALE_ROSSY_PRODUCTS\s*=\s*(\[.*\])\s*;", source, re.S)
    if not match:
        raise RuntimeError("Catalogo non trovato in products.js")
    rows = json.loads(match.group(1))
    assert rows and len({x["id"] for x in rows}) == len(rows), "ID duplicati"
    for p in rows:
        assert p["photos"] and p["summary"], p
        assert len(p["photos"]) <= 10, p["id"]
        assert len(p["summary"]) <= 2200, p["id"]
    return rows


def prepare():
    from PIL import Image, ImageOps
    OUTPUT.mkdir(parents=True, exist_ok=True)
    images = sorted({photo for product in catalog() for photo in product["photos"]})
    for name in images:
        source = SOURCE / name
        if not source.is_file():
            raise FileNotFoundError(str(source))
        dest = OUTPUT / (Path(name).stem + ".jpg")
        if dest.exists() and dest.stat().st_mtime >= source.stat().st_mtime:
            continue
        with Image.open(source) as original:
            pic = ImageOps.exif_transpose(original).convert("RGB")
            fitted = ImageOps.contain(pic, (1080, 1350), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (1080, 1350), "#F6F2EB")
            canvas.paste(fitted, ((1080 - fitted.width) // 2, (1350 - fitted.height) // 2))
            canvas.save(dest, "JPEG", quality=88, optimize=True, progressive=True, subsampling=0)
        print(f"Preparata {dest.relative_to(ROOT)}")
    print(f"Pronte {len(images)} foto per {len(catalog())} post; nessun post inviato.")


def http_session():
    import requests
    sess = requests.Session()
    sess.headers.update({"User-Agent": "ValeRossyInstagramPublisher/1.0"})
    return sess


def request_json(sess, method, url, token, **kwargs):
    params = kwargs.pop("params", {})
    if "access_token" not in params:
        params["access_token"] = token
    result = sess.request(method, url, params=params, timeout=45, **kwargs)
    try:
        data = result.json()
    except ValueError:
        raise RuntimeError(f"Instagram HTTP {result.status_code}: risposta non JSON")
    if not result.ok or "error" in data:
        error = data.get("error", {})
        raise RuntimeError(
            f"Instagram HTTP {result.status_code}: "
            f"{error.get('message', 'Errore API')} "
            f"(code {error.get('code', '?')}, subcode {error.get('error_subcode', '?')})"
        )
    return data


def graph(sess, token, method, path, data=None, fields=None):
    opts = {"data": data} if data is not None else {}
    if fields:
        opts["params"] = {"fields": fields}
    return request_json(sess, method, API + "/" + path.lstrip("/"), token, **opts)


def wait_ready(sess, token, container):
    for _ in range(40):
        status = graph(sess, token, "GET", container, fields="status_code").get("status_code")
        if status in ("FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Contenitore Instagram {container}: {status}")
        time.sleep(6)
    raise RuntimeError(f"Timeout elaborazione foto Instagram: {container}")


def photo_url(sess, photo):
    filename = Path(photo).stem + ".jpg"
    for base in (SITE + "/assets/instagram", RAW + "/assets/instagram"):
        url = base + "/" + filename
        try:
            r = sess.head(url, timeout=20, allow_redirects=True)
            if r.ok and "image/jpeg" in r.headers.get("content-type", "").lower() and int(r.headers.get("content-length", "2000")) > 1000:
                return url
        except Exception:
            pass
    raise RuntimeError(f"Immagine JPEG non ancora disponibile pubblicamente: {filename}")


def quota(sess, token, user_id):
    out = graph(sess, token, "GET", f"{user_id}/content_publishing_limit", fields="quota_usage,config")
    rows = out.get("data", [])
    info = rows[0] if rows else out
    config = info.get("config") or {}
    if isinstance(config, list):
        config = config[0] if config else {}
    used = info.get("quota_usage")
    limit = config.get("quota_total")
    if used is None or limit is None:
        raise RuntimeError("Impossibile verificare la quota di pubblicazione dell'account. Interrotto per sicurezza.")
    if int(used) >= int(limit):
        raise RuntimeError(f"Quota di Instagram esaurita: {used}/{limit} nelle ultime 24 ore.")
    print(f"Quota Instagram: {used}/{limit}")
    return int(limit) - int(used)


def current_media(sess, token, user_id):
    result = graph(sess, token, "GET", f"{user_id}/media", fields="id,caption,permalink")
    found = {}
    for entry in result.get("data", []):
        if entry.get("caption"):
            found[entry["caption"].strip()] = entry
    return found


def commit_log():
    subprocess.run(["git", "add", str(LEDGER.relative_to(ROOT))], cwd=ROOT, check=True)
    changes = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if changes.returncode != 0:
        subprocess.run(["git", "-c", "user.name=github-actions[bot]",
                        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                        "commit", "-m", "Registra pubblicazioni Instagram Vale & Rossy"], cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)


def publish():
    if os.getenv("CONFIRM_INSTAGRAM_PUBLISH") != "PUBBLICA_22_ORA":
        raise RuntimeError("Conferma mancante: nessun post pubblicato.")
    token = os.getenv("IG_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Secret IG_ACCESS_TOKEN non configurato. Nessun post pubblicato.")
    products = catalog()
    sess = http_session()
    account = graph(sess, token, "GET", EXPECTED_IG_ID, fields="id,username")
    username = (account.get("username") or "").lower()
    if username != EXPECTED or str(account.get("id")) != EXPECTED_IG_ID:
        raise RuntimeError(f"Account Instagram non autorizzato: @{username}. Atteso @{EXPECTED} ({EXPECTED_IG_ID}).")
    user_id = EXPECTED_IG_ID
    print(f"Account verificato: @{username}; {len(products)} creazioni da pubblicare.")
    already_online = current_media(sess, token, user_id)
    log = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    if not isinstance(log, dict):
        raise RuntimeError("Registro pubblicazioni non valido.")
    for index, product in enumerate(products, start=1):
        key = product["id"]
        caption = product["summary"].strip()  # COPY ESATTAMENTE COME SUL SITO
        if key in log:
            print(f"[{index}/{len(products)}] Gia registrato: {product['name']}")
            continue
        if caption in already_online:
            post = already_online[caption]
            print(f"[{index}/{len(products)}] Post gia su Instagram: {product['name']}")
            log[key] = {"id": post["id"], "permalink": post.get("permalink"), "recovered": True}
            LEDGER.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            commit_log()
            continue
        quota(sess, token, user_id)
        urls = [photo_url(sess, name) for name in product["photos"]]
        if len(urls) == 1:
            container = graph(sess, token, "POST", f"{user_id}/media",
                              data={"image_url": urls[0], "caption": caption})["id"]
            wait_ready(sess, token, container)
        else:
            children = []
            for url in urls:
                child = graph(sess, token, "POST", f"{user_id}/media",
                              data={"image_url": url, "is_carousel_item": "true"})["id"]
                wait_ready(sess, token, child)
                children.append(child)
            container = graph(sess, token, "POST", f"{user_id}/media",
                              data={"media_type": "CAROUSEL", "children": ",".join(children),
                                    "caption": caption})["id"]
            wait_ready(sess, token, container)
        post_id = graph(sess, token, "POST", f"{user_id}/media_publish",
                        data={"creation_id": container})["id"]
        print(f"[{index}/{len(products)}] PUBBLICATO: {product['name']} (ID {post_id})")
        log[key] = {"id": post_id, "name": product["name"],
                    "published_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        LEDGER.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        commit_log()
        already_online[caption] = {"id": post_id}
        time.sleep(3)
    print(f"Terminato: {len(log)} creazioni registrate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("prepare", "publish"))
    args = parser.parse_args()
    if args.operation == "prepare":
        prepare()
    else:
        publish()
