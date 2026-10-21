# documents/

Client material. Everything in this folder except this README is gitignored and
must never be committed.

| Path | Holds |
|---|---|
| `legacy-src/Payroll/` | Legacy iPay `Payroll.exe` v21.1.0.4, decompiled to C# with ILSpy 9.1 (originally VB.NET) |
| `legacy-src/iPay_IRAS_API/` | Legacy `iPay_IRAS_API.dll`, decompiled |
| `legacy-src/iPayLicenseService/` | Legacy `iPayLicenseService.exe`, decompiled |
| `legacy-src/_analysis/` | Machine-extracted indexes (report template catalog, rate tables) |

The decompiled source is proprietary to Ingenious Business Software Pte Ltd and may
contain hardcoded credentials. Read it; never copy secret values out of it.

The legacy installation it was decompiled from lives outside the repo, under
`Customers/Ingenious/iPay/`. Its `DBList.xml` and `*.ipay` files hold live connection
settings and are not to be opened or copied here.

The reverse-engineered specification built from this source is committed under
[`docs/legacy/`](../docs/legacy/).
