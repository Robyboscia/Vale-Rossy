# Vale & Rossy — La bottega di Natale

Sito-vetrina statico per decorazioni natalizie artigianali.

## Contenuti

- `index.html` — home e catalogo
- `styles.css` — grafica responsive
- `script.js` — navigazione, filtri, gallerie e contatti
- `products.js` — elenco creazioni: aggiornarlo quando arrivano nuove foto
- `config.js` — inserire WhatsApp, Instagram o email prima della pubblicazione
- `assets/img/` — fotografie ottimizzate

## Prima di pubblicare

Aprire `config.js` e inserire i recapiti effettivi, con il consenso del titolare. Verificare schede e descrizioni in `products.js`. Il sito non contiene un checkout né prezzi, e non costituisce un negozio online completo. Verificare separatamente i requisiti per l'attività di vendita.

## Da GitHub a Cloudflare Pages

1. Creare un repository GitHub chiamato per esempio `vale-e-rossy` (preferibilmente **privato** per mantenere riservato il codice sorgente).
2. Caricare **i file di questa cartella nella radice del repository**, in modo che `index.html` sia visibile subito nel livello principale. Non caricare lo ZIP come unico file.
3. In Cloudflare: **Workers & Pages > Create application > Pages > Connect to Git** e autorizzare l'accesso al repository.
4. Scegliere repository e branch `main`; selezionare nessun framework, **Build command** vuoto (oppure `exit 0`) e **Build output directory** `.` (la radice del progetto).
5. Pubblicare e verificare l'indirizzo gratuito `*.pages.dev`.
6. In seguito, nella sezione **Custom domains** del progetto Pages, collegare il dominio `.it` acquistato a parte e configurare DNS/nameserver come indicato dal servizio.

Dopo la connessione, ogni aggiornamento del branch `main` può ridistribuire automaticamente il sito su Cloudflare.

**Nota:** GitHub ospita i file; Cloudflare Pages pubblica il sito. Per questo catalogo che può promuovere vendite non usiamo GitHub Pages come hosting gratuito, perché i relativi termini pongono restrizioni ai siti commerciali.

Riferimenti: https://developers.cloudflare.com/pages/get-started/git-integration/ · https://developers.cloudflare.com/pages/framework-guides/deploy-anything/ · https://developers.cloudflare.com/pages/configuration/custom-domains/
