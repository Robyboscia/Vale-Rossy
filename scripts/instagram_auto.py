#!/usr/bin/env python3
"""Pubblica su Instagram soltanto le nuove foto registrate nel catalogo Vale & Rossy.

Richiede un Instagram Business User Access Token in GitHub Secret IG_ACCESS_TOKEN.
La baseline instagram_auto_state.json impedisce di pubblicare retroattivamente le foto già presenti.
"""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time

from instagram_catalog import (
    ROOT, EXPECTED, EXPECTED_IG_ID, graph, http_session, photo_url,
    quota, wait_ready, catalog,
)

STATE = ROOT / "instagram_auto_state.json"


def load_state():
    if not STATE.is_file():
        raise RuntimeError("Registro autopubblicazioni assente: bloccato per evitare di pubblicare tutto il catalogo.")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("version") != 1 or not isinstance(state.get("seen_photos"), list):
        raise RuntimeError("Registro autopubblicazioni non valido: interrotto.")
    return state


def new_photos(products, seen):
    """Un post per prodotto cambiato; più nuove immagini dello stesso prodotto -> carosello."""
    seen = set(seen)
    pending = []
    reserved = set()
    for product in products:
        photos = [name for name in product["photos"] if name not in seen and name not in reserved]
        if photos:
            reserved.update(photos)
            pending.append((product, photos))
    return pending


def write_and_push(state, message):
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["git", "add", STATE.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if changed.returncode:
        subprocess.run(["git", "-c", "user.name=github-actions[bot]",
                        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                        "commit", "-m", message], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)


def ensure_images_public(sess, names):
    for filename in names:
        for attempt in range(18):
            try:
                url = photo_url(sess, filename)
                break
            except RuntimeError:
                if attempt == 17:
                    raise
                print(f"Attendo disponibilita pubblica JPEG di {filename}...", flush=True)
                time.sleep(10)
        yield url


def main():
    state = load_state()
    products = catalog()
    todo = new_photos(products, state["seen_photos"])
    print(f"Registro iniziale: {len(state['seen_photos'])} fotografie note; "
          f"{sum(len(photos) for _, photos in todo)} foto nuove in {len(todo)} creazioni.", flush=True)

    token = os.getenv("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("Instagram non ancora autorizzato: manca GitHub Secret IG_ACCESS_TOKEN. "
              "Immagini preparate; nessun post pubblicato.", flush=True)
        return
    if not todo and not state.get("pending"):
        print("Nessuna fotografia nuova da pubblicare. Nessuna operazione su Instagram.", flush=True)
        return

    sess = http_session()
    account = graph(sess, token, "GET", "me", fields="id,username,account_type")
    username = str(account.get("username", "")).lower()
    if username != EXPECTED:
        raise RuntimeError(f"Token destinato a @{username}, non a @{EXPECTED}. Niente pubblicazione.")
    uid = str(account["id"])
    if state.get("pending"):
        pending = state["pending"]
        raise RuntimeError(
            f"Pubblicazione precedente da verificare prima di riprendere: {pending['product_id']} "
            f"con contenitore {pending['container_id']}. "
            "Registro non modificato per evitare doppioni."
        )
    for product, photos in todo:
        remaining = quota(sess, token, uid)
        if remaining < 1:
            raise RuntimeError("Quota di pubblicazione Instagram esaurita.")
        image_urls = list(ensure_images_public(sess, photos))
        caption = product["summary"].strip()  # Esattamente il copy sul sito
        if len(image_urls) == 1:
            container = graph(sess, token, "POST", f"{uid}/media",
                              data={"image_url": image_urls[0], "caption": caption})["id"]
            wait_ready(sess, token, container)
        else:
            children = []
            for url in image_urls:
                child = graph(sess, token, "POST", f"{uid}/media",
                              data={"image_url": url, "is_carousel_item": "true"})["id"]
                wait_ready(sess, token, child)
                children.append(child)
            container = graph(sess, token, "POST", f"{uid}/media",
                              data={"media_type": "CAROUSEL",
                                    "children": ",".join(children), "caption": caption})["id"]
            wait_ready(sess, token, container)

        # Salviamo lo stato prima della chiamata di pubblicazione irreversibile.
        # Se la rete fallisce dopo media_publish, non rischiamo un secondo invio automatico.
        state["pending"] = {
            "product_id": product["id"],
            "photos": photos,
            "container_id": container,
            "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        write_and_push(state, f"Instagram: preparata pubblicazione {product['id']}")
        published = graph(sess, token, "POST", f"{uid}/media_publish",
                          data={"creation_id": container})
        post_id = str(published["id"])
        state["seen_photos"] = sorted(set(state["seen_photos"]) | set(photos))
        state.setdefault("posts", []).append({
            "product_id": product["id"], "photos": photos,
            "instagram_id": post_id,
            "published_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
        state["pending"] = None
        write_and_push(state, f"Instagram: pubblicate nuove foto di {product['id']}")
        print(f"PUBBLICATO @{EXPECTED}: {product['name']} ({len(photos)} foto, post {post_id})", flush=True)
        time.sleep(3)
    print("Tutte le nuove fotografie sono state pubblicate.", flush=True)


if __name__ == "__main__":
    main()
