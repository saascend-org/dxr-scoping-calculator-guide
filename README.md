# DXR Cyber — scoping calculator guide

Short Pre-Sales guide to the scoping calculator (XYP-AGENT-002): how inputs become days,
how to read the reasoning, how to amend one scope, and how to change the calculator itself.

## The published file is encrypted

`index.html` is a **password gate**, not the guide. The readable page is AES-256-GCM ciphertext
inside it, under a PBKDF2-SHA256 (600k) key. **`GUIDE.md` is git-ignored** — it contains DXR's
effort model, which is the basis of their pricing, and must never be committed in the clear.

The password is not in this repo. `publish.sh` prompts for it.

## Editing

```bash
python3 build.py     # -> index.html, PLAINTEXT, local reading only (never commit)
./publish.sh         # rebuild, re-encrypt, commit, push
```

Edit `GUIDE.md`. **Never edit `index.html`** — it is regenerated, and a stray edit destroys the
gate. `encrypt.js` keeps one `.bak` of whatever it overwrites.

Serve over http, not file://, to preview — `crypto.subtle` needs a secure context.

## Keeping it true

Every figure in the guide is a live production parameter (`Effort_Parameter__mdt`). If the
calculator's bands or rates change, the guide is wrong until it is rebuilt. Re-check with:

```
sf data query --query "SELECT DeveloperName, Service__c, Value__c FROM Effort_Parameter__mdt" --target-org Xypher_Prod
```
