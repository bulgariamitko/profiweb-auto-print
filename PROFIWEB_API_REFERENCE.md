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

*Last updated: 2026-03-12 (v2 — added jobRestore.fcgi, jobPrintAndUnlock.fcgi, auto_print.py)*
*Generated from live API testing against AccurioPrint 2100 at 192.168.1.131:30083*
