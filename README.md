# Konica Minolta ProfiWEB Auto-Print

Automated batch printing for Konica Minolta printers running **AccurioPro ProfiWEB** (Print Manager). Import `.icjx` job files and print them with all embedded settings preserved — duplex, paper profile, image shift, booklet layout, and more.

Also supports direct PDF printing via IPP.

**Zero dependencies** — uses only Python 3 standard library + system `curl`.

## Supported Hardware

Tested on **AccurioPrint 2100** with ProfiWEB 1.0PW-4030. Should work with any Konica Minolta printer running AccurioPro Print Manager / ProfiWEB, including:

- AccurioPrint 2100
- AccurioPress C759 / C754e / C654e
- Other models with the ProfiWEB web interface (port 30083)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/bulgariamitko/profiweb-auto-print.git
cd profiweb-auto-print

# Print an .icjx file (imports via ProfiWEB, preserves all settings)
python3 auto_print.py --printer 10.0.0.50 order.icjx

# Batch print all .icjx files in a folder
python3 auto_print.py --printer 10.0.0.50 /path/to/orders/*.icjx

# Print a PDF directly via IPP
python3 auto_print.py --printer 10.0.0.50 document.pdf

# Preview what would happen (no actual printing)
python3 auto_print.py --printer 10.0.0.50 --dry-run *.icjx
```

## How It Works

### .icjx Files (ProfiWEB mode — default)

`.icjx` files are Konica Minolta's proprietary job export format. They contain a PDF plus all print settings (duplex, paper size, paper profile, image shift, N-up, finishing, etc.).

The script:
1. **Registers** a session with ProfiWEB (`register.fcgi`)
2. **Logs in** as Operator (`sessionLogin.fcgi`)
3. **Imports** the .icjx file via `jobRestore.fcgi` — this preserves ALL embedded settings
4. **Finds** the imported job in the Hold queue (`jobList.fcgi`)
5. **Locks** the job (`jobLock.fcgi`)
6. **Prints** and unlocks (`jobPrintAndUnlock.fcgi`)

### PDF Files (IPP mode — default)

PDFs are sent directly via the Internet Printing Protocol (IPP) on port 631. This is simpler but supports fewer settings (duplex, N-up, but no paper profiles or image shift).

## Usage

```
python3 auto_print.py [OPTIONS] FILE [FILE ...]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--printer IP` | Printer IP address (required) | — |
| `--mode {profiweb,ipp}` | Print mode | `profiweb` for .icjx, `ipp` for .pdf |
| `--copies N` | Number of copies (ProfiWEB mode) | `1` |
| `--no-delete` | Keep job in queue after printing (ProfiWEB) | Delete after print |
| `--duplex` | Force duplex printing (IPP mode) | Single-sided |
| `--profiweb-port PORT` | ProfiWEB port | `30083` |
| `--ipp-port PORT` | IPP port | `631` |
| `--dry-run` | Preview without printing | Off |

### Examples

```bash
# Print a single .icjx with all embedded settings
python3 auto_print.py --printer 10.0.0.50 order.icjx

# Print 3 copies
python3 auto_print.py --printer 10.0.0.50 --copies 3 order.icjx

# Keep job in queue after printing (don't delete)
python3 auto_print.py --printer 10.0.0.50 --no-delete order.icjx

# Batch print all .icjx files
python3 auto_print.py --printer 10.0.0.50 /path/to/folder/*.icjx

# Print PDF via IPP with duplex
python3 auto_print.py --printer 10.0.0.50 --duplex document.pdf

# Force PDF through ProfiWEB instead of IPP
python3 auto_print.py --printer 10.0.0.50 --mode profiweb document.pdf

# Dry run — see what would happen
python3 auto_print.py --printer 10.0.0.50 --dry-run *.icjx
```

## The .icjx File Format

`.icjx` is Konica Minolta's job export format created by the "Export" button in ProfiWEB. Structure:

```
[outer tar archive]
  └── ./1 {filename}.pdf          (NOT a raw PDF)
      ├── [~41KB binary header]   (job metadata, printer IP, settings refs)
      │   ├── Bytes 0-3: 0xFFFFFFFF (magic)
      │   ├── Job name (repeated)
      │   └── Source printer IP
      ├── [gzip stream]           (starts at ~offset 41056, magic: 0x1F8B)
      │   └── [inner tar]
      │       ├── {id}.pre        (THE ACTUAL PDF — starts with %PDF-)
      │       ├── EngPage000.dbm  (engine settings — binary)
      │       ├── bppage000.dbm   (box print settings — binary)
      │       ├── Adjustment/     (empty)
      │       ├── ToneCurve/      (empty)
      │       └── thumb/          (page thumbnails as .thm)
```

The script can also extract the PDF from .icjx files for IPP printing (use `--mode ipp`), though this loses the embedded print settings.

## ProfiWEB API Reference

See **[PROFIWEB_API_REFERENCE.md](PROFIWEB_API_REFERENCE.md)** for the complete API documentation, including:

- All 80+ `.fcgi` endpoints discovered from bundle.js analysis
- Authentication flow (register, login, admin)
- Job management (upload, import, lock, print, delete)
- Complete list of 216 print features (printFeatures)
- Container/queue system (Active, Hold, HDD, Secure, History)
- Device information and status polling
- Hot folder configuration
- IPP printing details
- Curl examples for every operation
- Known issues and workarounds

### Key API Endpoints

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `register.fcgi` | GET | Create a session |
| `sessionLogin.fcgi` | POST | Login as Operator (no password) |
| `checkAdminPwd.fcgi` | POST | Admin login (password required) |
| `jobSubmit.fcgi` | POST (multipart) | Upload PDF to queue |
| `jobRestore.fcgi` | POST (multipart) | Import .icjx file (preserves settings) |
| `jobList.fcgi` | GET | List jobs in a container |
| `jobDetails.fcgi` | GET | Get full job details + print settings |
| `jobLock.fcgi` | POST | Lock/unlock a job |
| `jobPrintAndUnlock.fcgi` | POST | Print a locked job |
| `setJobDetailsAndUnlock.fcgi` | POST | Modify settings and print |
| `jobDelete.fcgi` | POST | Delete a job |
| `deviceInfo.fcgi` | GET | Get printer status (trays, toner, etc.) |
| `productionData.fcgi` | GET | Get current print production status |
| `hotFolderList.fcgi` | GET | List hot folders |

### Quick curl Examples

```bash
# Register a session
curl -s "http://PRINTER:30083/register.fcgi?sessionId=-1&viewId=-1&ts=$(date +%s)000"
# Returns: {"sessionId": "abc123...", "viewId": 0}

# Login as Operator
curl -s -X POST "http://PRINTER:30083/sessionLogin.fcgi" \
  --data-urlencode "notauthuser=Operator" \
  --data-urlencode "sessionId=YOUR_SESSION" \
  -d "viewId=0&ts=$(date +%s)000"

# Import an .icjx file
curl -s -X POST "http://PRINTER:30083/jobRestore.fcgi" \
  -F "file=@job.icjx;type=application/octet-stream" \
  --form-string "sessionId=YOUR_SESSION" \
  -F "viewId=0"

# Upload a PDF to Hold queue
curl -s -X POST "http://PRINTER:30083/jobSubmit.fcgi" \
  -F "file=@document.pdf;filename=document.pdf" \
  --form-string "sessionId=YOUR_SESSION" \
  -F "viewId=0" -F "containerId=268435441" -F "hold=true"

# List jobs in Hold queue
curl -s "http://PRINTER:30083/jobList.fcgi?containerId=268435441&viewId=0"

# Lock a job
curl -s -X POST "http://PRINTER:30083/jobLock.fcgi" \
  -d "action=lock&jobId=JOB_ID&containerId=268435441&viewId=0&ts=$(date +%s)000" \
  --data-urlencode "sessionId=YOUR_SESSION"

# Print a locked job (and delete it after)
curl -s -X POST "http://PRINTER:30083/jobPrintAndUnlock.fcgi" \
  -d "jobId=JOB_ID&containerId=268435441&printMode=Print&deleteJob=true&numOfCopies=1&isLocked=true&viewId=0&ts=$(date +%s)000" \
  --data-urlencode "sessionId=YOUR_SESSION"

# Get printer status
curl -s "http://PRINTER:30083/deviceInfo.fcgi?viewId=0"

# Check what's currently printing
curl -s "http://PRINTER:30083/productionData.fcgi?viewId=0"
```

## Container IDs

ProfiWEB organizes jobs into containers (queues):

| Container | ID | Description |
|-----------|----|-------------|
| Active | 268435440 | Currently printing |
| Hold | 268435441 | Waiting to print |
| HDD | 268369922 | Stored on hard drive |
| Secure | 268435443 | Password-protected |
| History | 268435444 | Completed jobs |
| Editable Active | 268435445 | Active but editable |

## Print Settings (printFeatures)

When a job is imported via `.icjx`, all 216 print features are preserved. Key settings:

| Feature | Values | Description |
|---------|--------|-------------|
| `NumCopies` | 1-9999 | Number of copies |
| `Duplex` | `True` / `False` | Two-sided printing |
| `PageSize` | `A3`, `A4`, `A5`, etc. | Document size |
| `TargetPaperSize` | `Auto`, `A3`, `A4`, etc. | Output paper size |
| `InputSlot` | `Auto`, `Tray1`, `Tray2` | Paper tray |
| `Orientation` | `Port` / `Land` | Portrait/Landscape |
| `Layout` | `None`, `2up`, `4up` | N-up layout |
| `FullBleed` | `True` / `False` | Full bleed printing |
| `Fold` | `None`, `HalfFold`, etc. | Folding |
| `Staple` | `None`, etc. | Stapling |
| `Resolution` | `1200dpi` | Print resolution |
| `HorizontalShift` | integer (micrometers) | X image shift |
| `VerticalShift` | integer (micrometers) | Y image shift |
| `ScaleToFit` | `True` / `False` | Scale to fit |
| `Binding` | `Left`, `Right`, `Top` | Binding edge |

Full list of all 216 features available in `PROFIWEB_API_REFERENCE.md`.

## Alternative Printing Methods

| Method | Port | Settings Support | Complexity |
|--------|------|-----------------|------------|
| **ProfiWEB + .icjx** | 30083 | ALL settings preserved | Medium |
| **IPP** | 631 | Duplex, N-up, basic | Simple |
| **Hot Folder** | SMB/FTP | Hot folder defaults | Simple |
| **Raw/JetDirect** | 9100 | Printer defaults only | Simplest |
| **LPR** | 515 | Basic | Simple |

### IPP Printing

```bash
# Via lp command
lp -h PRINTER:631 -d ipp document.pdf

# With duplex
lp -h PRINTER:631 -d ipp -o sides=two-sided-long-edge document.pdf
```

### Raw Print (Port 9100)

```bash
cat document.pdf | nc PRINTER 9100
```

## Network Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 631 | IPP | Internet Printing Protocol |
| 515 | LPR | Line Printer Remote |
| 9100 | RAW | JetDirect direct printing |
| 445 | SMB | File sharing (hot folders) |
| 139 | NetBIOS | Name service |
| 21 | FTP | File transfer |
| 30083 | HTTP | ProfiWEB web interface |

## Known Issues

### Python http.client Incompatibility

Python's `http.client` has a subtle incompatibility with the ProfiWEB server — `jobPrintAndUnlock.fcgi` returns `AioJobInUse` even after a successful lock with the same session. The identical request works via `curl`. The `auto_print.py` script uses `subprocess` with `curl` as a workaround.

### setJobDetailsAndUnlock.fcgi

This endpoint (used to modify print settings before printing) only works from the browser's JavaScript context, not from curl or Python. For basic printing without modifying settings, use `jobPrintAndUnlock.fcgi` instead. If you need to modify settings programmatically, consider browser automation.

### Admin Passwords

Common default admin passwords by model:

| Model | Password |
|-------|----------|
| AccurioPrint 2100, C754e | `12345678` |
| C654e, C759 | `1234567812345678` |

## Requirements

- Python 3.6+
- `curl` (system command — preinstalled on macOS/Linux)
- Network access to the printer's ProfiWEB interface (port 30083)

## How This Was Discovered

The ProfiWEB API is undocumented. All endpoints were discovered by:

1. Analyzing the minified `bundle.js` (3.8MB AngularJS 1.8.2 app) served by ProfiWEB
2. Intercepting browser network requests via Chrome DevTools
3. Testing endpoints with curl to determine parameters and behavior
4. Examining the `fcgiSrv` AngularJS service that wraps all API calls

The `PROFIWEB_API_REFERENCE.md` documents everything found, including the 80+ endpoints, request formats, response structures, and container system.

## Contributing

Found additional endpoints or settings? PRs welcome. If you have a different Konica Minolta model, testing and reporting compatibility would be valuable.

## License

MIT
