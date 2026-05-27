# AccurioPro ProfiWEB API Reference

**Device**: KONICA MINOLTA AccurioPrint 2100
**Web Interface**: AccurioPro Print Manager (ProfiWEB)
**Base URL**: `http://192.168.1.131:30083`
**Software Version**: 1.0PW-4030

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Sessions](#authentication--sessions)
3. [API Endpoints (Complete List)](#api-endpoints-complete-list)
4. [Core Workflows](#core-workflows)
5. [File Upload (jobSubmit.fcgi)](#file-upload-jobsubmitfcgi)
6. [Job Management](#job-management)
7. [Print Settings (printFeatures)](#print-settings-printfeatures)
8. [Container/Queue System](#containerqueue-system)
9. [Device Information](#device-information)
10. [The .icjx File Format](#the-icjx-file-format)
11. [Known Issues & Gaps](#known-issues--gaps)
12. [Curl Examples](#curl-examples)

---

## Overview

The AccurioPro ProfiWEB interface is an AngularJS 1.8.2 web application that communicates with the print server via `.fcgi` endpoints. All API calls use standard HTTP GET/POST with URL-encoded form data. Responses are JSON.

The frontend JavaScript is bundled in:
- `http://192.168.1.131:30083/bundle.js` (3.8MB, minified)
- `http://192.168.1.131:30083/build/loader.js`

The internal AngularJS module is called `"profiweb"` and uses a custom `fcgiSrv` service that wraps `$http`.

### Request Format

All POST requests use `Content-Type: application/x-www-form-urlencoded`. Parameters are URL-encoded using JavaScript's `encodeURIComponent()` (uses `%20` for spaces, NOT `+`).

The `fcgiSrv` service automatically appends these params to every request:
- `sessionId` - from register.fcgi
- `viewId` - from register.fcgi (usually 0)
- `ts` - current timestamp in milliseconds

---

## Authentication & Sessions

### 1. Register a Session

```
GET /register.fcgi?sessionId=-1&viewId=-1&ts={timestamp}
```

**Response:**
```json
{
  "sessionId": "stvGaOk77Lwn1pp8NpKMPMSiOHWA",
  "viewId": 0
}
```

### 2. Login as Operator (No Password Required)

```
POST /sessionLogin.fcgi
Content-Type: application/x-www-form-urlencoded

notauthuser=Operator&sessionId={sessionId}&viewId=0&ts={timestamp}
```

**Response:**
```json
{
  "displayUserName": "Operator",
  "canCopy": true,
  "canScan": true,
  "canPrint": true,
  "canCreateUserBox": true,
  "canCopyBlack": false,
  "canPrintBlack": false
}
```

### 3. Admin Login (Password Required)

For the 2100 model, admin password is `12345678`.

```
POST /checkAdminPwd.fcgi
Content-Type: application/x-www-form-urlencoded

password={password}&sessionId={sessionId}&viewId=0&ts={timestamp}
```

### 4. Logout

```
POST /logout.fcgi
```

### 5. Keep-Alive

```
GET /alive.fcgi?timeout={ms}
```

**Response:**
```json
{"result": {"type": "ok", "details": []}}
```

---

## API Endpoints (Complete List)

All discovered `.fcgi` endpoints from the bundle.js analysis:

### Session/Auth
| Endpoint | Method | Description |
|----------|--------|-------------|
| `register.fcgi` | GET | Create new session |
| `sessionLogin.fcgi` | POST | Login (operator or user) |
| `checkAdminPwd.fcgi` | POST | Admin password check |
| `logout.fcgi` | POST | End session |
| `alive.fcgi` | GET | Keep-alive / health check |
| `initialUserStatus.fcgi` | GET | Get user auth info |

### Job Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `jobSubmit.fcgi` | POST (multipart) | **Upload a file as a new job** |
| `jobList.fcgi` | GET | List jobs in a container |
| `jobDetails.fcgi` | GET | Get full job details + print settings |
| `jobLock.fcgi` | POST | Lock/unlock a job for editing |
| `setJobDetailsAndUnlock.fcgi` | POST | Save job settings and unlock |
| `jobPrintAndUnlock.fcgi` | POST | Print a job and unlock |
| `jobDelete.fcgi` | POST | Delete a job |
| `jobCopy.fcgi` | POST | Duplicate a job |
| `jobMove.fcgi` | POST | Move job between containers |
| `jobRename.fcgi` | POST | Rename a job |
| `jobBackup.fcgi` | POST | Export/backup a job |
| `jobRestore.fcgi` | POST | Import/restore a job |
| `jobReset.fcgi` | POST | Reset a job |
| `jobSetPriority.fcgi` | POST | Set job priority |
| `jobMergeAndUnlock.fcgi` | POST | Merge jobs |
| `jobPreview.fcgi` | GET | Get job page preview |
| `checkConstraints.fcgi` | POST | Validate print settings |
| `setPagesAndUnlock.fcgi` | POST | Save page-specific settings |

### Container/Box Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `containerList.fcgi` | GET | List all containers/queues |
| `containerCreate.fcgi` | POST | Create a new box |
| `containerDelete.fcgi` | POST | Delete a box |
| `containerRename.fcgi` | POST | Rename a box |
| `containerLock.fcgi` | POST | Lock a container |
| `containerUnlock.fcgi` | POST | Unlock a container |
| `containerSetPassword.fcgi` | POST | Set box password |

### Configuration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `deviceInfo.fcgi` | GET | Full device info (trays, toner, status) |
| `productionData.fcgi` | GET | Current print job production status |
| `paperProfileList.fcgi` | GET | List paper profiles |
| `customSizeList.fcgi` | GET | List custom paper sizes |
| `customSizeCreate.fcgi` | POST | Create custom size |
| `customSizeDelete.fcgi` | POST | Delete custom size |
| `colorDefaultSettings.fcgi` | GET | Color settings |
| `saveColorDefaultSettings.fcgi` | POST | Save color settings |

### Hot Folders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `hotFolderList.fcgi` | GET | List hot folders |
| `hotFolderDetails.fcgi` | GET | Hot folder details |
| `hotFolderCreate.fcgi` | POST | Create hot folder |
| `hotFolderDelete.fcgi` | POST | Delete hot folder |
| `hotFolderLock.fcgi` | POST | Lock hot folder |
| `setHotFolderDetailsAndUnlock.fcgi` | POST | Save & unlock hot folder |
| `hotFolderUserList.fcgi` | GET | List hot folder users |

### Tone Curves
| Endpoint | Method | Description |
|----------|--------|-------------|
| `toneCurveList.fcgi` | GET | List tone curves |
| `toneCurveDetails.fcgi` | GET | Tone curve details |
| `toneCurveCreate.fcgi` | POST | Create tone curve |
| `toneCurveDelete.fcgi` | POST | Delete tone curve |
| `toneCurveCmyk.fcgi` | POST | Get CMYK data |
| `toneCurvePreview.fcgi` | POST | Preview tone curve |
| `toneCurveProofPrint.fcgi` | POST | Print proof |
| `toneCurveBackup.fcgi` | POST | Backup tone curves |
| `toneCurveRestore.fcgi` | POST | Restore tone curves |
| `toneCurveLock.fcgi` | POST | Lock tone curve |
| `setToneCurveDetailsAndUnlock.fcgi` | POST | Save & unlock |

### Favorites & Misc
| Endpoint | Method | Description |
|----------|--------|-------------|
| `listFavoriteJobSettings.fcgi` | GET | List saved presets |
| `loadFavoriteJobSettings.fcgi` | GET | Load a preset |
| `saveFavoriteJobSettings.fcgi` | POST | Save a preset |
| `localization.fcgi` | GET | Get UI translations |
| `localizationUpload.fcgi` | POST | Upload translations |
| `localizationDownload.fcgi` | GET | Download translations |
| `setLanguage.fcgi` | POST | Set UI language |
| `setUnits.fcgi` | POST | Set measurement units |
| `getUnits.fcgi` | GET | Get measurement units |
| `getSettingsPreview.fcgi` | POST | Preview settings effect |
| `printerSearch.fcgi` | GET | Search for printers |
| `accountingDownload.fcgi` | GET | Download accounting data |
| `accountingGetLimits.fcgi` | GET | Get accounting limits |
| `profileList.fcgi` | GET | List profiles |
| `spotColorTableList.fcgi` | GET | List spot color tables |

### File Transfer
| Endpoint | Method | Description |
|----------|--------|-------------|
| `createDownload.fcgi` | POST (multipart) | Upload a file and get a download key |
| `getDownload.fcgi` | GET | Download a file by key |

### Other Pages
| Path | Description |
|------|-------------|
| `/version` | Server version string |
| `/buildtime` | Build timestamp |
| `/reload.html` | Force reload page |

---

## Core Workflows

### Upload PDF → Hold Queue (CONFIRMED WORKING)

```
1. GET  /register.fcgi          → get sessionId
2. POST /sessionLogin.fcgi      → login as Operator
3. POST /jobSubmit.fcgi          → upload PDF file (multipart)
4. GET  /jobList.fcgi            → verify job appears in queue
```

### Import .icjx → Print (CONFIRMED WORKING - RECOMMENDED FOR .icjx FILES)

```
1. GET  /register.fcgi          → get sessionId
2. POST /sessionLogin.fcgi      → login as Operator
3. POST /jobRestore.fcgi         → import .icjx file (preserves ALL embedded settings)
4. POST /getJobs.fcgi            → find the imported jobId in Hold queue
5. POST /jobLock.fcgi            → lock job (action=lock)
6. GET  /jobDetails.fcgi         → get job details (settings already applied from .icjx)
7. POST /setJobDetailsAndUnlock.fcgi → print with print=true (via browser JS)
```

### Upload PDF → Print (via Browser Automation)

```
1. GET  /register.fcgi          → get sessionId
2. POST /sessionLogin.fcgi      → login as Operator
3. POST /jobSubmit.fcgi          → upload PDF to Hold queue
4. POST /getJobs.fcgi            → find jobId
5. POST /jobLock.fcgi            → lock job (action=lock)
6. GET  /jobDetails.fcgi         → get job details
7. POST /setJobDetailsAndUnlock.fcgi → save settings with print=true (via browser JS)
```

**NOTE**: Step 7 (`setJobDetailsAndUnlock.fcgi`) only works reliably from the browser's JavaScript context. See [Known Issues](#known-issues--gaps).

### Modify Job Settings

```
1. POST /jobLock.fcgi            → lock job (action=lock)
2. GET  /jobDetails.fcgi         → get current settings
3. POST /setJobDetailsAndUnlock.fcgi → save modified settings (via browser JS)
```

---

## Import .icjx Files (jobRestore.fcgi) — CONFIRMED WORKING

The `jobRestore.fcgi` endpoint imports `.icjx` files directly into the Hold queue, **preserving all embedded print settings** (duplex, paper size, copies, image shift, etc.). This is the recommended way to import jobs that were exported from ProfiWEB.

### Curl Example

```bash
SESSION="your-session-id"

curl -X POST "http://192.168.1.131:30083/jobRestore.fcgi" \
  -H "Content-Type: multipart/form-data" \
  -F "sessionId=$SESSION" \
  -F "viewId=0" \
  -F "file=@/path/to/job.icjx;filename=job.icjx;type=application/octet-stream"
```

### Request Format (from browser capture)

```
POST /jobRestore.fcgi HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...\r\n
Content-Disposition: form-data; name="sessionId"\r\n
\r\n
{sessionId}\r\n
------WebKitFormBoundary...\r\n
Content-Disposition: form-data; name="viewId"\r\n
\r\n
0\r\n
------WebKitFormBoundary...\r\n
Content-Disposition: form-data; name="file"; filename="Proba booklet.pdf 20260312114633.icjx"\r\n
Content-Type: application/octet-stream\r\n
\r\n
{binary file data}\r\n
------WebKitFormBoundary...--\r\n
```

### Response (success)

```json
{"result": {"type": "ok", "details": []}}
```

### Key Points

- The imported job appears in the **Hold queue** (containerId: 268435441)
- **All print settings from the .icjx are preserved** — duplex, paper size, image shift, paper profile, etc.
- The job status will be `unedited` or `edited` depending on the original export state
- After import, use `getJobs.fcgi` to find the new jobId, then lock → print
- Unlike `jobSubmit.fcgi` (which rejects .icjx with `AioJobFormatNotSupported`), `jobRestore.fcgi` is specifically designed for .icjx import

### Difference: jobSubmit.fcgi vs jobRestore.fcgi

| Feature | jobSubmit.fcgi | jobRestore.fcgi |
|---------|---------------|-----------------|
| Accepts PDF | ✅ | ❌ |
| Accepts .icjx | ❌ (AioJobFormatNotSupported) | ✅ |
| Preserves print settings | N/A (PDFs have no settings) | ✅ (from .icjx metadata) |
| Use case | New documents | Re-importing exported jobs |

---

## File Upload — PDF (jobSubmit.fcgi)

### CONFIRMED WORKING - Upload to Hold Queue

```bash
curl -X POST "http://192.168.1.131:30083/jobSubmit.fcgi" \
  -F "file=@/path/to/document.pdf;filename=document.pdf" \
  -F "sessionId={sessionId}" \
  -F "viewId=0" \
  -F "containerId=268435441" \
  -F "hold=true"
```

**Parameters:**
- `file` - The PDF/PS/TIFF file (multipart file upload)
- `filename` - Name for the file (in Content-Disposition)
- `sessionId` - From register.fcgi
- `viewId` - Usually 0
- `containerId` - Target queue (268435441 = Hold)
- `hold` - "true" to hold, omit or "false" to process

**Response (success):**
```json
{"result": {"type": "ok", "details": []}}
```

**Supported file types** (from bundle.js): `ps`, `pdf`, `pdfAppe`, `tiff`, `jpeg`, `ppml`

### Upload Generic File (createDownload.fcgi)

Used for non-job uploads (tone curves, localization files, etc.):

```bash
curl -X POST "http://192.168.1.131:30083/createDownload.fcgi" \
  -F "file=@/path/to/file" \
  -F "contentType=application/pdf" \
  -F "filename=myfile.pdf"
```

**Response:**
```json
{"key": "+RW4L/4f8w"}
```

The key can be used with `getDownload.fcgi` to retrieve the file.

---

## Job Management

### List Jobs in a Container

```
GET /jobList.fcgi?containerId=268435441&sessionId={sid}&viewId=0&ts={ts}
```

**Response:**
```json
{
  "jobLists": [{
    "containerId": 268435441,
    "jobs": [{
      "jobId": 20750,
      "name": "az chovek sam booklet.pdf",
      "owner": "",
      "pages": 14,
      "jobType": "print",
      "status": "edited",
      "pdl": "pdf",
      "pdlFileSize": 632127,
      "datePrintEnd": 1773235245,
      "dateModified": 1773235200,
      "dateStored": 1773235000,
      "isPrinted": "True",
      "notRiped": "False",
      "activeToHold": "False",
      "editingPlace": "editedCentro",
      "engineOnly": "False",
      "workflow": "",
      "form": "False",
      "printFeatures": {
        "Orientation": "Land",
        "Fold": "None",
        "FoldDirection": "Inside",
        "NumCopies": 1,
        "OutputBin": "Auto",
        "TargetPaperSize": "A4",
        "MediaTypeAuto": "Plain",
        "Duplex": "True",
        "Layout": "None",
        "Staple": "None",
        "PageSize": "A4"
      }
    }]
  }]
}
```

**Job statuses:** `unedited`, `editing`, `edited`, `ripping`, `ripped`, `printing`, `warningStopPrint`

### Get Full Job Details

```
GET /jobDetails.fcgi?jobId={id}&containerId={cid}&sessionId={sid}&viewId=0&ts={ts}
```

Returns COMPLETE job info including ALL printFeatures (100+ settings), pageDetails (per-page settings), and pageSettings.

### Lock a Job

```
POST /jobLock.fcgi
action=lock&jobId={id}&containerId={cid}&sessionId={sid}&viewId=0&ts={ts}
```

### Unlock a Job

```
POST /jobLock.fcgi
action=unlock&jobId={id}&containerId={cid}&sessionId={sid}&viewId=0&ts={ts}
```

### Delete a Job

```
POST /jobDelete.fcgi
jobId={id}&containerId={cid}&sessionId={sid}&viewId=0&ts={ts}
```

**Note:** Job must NOT be locked (AioJobInUse error).

### Save Settings and Unlock (setJobDetailsAndUnlock.fcgi)

```
POST /setJobDetailsAndUnlock.fcgi
jobId={id}&containerId={cid}&sessionId={sid}&viewId=0&ts={ts}&jobData={urlEncodedJSON}
```

**jobData structure** (from getRipDataObject):
```json
{
  "printFeatures": { ... all print features ... },
  "pageSettings": [],
  "pageDetails": [ ... per-page details ... ],
  "jobToneCurves": {},
  "pageToneCurves": [],
  "inputTrays": [],
  "paperProfileList": [],
  "customSizeList": []
}
```

**To also trigger printing**, add `print=true` to the params (this is what `saveAndPrintAndUnlock` does).

**To process without printing**, add `process=process` or `process=withoutProcessing`.

**⚠️ STATUS: NOT YET WORKING VIA CURL** - See Known Issues section.

---

## Print Settings (printFeatures)

The complete list of available print features (from jobDetails.fcgi response):

### Key Settings
| Feature | Values | Description |
|---------|--------|-------------|
| `NumCopies` | 1-9999 | Number of copies |
| `Duplex` | "True" / "False" | Two-sided printing |
| `PageSize` | "A3", "A4", "A5", etc. | Original document size |
| `TargetPaperSize` | "Auto", "A3", "A4", etc. | Output paper size |
| `InputSlot` | "Auto", "Tray1", "Tray2" | Paper tray selection |
| `Orientation` | "Port" / "Land" | Portrait/Landscape |
| `Layout` | "None", "2up", "4up", etc. | N-up layout |
| `FullBleed` | "True" / "False" | Full bleed printing |
| `FaceUp` | "True" / "False" | Output face up |
| `Collate` | "Sort" / "Group" | Sorting mode |
| `Binding` | "Left", "Right", "Top" | Binding edge |

### Paper & Media
| Feature | Values | Description |
|---------|--------|-------------|
| `MediaTypeAuto` | "Plain", "NoSet", etc. | Media type |
| `MediaWeightAuto` | "Thick2", "Thick4", "NoSet" | Paper weight |
| `MediaColorAuto` | "White", "NoSet" | Paper color |
| `MainPaperProfileIndex` | 0-N | Paper profile index |
| `MediaPrepunchedAuto` | "True" / "False" | Pre-punched paper |
| `FeedDir` | "Auto", "ShortEdge", "LongEdge" | Feed direction |

### Finishing
| Feature | Values | Description |
|---------|--------|-------------|
| `Staple` | "None", etc. | Stapling |
| `Punch` | "None", etc. | Hole punching |
| `Fold` | "None", "HalfFold", etc. | Folding |
| `FoldDirection` | "Inside" / "Outside" | Fold direction |
| `Crease` | "Off", "On" | Creasing |

### Image Position
| Feature | Values | Description |
|---------|--------|-------------|
| `HorizontalShift` | integer (µm) | X shift |
| `VerticalShift` | integer (µm) | Y shift |
| `HorizontalShiftBack` | integer (µm) | Back side X shift |
| `VerticalShiftBack` | integer (µm) | Back side Y shift |
| `ImageShiftType` | "SeparateFrontBack" | Shift mode |
| `ScaleToFit` | "True" / "False" | Scale to fit |
| `Zoom` | 100 | Zoom percentage |
| `PrintPosition` | "Middle" | Position on page |

### Advanced
| Feature | Values | Description |
|---------|--------|-------------|
| `Resolution` | "1200dpi" | Print resolution |
| `PrintQuality` | "Normal" | Quality setting |
| `Enhancement` | "True" / "False" | Edge enhancement |
| `Thinning` | "True" / "False" | Thinning |
| `UseCieColor` | "On" / "Off" | CIE color matching |
| `ForceRip` | "True" / "False" | Force re-RIP |
| `OutputMethod` | "Print" | Output method |
| `PrintMode` | "Print" | Print mode |

---

## Container/Queue System

```
GET /containerList.fcgi?sessionId={sid}&viewId=0&ts={ts}
```

### Standard Containers

| Container | containerId | Type | Description |
|-----------|-------------|------|-------------|
| Active | 268435440 | active | Currently printing jobs |
| Hold | 268435441 | hold | Jobs waiting to be printed |
| HDD | 268369922 | hdd | Stored on hard drive (has sub-folders) |
| Secure | 268435443 | secure | Password-protected jobs |
| History | 268435444 | finished | Completed jobs (max 200) |
| Editable Active | 268435445 | activeHold | Active jobs that can be edited |

### HDD Sub-Structure (on this device)
```
HDD (268369922)
└── Public (268369938)
    └── izdavam (65554) - 44 jobs stored
```

### Storage Info
- Copy/RIPed Data: 324 GB of 590 GB Free
- Pre-RIP Data/Scan/Form: 153 GB of 166 GB Free

---

## Device Information

```
GET /deviceInfo.fcgi?sessionId={sid}&viewId=0&ts={ts}
```

### Key Device Info
```json
{
  "printerInformation": {
    "deviceName": "KONICA MINOLTA AccurioPrint 2100",
    "printerName": "2100",
    "macAddress": "00:50:AA:2C:DA:08",
    "ipV4Address": "192.168.1.131",
    "administratorMode": false,
    "hotFolderEnabled": true
  },
  "toner": [{"name": "black", "level": "ready", "amount": 90}],
  "inputTrays": [
    {"trayId": "Tray1", "TargetPaperSize": "A3", "paperAmount": 2,
     "MainPaperProfileName": "Offset 80 420x297 TEST", "FeedDir": "ShortEdge"},
    {"trayId": "Tray2", "TargetPaperSize": "A4", "paperAmount": 5,
     "MainPaperProfileName": "novo Offset120grA4 210x297", "FeedDir": "LongEdge"}
  ]
}
```

### Production Status (polling endpoint)

```
GET /productionData.fcgi?sessionId={sid}&viewId=0&ts={ts}
```

Returns current printing status:
```json
{
  "jobId": 22604,
  "jobName": "10660A3 Milen.pdf",
  "printedCopies": 0,
  "printedPages": 202,
  "totalCopies": 3,
  "totalPages": 202,
  "productionStatus": "printing"
}
```

Returns `{}` when no job is printing.

---

## The .icjx File Format

### Overview

The `.icjx` file is a **Konica Minolta AccurioPro Print Manager proprietary format**. It is created by the "Export" function and can be re-imported via "Upload / Import Job".

### File Structure

```
[outer tar archive]
├── ./                              (directory entry)
└── ./1 {filename}.pdf              (main content file - NOT a raw PDF)
    ├── [41KB binary header]        (job metadata, settings references)
    │   ├── Bytes 0-3: 0xFFFFFFFF  (signature)
    │   ├── Job name (repeated 3x)
    │   ├── "_SAMEASIMAGE" string
    │   ├── IP address of source printer (e.g., "192.168.1.238")
    │   └── Various binary settings
    ├── [gzip-compressed tar]       (at offset ~41056, starts with 0x1F8B)
    │   ├── {jobid}.pre             (THE ACTUAL PDF FILE - %PDF-1.4)
    │   ├── EngPage000.dbm          (engine/page settings - binary)
    │   ├── bppage000.dbm           (box print page settings - binary, contains paths like /km/doc/boxprint/box/-1/{id}/{id}.pre)
    │   ├── Adjustment/             (empty directory)
    │   ├── ToneCurve/              (empty directory)
    │   ├── data/                   (empty directory)
    │   └── thumb/                  (thumbnail images)
    │       ├── 1.thm              (page 1 thumbnail)
    │       ├── 2.thm              (page 2 thumbnail)
    │       └── ...
```

### Extracting the PDF from .icjx

```python
import tarfile, zlib, io

# Step 1: Extract outer tar
with tarfile.open("file.icjx") as tar:
    inner_file = tar.extractfile(tar.getmembers()[1])  # Skip "./" entry
    data = inner_file.read()

# Step 2: Find gzip stream (starts at ~offset 41056)
gzip_offset = data.find(b'\x1f\x8b')

# Step 3: Decompress
decompressed = zlib.decompress(data[gzip_offset + 10:], -15)

# Step 4: Extract inner tar
inner_tar = tarfile.open(fileobj=io.BytesIO(decompressed))
for member in inner_tar.getmembers():
    if member.name.endswith('.pre'):
        pdf_data = inner_tar.extractfile(member).read()
        # This is the actual PDF!
        with open("extracted.pdf", "wb") as f:
            f.write(pdf_data)
```

### Key Observations

- The `.pre` file inside IS a standard PDF (starts with `%PDF-1.4`)
- The `.dbm` files contain binary print settings (proprietary format)
- The binary header (first 41KB) contains the job name, source printer IP, and references to settings
- Thumbnails are stored as `.thm` files (one per page)

---

## Known Issues & Gaps

### setJobDetailsAndUnlock.fcgi - Works from Browser Only

**Status**: Works from browser JavaScript (`fcgiSrv.post`), but fails from Python's `http.client`.

**From Python http.client**: Returns `AioJobNoExists` or `InternalError`.

**From browser**: Successfully prints jobs. Confirmed working with jobs 100022612, 100022626, 100022633.

**Not needed for basic printing**: Use `jobPrintAndUnlock.fcgi` instead (see above), which works from both curl and Python.

**Only needed when**: You want to modify print settings (printFeatures) before printing — e.g., changing duplex, paper size, image shift, etc. For .icjx files, settings are already embedded, so `jobPrintAndUnlock.fcgi` is sufficient.

### Python http.client vs curl — AioJobInUse Issue

**Problem**: `jobPrintAndUnlock.fcgi` returns `AioJobInUse` when called via Python's `http.client`, even after a successful lock with the same session. The identical request works via curl.

**Workaround**: The `auto_print.py` script uses `subprocess` to call curl directly, which reliably works. This avoids the HTTP-level incompatibility between Python's `http.client` and the ProfiWEB server.

### jobPrintAndUnlock.fcgi — CONFIRMED WORKING

Previously returned `InvalidParameter: isLocked` because the required parameters were not all included. The full parameter set is:

```
POST /jobPrintAndUnlock.fcgi
Content-Type: application/x-www-form-urlencoded

jobId={id}&containerId={cid}&printMode=Print&deleteJob=true&numOfCopies=1&isLocked=true&ts={timestamp}&sessionId={URL-encoded sessionId}&viewId=0
```

**Required parameters:**
- `jobId` — the job ID
- `containerId` — container where the job lives (268435441 = Hold)
- `printMode` — `Print` (or other modes)
- `deleteJob` — `true` to delete after printing, `false` to keep
- `numOfCopies` — number of copies (overrides job setting)
- `isLocked` — must be `true` (job must be locked before calling)
- `sessionId`, `viewId`, `ts` — standard session params

**Important**: The job MUST be locked first via `jobLock.fcgi` with `action=lock`.

---

## Curl Examples

### Complete Upload-to-Hold Workflow

```bash
# 1. Register session
SESSION=$(curl -s "http://192.168.1.131:30083/register.fcgi?sessionId=-1&viewId=-1&ts=$(date +%s)000" | python3 -c "import sys,json; print(json.load(sys.stdin)['sessionId'])")

# 2. Login as Operator
curl -s -X POST "http://192.168.1.131:30083/sessionLogin.fcgi" \
  -d "notauthuser=Operator&sessionId=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SESSION'))")&viewId=0&ts=$(date +%s)000"

# 3. Upload PDF to Hold queue
curl -s -X POST "http://192.168.1.131:30083/jobSubmit.fcgi" \
  -F "file=@/path/to/document.pdf;filename=document.pdf" \
  --form-string "sessionId=$SESSION" \
  -F "viewId=0" \
  -F "containerId=268435441" \
  -F "hold=true"

# 4. List jobs in Hold queue
curl -s "http://192.168.1.131:30083/jobList.fcgi?containerId=268435441&viewId=0"

# 5. Get device status
curl -s "http://192.168.1.131:30083/deviceInfo.fcgi?viewId=0"

# 6. Check current print production
curl -s "http://192.168.1.131:30083/productionData.fcgi?viewId=0"
```

### Lock, Get Details, Unlock

```bash
JOB_ID=20750
CID=268435441

# Lock
curl -s -X POST "http://192.168.1.131:30083/jobLock.fcgi" \
  -d "action=lock&jobId=$JOB_ID&containerId=$CID&viewId=0"

# Get details
curl -s "http://192.168.1.131:30083/jobDetails.fcgi?jobId=$JOB_ID&containerId=$CID&viewId=0"

# Unlock
curl -s -X POST "http://192.168.1.131:30083/jobLock.fcgi" \
  -d "action=unlock&jobId=$JOB_ID&containerId=$CID&viewId=0"
```

### Delete a Job

```bash
curl -s -X POST "http://192.168.1.131:30083/jobDelete.fcgi" \
  -d "jobId=100022612&containerId=268435441&viewId=0"
```

---

## Appendix: Paper Profiles on This Device

| Index | Name | Tray |
|-------|------|------|
| 11 | Offset 80 420x297 TEST | Tray1 (A3) |
| 15 | novo Offset120grA4 210x297 | Tray2 (A4) |

## Appendix: Passwords

| Model | Admin Password |
|-------|---------------|
| 2100, 754e | 12345678 |
| C654, 759 | 1234567812345678 |

---

---

## IPP Printing (CONFIRMED WORKING - RECOMMENDED APPROACH)

The printer exposes a standard IPP (Internet Printing Protocol) endpoint that supports direct PDF printing. **This is the simplest and most reliable way to print.**

### IPP Endpoint

```
ipp://192.168.1.131:631/ipp
```

### Supported Formats
- `application/pdf`
- `application/postscript`
- `application/vnd.hp-PCL`
- `text/plain`
- `text/html`
- `application/octet-stream`

### Supported IPP Operations
- `Print-Job` - Submit and print a file
- `Validate-Job` - Validate without printing
- `Cancel-Job` - Cancel a job
- `Get-Job-Attributes` - Get job info
- `Get-Jobs` - List jobs
- `Get-Printer-Attributes` - Get printer info

### IPP Print Settings
| Setting | Values |
|---------|--------|
| `sides` | `one-sided`, `two-sided-long-edge`, `two-sided-short-edge` |
| `copies` | 1-N (default: 1) |
| `number-up` | 1, 2, 4, 6, 9, 16 |
| `finishings` | `none`, `staple`, `punch`, `cover` |

### Print via lp command

```bash
# Basic print
lp -h 192.168.1.131:631 -d ipp /path/to/document.pdf

# With settings
lp -h 192.168.1.131:631 -d ipp \
  -n 3 \                          # 3 copies
  -o sides=two-sided-long-edge \  # duplex
  /path/to/document.pdf
```

### Print via ipptool

```bash
ipptool -f /path/to/document.pdf ipp://192.168.1.131:631/ipp print-job.test
```

### Print via curl (raw IPP)

```bash
# IPP uses a binary protocol. For raw IPP, use ipptool or a library.
# Python example with python-ipp or pycups is recommended.
```

### Printer Status via IPP
```
printer-state = stopped (currently, due to media-jam-error)
printer-state-reasons = media-jam-error, media-empty-warning, media-low-warning
printer-is-accepting-jobs = true
```

### Other Open Ports
| Port | Protocol | Status |
|------|----------|--------|
| 631 | IPP | OPEN - Printer |
| 515 | LPR | OPEN |
| 9100 | RAW/JetDirect | OPEN |
| 445 | SMB | OPEN (needs auth) |
| 139 | NetBIOS | OPEN |
| 21 | FTP | OPEN (needs auth) |
| 30083 | HTTP/ProfiWEB | OPEN |

---

## Hot Folders (Auto-Print)

The device has a hot folder configured that can auto-print files placed in it.

### Hot Folder Configuration

```
GET /hotFolderList.fcgi?viewId=0
```

**Current hot folder:**
```json
{
  "hotFolderId": 1,
  "name": "print",
  "authentication": "GUEST",
  "status": "unedited",
  "printMode": "Print",
  "outputMethod": "Print",
  "printSettingPriority": "hotFolder",
  "enabled": true,
  "deletePrintedFile": true
}
```

- `printMode: "Print"` - Files are printed automatically
- `deletePrintedFile: true` - Files are deleted after printing
- `printSettingPriority: "hotFolder"` - Hot folder settings override the file's settings
- `authentication: "GUEST"` - No authentication required

### Hot Folder Print Settings

The hot folder has its own set of printFeatures (same format as job printFeatures). Key defaults:
- `Duplex: "True"` - Two-sided
- `NumCopies: 1` - Single copy
- `PageSize: "A4"` - A4 paper
- `InputSlot: "Auto"` - Auto tray select
- `FullBleed: "True"` - Full bleed
- `Resolution: "1200dpi"` - Max resolution

### Accessing the Hot Folder

The hot folder is typically accessible via SMB share (port 445). The share name is usually the hot folder name ("print"). SMB access requires authentication which needs to be configured on the printer's admin interface.

**To investigate**: Check the printer's WCD admin interface for SMB/FTP credentials, or configure them.

---

## Recommended Auto-Print Strategy

### Option 1: Import .icjx via jobRestore + Print (RECOMMENDED FOR .icjx) ✅ FULLY AUTOMATED

**Best for batch printing .icjx files with their embedded settings preserved.**

```bash
python3 auto_print.py *.icjx                    # Print all .icjx files
python3 auto_print.py --copies 3 order.icjx     # 3 copies
python3 auto_print.py --no-delete order.icjx    # Keep in queue after printing
```

Flow:
1. Register session + login via curl
2. Import .icjx via `jobRestore.fcgi` (preserves ALL embedded settings)
3. Find imported jobId via `jobList.fcgi`
4. Lock job via `jobLock.fcgi`
5. Print via `jobPrintAndUnlock.fcgi` (with delete option)

**Pros**: Preserves ALL .icjx print settings (duplex, paper profile, image shift, booklet, etc.), fully automated, no browser needed
**Cons**: Cannot modify settings before printing (uses settings from .icjx as-is)

### Option 2: IPP Print (Simplest — For PDFs)

1. Extract PDF from `.icjx` file (Python script — `auto_print.py`)
2. Read print settings from the `.icjx` metadata
3. Send via IPP with settings: `lp -h 192.168.1.131:631 -d ipp -o sides=two-sided-long-edge file.pdf`

**Pros**: Standard protocol, works with any OS, simple command, no browser needed
**Cons**: Limited IPP settings (no paper profile, no image shift, no booklet layout, copies limited to 1)

### Option 3: Hot Folder via SMB/FTP

1. Configure SMB/FTP credentials on the printer
2. Drop PDF file into the hot folder share
3. Printer auto-prints with hot folder default settings

**Pros**: Fully automatic, no API calls needed
**Cons**: Need to set up credentials, limited to hot folder's fixed settings

### Option 4: Direct Socket Print (Port 9100)

1. Send raw PDF or PostScript to port 9100
2. `cat file.pdf | nc 192.168.1.131 9100`

**Pros**: Simplest possible, no authentication
**Cons**: No control over print settings, uses printer defaults

---

## Per-Job Tray Selection — The Real Story (added 2026-05-26)

### Problem

We need to force a specific paper tray on a per-job basis (e.g., MBT for 300g cards) without an operator manually setting the panel defaults. Everything in this section was investigated against the **AccurioPrint C4065 / IC-607** at `192.168.1.250` while building the nima.bg print poller.

### Option A — `setJobDetailsAndUnlock.fcgi` is harder than the doc above suggests

The earlier "browser-only" note is correct but incomplete. The real obstacle:

- The SPA does **not** send the response of `jobDetails.fcgi` back to the server. It sends the output of `job.getRipDataObject()`, which is a **writable subset** computed by the job model.
- A live `jobDetails.fcgi` reply for one job contained **449 printFeatures**, most of which are read-only / device-state. Sending them back verbatim returns `InternalError`.
- `applySendHacks(e)` (the `B(...)` function the bundle references) is **almost a no-op** — it only rewrites `printFeatures.PerfectBindPaperSize: "Custom"` → `"CustomSize"`. The heavy lifting is in `getRipDataObject()` / `getRipPrintFeatures()` which filter the data.
- Empirically confirmed: calling `fcgiSrv.post("/setJobDetailsAndUnlock.fcgi", {params: {jobId, containerId, jobData: JSON.stringify(d)}})` *from inside the SPA's own session* — where `d` is the unfiltered `jobDetails.fcgi` response wrapped in the `{printFeatures, pageSettings, …}` envelope — still returns `InternalError`.

So to drive `setJobDetailsAndUnlock` from a script you would need one of:

1. **Capture an actual successful save's body** from a live SPA save (post a UI change → click Save) and replay it. Brittle: the writable subset changes with firmware, and the SPA computes it from per-job state.
2. **Re-implement the bundle's `getRipPrintFeatures()` / `getRipDataObject()` logic in your script.** Means tracking ~30-50 writable PrintFeature fields and their constraints. Maintainable but a few weeks of work.
3. **Walk AngularJS scopes to find the live job model and call its method.** Requires a real headless browser session. Heavy.

### Option B — Use CUPS + Konica PostScript driver (CONFIRMED WORKING ✅ 2026-05-26)

This sidesteps `setJobDetailsAndUnlock` entirely. The Konica AccurioPress C4080 PostScript driver writes the same job ticket *inside* the PostScript stream as `SHKM*` directives, and the IC-607 RIP honors them when the PS is dropped onto `socket://<printer>:9100`.

#### What we verified

- **Test print on C4065 → MBT pulled correctly with `KOMediaWeight=Thick8` (300g class).** Printer stopped asking for the 300g paper instead of silently substituting 80g (which was the previous symptom).
- **CUPS-submitted job lands in the ProfiWEB Hold queue with the right job ticket** — `jobDetails.fcgi` afterwards shows `printFeatures.InputSlot = "MBT"`, `MainPaperProfileIndex = 22` (the "300 mat A4 legnal" profile). So the CUPS path is equivalent to a properly-set-up `setJobDetailsAndUnlock` call, just achieved differently.

#### Driver download

- **Title on KM site**: `IC-609 PS Driver for Mac OS X` (e.g., `IC609PSMACOS_60603MU.dmg`, ~30 MB)
- The `.dmg` contains `KONICA MINOLTA C4080Series PS.pkg`. Inside `Driver.pkg/Scripts/Package.zip` you'll find:
  - PPD: `Library/Printers/PPDs/Contents/Resources/en.lproj/KOIC4080_.ppd` (~720 KB)
  - CUPS filter: `Library/Printers/KONICA_MINOLTA/Filters/10.8/pstoKOIC4080` (Mach-O x86_64+i386, runs under Rosetta on Apple Silicon)
  - PDE plugin: `Library/Printers/KONICA_MINOLTA/PDEs/10.8/KOIC4080.plugin` (only needed for the GUI print dialog; not required for `lp -o ...`)

**Critical**: this driver bundle is labelled for the **IC-609** controller, but the PPD's `*Product` line is:
```
*Product: "(KONICA MINOLTA C4080/C4070/C4065)"
```
…so it covers all three models. Confirmed: **works against the C4065's IC-607** despite the controller-naming mismatch.

#### Manual install (bypassing the GUI installer)

```bash
# After expanding the .pkg and unzipping Package.zip:
sudo mkdir -p /Library/Printers/KONICA_MINOLTA/Filters /Library/Printers/KONICA_MINOLTA/PDEs
sudo cp pstoKOIC4080 /Library/Printers/KONICA_MINOLTA/Filters/
sudo chmod 755 /Library/Printers/KONICA_MINOLTA/Filters/pstoKOIC4080
sudo cp -R KOIC4080.plugin /Library/Printers/KONICA_MINOLTA/PDEs/
sudo cp KOIC4080_.ppd /Library/Printers/PPDs/Contents/Resources/
sudo chown -R root:wheel /Library/Printers/KONICA_MINOLTA /Library/Printers/PPDs/Contents/Resources/KOIC4080_.ppd

sudo lpadmin -p NimaC4065 -E \
  -v socket://192.168.1.250:9100 \
  -P /Library/Printers/PPDs/Contents/Resources/KOIC4080_.ppd \
  -o printer-is-shared=false
```

The CUPS filter has no arm64 slice, so on Apple Silicon Macs **Rosetta 2 must be installed** (`oahd` running). Verified on macOS 26.3.1 / arm64.

#### Per-job options (PPD-level, drive via `lp -o`)

| Option | Values | Notes |
|---|---|---|
| `InputSlot` | `Tray1`…`Tray11`, `MBT` | Forces a specific tray. Names match what `deviceInfo.fcgi` returns as `inputTrays[i].trayId`. |
| `KOMediaWeight` | `NoSet`, `Normal` (62-74), `Thick` (75-80), `Thick2` (81-91), `Thick3` (92-105), `Thick4` (106-135), `Thick5` (136-176), `Thick6` (177-216), `Thick7` (217-256), `Thick8` (257-300), `Thick9` (301-350), `Thick10` (351-360) | Sets the media-weight job attribute. |
| `KOTargetPaperSize` | `A3`, `A4`, `A5`, `A6`, `SRA3`, `SRA4`, `KMB4`, `KMB5`, `KMTabloid`, `9x11`, `Legal`, `Letter`, custom… | Output paper size. |
| `KOMediaType` | `NoSet`, `Plain`, `Color`, `Fine`, `Envelope`, `Embossed`, `CoatedG`, `CoatedM` | Media type. |
| `KODuplex` | `True`, `False` | 2-sided. |
| `KOLayout` | `None`, `AdhBinding`, `Booklet`, `2in1`, `4in1Horizontal`, … | Imposition. |
| `KOOutputOrder` | `FaceDown`, `FaceUp` | Face up/down. |
| `KOCollate` | `Sort`, `Group` | Sorting mode. |

Plus standard CUPS options: `-n <copies>`, `-o media=A4`, etc.

#### Example commands

```bash
# 300g A4 on the bypass tray, simplex, 1 copy
lp -d NimaC4065 -n 1 \
   -o InputSlot=MBT \
   -o KOMediaWeight=Thick8 \
   -o KOTargetPaperSize=A4 \
   -o KODuplex=False \
   file.pdf

# Dry-run via cupsfilter to inspect the PostScript output (without printing)
cupsfilter -p /Library/Printers/PPDs/Contents/Resources/KOIC4080_.ppd \
   -m application/vnd.cups-postscript \
   -o "InputSlot=MBT" -o "KOMediaWeight=Thick8" -o "KOTargetPaperSize=A4" \
   file.pdf > /tmp/out.ps

# Check SHKM directives baked into the output
grep -aoE "SHKM[A-Za-z]+ [^ /]+|SHKMInputSlot/[A-Za-z0-9]+" /tmp/out.ps | sort -u
# Expected:
#   SHKMInputSlot/MBT put
#   SHKMMediaWeight/Thick8 put
#   SHKMDuplex false
#   SHKMCollate true
```

#### PostScript job-ticket format (what the filter emits)

The `pstoKOIC4080` filter emits standard PostScript with a setpagedevice-like prologue using a Konica-internal dictionary called `SHKMFeatures`. Each option becomes:

```postscript
SHKMFeatures dup/SHKMInputSlot/MBT put /Sofha_P20 get exec
SHKMFeatures dup/SHKMMediaWeight/Thick8 put /Sofha_P20 get exec
```

`Sofha` is the company that wrote the IC-607 controller firmware (Sofha GmbH; mentioned in the driver postflight script copyright). `Sofha_P20` is the dispatch handler in the printer's RIP that processes each feature/value pair. This is why **port 9100 raw PostScript works for tray selection** even though the IPP listener on port 631 doesn't — they're separate code paths inside the controller.

### IPP listener (port 631) — confirmed useless for per-job control

`Get-Printer-Attributes` against `ipp://192.168.1.250:631/ipp` returns:

```
printer-make-and-model = "KONICA MINOLTA AccurioPrint C4065 IC-607"
job-creation-attributes-supported = job-priority    ← ONLY job-priority
media-source-supported  → absent
media-col-supported     → absent
sides-supported         = one-sided                  ← no duplex either
finishings-supported    = none
```

So `lp -h 192.168.1.250:631 -d ipp -o media-source=tray3 …` won't work — the printer accepts `-o job-priority=N` and that's it. The earlier note ("IPP CONFIRMED WORKING - RECOMMENDED") only meant *plain PDF goes out and prints*, not that you can configure anything per-job through it.

### Quick-reference comparison

| Path | Tray control? | Where the magic lives | Scriptable? |
|---|---|---|---|
| `setJobDetailsAndUnlock.fcgi` | **Yes** | `jobData` JSON inside a held `jobLock` | **✅ — see "ProfiWEB-only per-job settings" below (2026-05-27 finding, supersedes earlier "no" claim)** |
| `jobSubmit.fcgi` + `jobPrintAndUnlock.fcgi` | No | Panel defaults at print time | ✅ but tray is whatever the panel says |
| IPP (port 631) | No | Printer ignores media-* attrs | ✅ but no setting control |
| `lp -d NimaC4065` (CUPS+PPD) | Yes | SHKM directives in the PostScript stream | ✅ but obsoleted by the ProfiWEB-only path |
| Raw PS to port 9100 with hand-written SHKM | Yes | Same as above, without CUPS | ✅ |

### Misc empirical notes

- **Hold-queue display ID == `jobId`**. The number you see in the UI (e.g. `7438`) IS the value to pass to `jobId=` *when querying from the SPA's logged-in session*. Jobs uploaded via `jobSubmit.fcgi` from a fresh curl session get a 100000000-offset jobId (e.g. `100007462`). Both forms work in `jobLock.fcgi` / `jobDetails.fcgi` / `setJobDetailsAndUnlock.fcgi` — use whichever you got back from `jobList.fcgi`.
- **`jobDetails.fcgi` returns 21 top-level keys** including `printFeatures` (449 entries on a C4065 job), `pageSettings`, `pageDetails`, `pageToneCurves`, `jobToneCurves`, `constraints`, `jobInfo`. Most are read-only, **but the server accepts the entire response back in `setJobDetailsAndUnlock.fcgi`'s `jobData=` parameter without complaint when the lock is held — see below.**
- **C4065 paper profiles**: `MainPaperProfileIndex: 22` corresponds to "300 mat A4 legnal" (the MBT profile). The full mapping is in `paperProfileList.fcgi`. The index is what the SPA writes when an operator picks a paper from the dropdown; the matching tray's `MainPaperProfileName` in `deviceInfo.fcgi` is the human-readable name.
- **Existing C754e/C759 in the shop have EFI Fiery E100 controllers** (advertised over Bonjour as `_ipp._tcp`), so they use Fiery PPDs. The **C4065 does not** — its IC-607 is Konica's own controller, hence the different CUPS driver lineage.

---

## ProfiWEB-only Per-Job Settings — The Working Recipe (added 2026-05-27)

**This supersedes both the "browser-only" claim earlier in this doc AND the CUPS+PPD workaround.** A 2026-05-27 investigation showed `setJobDetailsAndUnlock.fcgi` IS fully scriptable from curl/Python. The yesterday-and-prior failures were all the **same root cause**: the same session must hold a `jobLock.fcgi` lock on the job. With the lock held, the server accepts the raw `jobDetails.fcgi` response back as `jobData=` *unchanged*, mutating only the fields you care about.

### The recipe — 3 HTTP calls per print

```
POST /jobLock.fcgi                  action=lock&jobId=…&containerId=…
GET  /jobDetails.fcgi                jobId=…&containerId=…  → raw JSON, modify in-memory
POST /setJobDetailsAndUnlock.fcgi   jobId=…&containerId=…&jobData=<urlencoded JSON>&print=true&deleteJob=true
```

Optional: also `jobSubmit.fcgi` before the lock if you need to upload first, and `jobList.fcgi` to find the new `jobId`.

### What was wrong about the earlier "browser-only" claim

The earlier note said `setJobDetailsAndUnlock.fcgi` works from browser JS but fails from curl/Python with `AioJobNoExists` or `InternalError`. Today we proved:

- **Calling `fcgiSrv.post` from the browser console with the *raw* `jobDetails.fcgi` response also returned `InternalError`** when we didn't have the lock. So the failure was never about the payload shape or browser-specific magic — it was missing the lock.
- **Once `jobLock.fcgi` with `action=lock` returned successfully**, both the SPA's own filtered subset AND the raw `jobDetails.fcgi` payload worked. The error became `id: 77 "Print Manager is disconnected"` when the lock wasn't acquired in our session — generic enough that it had been misdiagnosed.
- **`applySendHacks(e)` (the `B(…)` function the bundle references)** is **a near-no-op**: it only renames `printFeatures.PerfectBindPaperSize: "Custom"` → `"CustomSize"`. The heavy lifting that earlier notes attributed to it doesn't exist. For 99% of jobs you can skip it.
- **`getRipDataObject()` / `getRipPrintFeatures()`** produces a different (smaller, partly-defaulted) payload than `jobDetails.fcgi`, but the server is fine with either. The SPA's filtering is a client-side concern, not a server-side requirement.

### URL-encoding gotcha (the one Python-specific snag)

`jobData` is a 25 KB JSON string with `:`, `,`, `&`, `=`, `"`, `{`, `}` characters. If you naively join `params` with `&` like `jobId=X&containerId=Y&jobData={...}` and `curl -d`, the server's form parser truncates `jobData` at the first `&` or `=` inside the JSON and reports `InvalidParameter: jobData is empty`. **Use `curl --data-urlencode key=value` for every parameter** so each value gets URL-encoded independently.

In Python:

```python
args = ['/usr/bin/curl', '-s', '-X', 'POST', url, '-H', 'Content-Type: application/x-www-form-urlencoded']
for k, v in params.items():
    args.extend(['--data-urlencode', f'{k}={v}'])
```

### Which printFeatures to set (cheat sheet)

For a typical "print A4 portrait on the tray loaded with weight X" use case:

| Field | Set to | Notes |
|---|---|---|
| `InputSlot` | `'MBT'`, `'Tray1'..'Tray11'` | The tray you want feeding |
| `MainPaperProfileIndex` | profile index from `paperProfileList.fcgi`, OR `0` for "no profile constraint" | Set to the tray's current profile index; the printer cross-checks the loaded paper |
| `TargetPaperSize` | `'A4'` / `'A3'` / `'A5'` / `'A6'` (or `'PaperProfile'` to defer to the profile's own size) | Sets the output size |
| `TargetPaperSize{InputSlot}` (e.g. `TargetPaperSizeMBT`) | same as `TargetPaperSize` | Per-tray override; the printer reads this when `InputSlot` matches |
| `Orientation` | `'Port'` / `'Land'` | Content orientation |
| `Rotate180` | `'False'` (or `'True'`) | Flip 180° |
| `MediaWeightAuto` | `'Thick'`, `'Thick2'`…`'Thick10'`, or `'NoSet'` | Weight class constraint; the printer halts if it disagrees |
| `MediaTypeAuto` | `'Plain'`, `'NoSet'`, etc. | Usually leave as `'NoSet'` |
| `NumCopies` | integer | Number of copies |
| `Duplex` | `'True'` / `'False'` | 2-sided |
| `FeedDirMBT` / `FeedDirTrayN` | `'Auto'` / `'LongEdge'` / `'ShortEdge'` | **The printer often overrides this with the tray's panel-stored setting**. If your portrait PDF prints landscape, the operator needs to physically reload the paper short-edge first OR change the tray's stored feed direction at the panel; the per-job override is unreliable. |

Weight classes from `*KOMediaWeight` in the PPD:

| Class | g/m² | Notes |
|---|---|---|
| Normal | 62-74 | |
| Thick | 75-80 | strict PPD range for 80g, but… |
| Thick2 | 81-91 | **the shop's "80g" profiles are actually Thick2** — match what's on the trays |
| Thick3 | 92-105 | |
| Thick4 | 106-135 | |
| Thick5 | 136-176 | 150g |
| Thick6 | 177-216 | |
| Thick7 | 217-256 | 250g |
| Thick8 | 257-300 | 300g |
| Thick9 | 301-350 | |
| Thick10 | 351-360 | |

### Tray-matching logic (what's actually safe)

When picking a tray for a job by weight + size:

- **Use `tray.TargetPaperSize`** (from `deviceInfo.fcgi`'s `inputTrays[]`) to match size — NOT the paper profile's `TargetPaperSize`. A profile can declare `NoSet` and still be assigned to a tray loaded with a specific size; trusting the profile's value alone matches wrong (a profile=NoSet on Tray2 loaded with A3 would incorrectly satisfy a request for A4).
- **Use `profile.MediaWeightAuto`** (looked up via the tray's `MainPaperProfileIndex` in `paperProfileList.fcgi`) to match weight. The tray itself doesn't carry weight info.
- **Require `paperAmount >= 5%`** to avoid sending jobs to empty/near-empty trays. The check is a polite guard; the printer will halt anyway if a tray is empty, but pre-flighting saves a wasted RIP cycle.
- **Skip trays with `MainPaperProfileIndex == 0`** (no profile assigned). Common when the operator changed paper but didn't pick a profile at the panel — we have no way to verify what's actually in there.

```python
# Find the loaded-and-matching tray
matches = []
for t in device_info['printerInformation']['inputTrays']:
    if t.get('paperAmount', 0) < 5:                    continue
    if t.get('TargetPaperSize') != target_size:        continue
    profile = profiles.get(t.get('MainPaperProfileIndex'))
    if not profile:                                    continue
    if profile.get('MediaWeightAuto') != target_thick: continue
    matches.append((t['paperAmount'], t['trayId'], t['MainPaperProfileIndex']))
matches.sort(reverse=True)   # prefer the tray with the most paper left
tray_id, profile_idx = (matches[0][1], matches[0][2]) if matches else (None, None)
```

### Production status polling for completion

After `setJobDetailsAndUnlock.fcgi` with `print=true&deleteJob=true`:

```python
while time.time() - start < timeout:
    pd = curl_get('productionData.fcgi')
    status = pd.get('productionStatus')
    if status in ('warningStopPrint', 'error', 'aborted', 'cancelled', 'failed'):
        # printer halted — paper jam, empty tray, operator-cancel at panel
        return {'success': False, 'error': f'printer stopped: {status}'}
    if not pd or not status:
        # productionData empty; cross-check the Hold queue
        if not any(j['jobId'] == job_id for j in curl_get('jobList.fcgi', containerId=hold)['jobLists'][0]['jobs']):
            return {'success': True, 'job_id': job_id}
    time.sleep(3)
```

Observed productionStatus sequence on a successful 1-page color print:
```
"printing" → "waitPrinting" → "printing" → "" (cleared, ~1-3s) → job gone from Hold
```

Total wallclock from `setJobDetailsAndUnlock` to "job gone from Hold" on a 1-page job: ~90-100s (most of it is the IC-607's RIP + paper-warmup).

### Why the previous CUPS+PPD path was abandoned (still works, but obsolete)

The CUPS+PPD approach (Konica AccurioPress C4080 PostScript PPD installed on macOS, queue → `socket://192.168.1.250:9100`) DOES work — the SHKM-tagged PostScript stream steers the IC-607 RIP correctly. But it has three real downsides vs. the ProfiWEB-only path:

1. **Two-codepath maintenance** — different RIP entry point, different color path. Two pipelines to validate.
2. **Apple deprecation warning** — `lpadmin: Printer drivers are deprecated and will stop working in a future version of CUPS.` Apple's official line. Classic PPD-based queues on macOS 26 still work but won't forever.
3. **No clean failure signal** — CUPS marks a job done as soon as bytes are transmitted. If the printer halts after (paper jam, empty tray), the poller reports `done` but no sheet came out. The ProfiWEB path's `productionData.fcgi` polling catches `warningStopPrint` cleanly.

Now that ProfiWEB-only works for per-job tray selection, the CUPS dependency was removed from kasa1 (2026-05-27).

### Practical end-to-end pseudocode

```python
def profiweb_print_with_tray(filepath, host, paper_size, paper_weight, duplex=False, orientation='Port', copies=1):
    sess = register_and_login(host)
    
    # 1) Find a tray with matching paper loaded (fail loud if none)
    info = curl_get('deviceInfo.fcgi')
    profs = {p['MainPaperProfileIndex']: p for p in curl_get('paperProfileList.fcgi')['paperProfileList']}
    tray_id, profile_idx = find_loaded_tray(info, profs, weight_to_thick(paper_weight), paper_size)
    if not tray_id:
        raise NoPaperLoaded(f'no tray has {paper_weight} {paper_size}')
    
    # 2) Upload
    curl_post_multipart('jobSubmit.fcgi', file=filepath, containerId=HOLD)
    job_id = find_new_job_id(HOLD)
    
    # 3) Lock + read + modify + save+print  ← the magic
    curl_post('jobLock.fcgi', action='lock', jobId=job_id, containerId=HOLD)
    raw = curl_get('jobDetails.fcgi', jobId=job_id, containerId=HOLD)
    raw['printFeatures'].update({
        'InputSlot': tray_id,
        'MainPaperProfileIndex': profile_idx,
        'TargetPaperSize': paper_size,
        f'TargetPaperSize{tray_id}': paper_size,
        'Orientation': orientation,
        'Rotate180': 'False',
        'MediaWeightAuto': weight_to_thick(paper_weight),
        'NumCopies': copies,
        'Duplex': 'True' if duplex else 'False',
    })
    curl_post('setJobDetailsAndUnlock.fcgi',  # MUST use --data-urlencode for each param
              jobId=job_id, containerId=HOLD,
              jobData=json.dumps(raw),
              print='true', deleteJob='true')
    
    # 4) Poll productionData until done or warningStopPrint
    return poll_until_done(job_id, HOLD)
```

Reference implementation: `auto_print.profiweb_print_v2()` and `_find_matching_tray()` in this folder (and on kasa1 at `~/print-watcher/auto_print.py`).

---

*Last updated: 2026-05-27 (v4 — setJobDetailsAndUnlock.fcgi confirmed scriptable when the same session holds the lock; CUPS path retired; URL-encoding requirement documented; production status polling pattern documented)*
*Generated from live API testing against AccurioPrint 2100 (192.168.1.131) and AccurioPrint C4065 (192.168.1.250)*
