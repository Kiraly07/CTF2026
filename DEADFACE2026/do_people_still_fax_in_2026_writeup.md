# Do People Still Fax in 2026? (3 of 4 series) — Web (100 pts)

"Websites with documents. Exposure of files are always nasty little vulnerabilities. Find a document that doesn't belong to you." Same Health Spark app at http://45.79.200.170:3000.

## How I solved it

**Finding the document endpoint.** The portal pages never mention it, but there's a hidden Swagger UI at **`/api-docs`** (redirects to /api-docs/, spec embedded in swagger-ui-init.js). It documents one endpoint the site JS never calls:

```
POST /file_document?id=<integer>
body: {"departmentid": ...}
"Download a member document (PDF)"
```

The spec even leaks that "the website can only host 1000 files at most" with an example id of 1009.

**The IDOR.** The endpoint takes a document id and a `departmentid` in the body — but never checks that the document belongs to the department in *your* JWT. So with john.smith's normal user token (departmentid 10685), you can just ask for another department's member records:

```json
POST /file_document?id=1020
Authorization: Bearer <user JWT>
{"departmentid": 18432}
```

200 OK, `application/pdf` — a member medical record that definitely doesn't belong to us. Cross-checks confirm the access control logic: your own department's file (id 1009 + 10685) works, asking for *your* file via another department (1009 + 18432) gives 403, unknown ids 404. The check is "does the departmentid in the body match the document's department" — the token is never consulted.

**Reading the flag.** The flag isn't in the visible PDF text — it's in the PDF's uncompressed string objects (the metadata area):

```
Title: Health Spark Member Record 1020
object 17: (deadface{someone_should_report_this})
```

`strings file.pdf` or any PDF object viewer shows it right away.

## Dead ends worth mentioning

There's no actual fax machine/spool anywhere — "fax" is just the theme. And don't get distracted like I did by the mass-assignment + SSRF chain (`POST /api/profile {"role":"admin"}` → `/api/admin/fetch-photo` → internal console at localhost:8080): that console's `admin_console_token: deadface{oh_you_shouldnt_be_here}` is a **decoy** — rejected by the CTF for this challenge. The document exposure they wanted is the boring old IDOR on /file_document.

## Flag

```
deadface{someone_should_report_this}
```
