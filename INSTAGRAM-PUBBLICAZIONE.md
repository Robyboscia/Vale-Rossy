# Instagram Vale & Rossy — pubblicazione gratuita via GitHub

## NOVITÀ — Autopubblicazione delle nuove foto sul sito

✅ Il workflow [Vale & Rossy | autopubblica nuove foto](https://github.com/Robyboscia/Vale-Rossy/actions/workflows/instagram-auto.yml) è installato nel ramo `main` e si avvia da solo quando modifichiamo `products.js` oppure i file in `assets/img/`.

**Attivazione: una tantum**: configura Meta Instagram API with Instagram Login e inserisci il token in [GitHub Secret IG_ACCESS_TOKEN](https://github.com/Robyboscia/Vale-Rossy/settings/secrets/actions/new). Il workflow rimane inattivo per la pubblicazione se il secret non è presente. Non usare Metricool e TinyFish.

**Cosa succede dopo l'autorizzazione:**
1. Carica la foto nella cartella `assets/img/` e inserisci il **nuovo nome file** nella scheda di `products.js`. Il file da solo, non inserito in una scheda, non viene pubblicato.
2. GitHub Actions crea automaticamente il JPEG 1080×1350 e lo rende disponibile su `assets/instagram/`.
3. Instagram pubblica la foto con la **stessa descrizione** (`summary`) del sito; se più foto vengono aggiunte contemporaneamente alla stessa scheda, crea un carosello unico.
4. Il registro `instagram_auto_state.json` evita doppioni. Le **37 fotografie già nel sito al momento dell'attivazione** sono state registrate come baseline: non vengono pubblicate automaticamente per errore.
5. Il sistema controlla l'account `@ticonciamoperlefeste2026`, la quota di pubblicazione e lo stato di ogni contenitore. Se la risposta di pubblicazione è incerta, si ferma e richiede una verifica manuale prima di ritentare.

**Attenzione:** se sostituisci la fotografia mantenendo lo stesso nome file, il sistema considera quella fotografia già vista. Per pubblicare una nuova foto usa un nuovo nome file e aggiungilo alla scheda. Se il token è assente, i nuovi elementi restano in attesa e la prossima esecuzione del workflow può riprovarci dopo l'autorizzazione. Il token Instagram può scadere: occorre rinnovarlo periodicamente.

**Stato attuale (01/11/2026):** primo test GitHub Actions completato con successo. Nessuna foto nuova riconosciuta e **nessun post pubblicato**, perché il Secret Meta non è ancora configurato.

---


**Account autorizzato: @ticonciamoperlefeste2026.** Non usare Metricool o TinyFish.

## Stato del progetto

- Catalogo: `products.js`, 22 creazioni.
- Immagini: `assets/instagram/*.jpg`, 37 fotografie convertite a 1080 × 1350 senza tagli.
- Testi: descrizioni `summary` originali del sito, senza hashtag/prezzi aggiunti.
- Oggetti con più immagini: un post carosello per prodotto (fino a 10 immagini).
- Automazione di preparazione: [GitHub Actions — prepara](https://github.com/Robyboscia/Vale-Rossy/actions/workflows/instagram-prepara.yml).
- Automazione di pubblicazione: [GitHub Actions — PUBBLICA subito](https://github.com/Robyboscia/Vale-Rossy/actions/workflows/instagram-pubblica.yml).

## Autorizzazione Meta: una tantum

Per l'API **Instagram Login** serve un'app Meta con un token utente autorizzato per l'account Business.

1. Apri [Meta for Developers](https://developers.facebook.com/apps/) ed effettua l'accesso con l'account autorizzato a gestire **@ticonciamoperlefeste2026**.
2. Crea o seleziona un'app Meta e configura il prodotto **Instagram API with Instagram Login**. In base all'interfaccia potresti dover configurare prima un caso d'uso Instagram Business.
3. Autorizza l'account Instagram Business come tester/utente dell'app, se richiesto dal pannello.
4. Genera un **Instagram User Access Token** con le autorizzazioni `instagram_business_basic` e `instagram_business_content_publish`. Usa il flusso Instagram Login, **non** il token Facebook Login.
5. Senza incollare il token in una chat, visita [Aggiungi GitHub Actions Secret](https://github.com/Robyboscia/Vale-Rossy/settings/secrets/actions/new), imposta **Name = IG_ACCESS_TOKEN** e incolla il token come **Secret**.
6. Vai su [PUBBLICA subito](https://github.com/Robyboscia/Vale-Rossy/actions/workflows/instagram-pubblica.yml), seleziona **Run workflow**, scegli **PUBBLICA_22_ORA**, premi di nuovo **Run workflow**.

**Non creare una Pagina Facebook soltanto per questo flusso:** la modalità Instagram Login funziona direttamente con l'account professionale.

## Cosa fa il programma

1. Controlla che il token appartenga esattamente a `@ticonciamoperlefeste2026`; altrimenti non pubblica.
2. Controlla la quota API di pubblicazione fornita da Instagram. Se insufficiente, si ferma.
3. Controlla i post esistenti e il registro `instagram_pubblicati.json` per evitare duplicati.
4. Legge **in tempo reale** i prodotti da `products.js`.
5. Per ciascun prodotto pubblica la foto o il carosello con **la stessa descrizione** del sito.
6. Registra e salva sul repository l'ID di ogni post pubblicato, per poter riprendere in caso di interruzione.

### Importante

- I post **non partono automaticamente** finché il workflow manuale non riceve la conferma `PUBBLICA_22_ORA`.
- La procedura può fermarsi se Meta rifiuta i permessi, la quota è insufficiente, il token scade o un'immagine pubblica non è accessibile. Non aggira i limiti della piattaforma.
- Il token è una credenziale sensibile: **mai inserirlo in file del repository o messaggi**; usa solo GitHub Secrets.
- Se in futuro si vuole pubblicare altro, è necessario mantenere il token autorizzato e aggiornare le immagini.
- Per la documentazione ufficiale: [Meta Instagram API with Instagram Login](https://www.postman.com/meta/instagram/folder/1z5vxzu/instagram-api-with-instagram-login).
