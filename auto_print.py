#!/usr/bin/env python3
"""
Auto-Print Script for Konica Minolta AccurioPrint 2100
======================================================

Two printing modes:
  1. ProfiWEB API (default for .icjx) — imports via jobRestore.fcgi, preserves ALL settings
  2. IPP (default for .pdf) — direct printing via port 631

Usage:
  # Print .icjx files via ProfiWEB (preserves all embedded settings)
  python3 auto_print.py order.icjx
  python3 auto_print.py *.icjx

  # Print a PDF via IPP
  python3 auto_print.py document.pdf

  # Print PDF via ProfiWEB instead of IPP
  python3 auto_print.py --mode profiweb document.pdf

  # Print .icjx via IPP (extracts PDF, loses some settings)
  python3 auto_print.py --mode ipp order.icjx

  # Batch print a folder of .icjx files
  python3 auto_print.py /path/to/folder/*.icjx

  # Set copies (ProfiWEB mode)
  python3 auto_print.py --copies 3 order.icjx

  # Delete job after printing (ProfiWEB, default: true)
  python3 auto_print.py --no-delete order.icjx

  # Dry run
  python3 auto_print.py --dry-run *.icjx

  # Specify printer IP
  python3 auto_print.py --printer 192.168.1.131 document.pdf
"""

import argparse
import gzip
import http.client
import io
import json
import os
import struct
import subprocess
import sys
import tarfile
import time
import urllib.parse
import configparser


# ─── ProfiWEB API ─────────────────────────────────────────────────────────

class ProfiWebClient:
    """Client for the AccurioPro ProfiWEB API (.fcgi endpoints on port 30083)."""

    HOLD_CONTAINER = 268435441

    def __init__(self, host, port=30083):
        self.host = host
        self.port = port
        self.session_id = None
        self.view_id = 0

    def _curl(self, method, endpoint, params=None, multipart=None):
        """Execute HTTP request via curl and return parsed JSON."""
        url = f'http://{self.host}:{self.port}/{endpoint}'

        if method == 'GET':
            params = params or {}
            params['ts'] = str(int(time.time() * 1000))
            params['viewId'] = str(self.view_id)
            if self.session_id:
                params['sessionId'] = self.session_id
            qs = '&'.join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
            args = ['/usr/bin/curl', '-s', f'{url}?{qs}']
        elif multipart:
            args = multipart  # pre-built curl args
        else:
            # POST with form data
            params = params or {}
            params['ts'] = str(int(time.time() * 1000))
            params['viewId'] = str(self.view_id)
            args = ['/usr/bin/curl', '-s', '-X', 'POST', url,
                    '-H', 'Content-Type: application/x-www-form-urlencoded']
            # Build data: use -d for regular params, --data-urlencode for sessionId
            regular = '&'.join(f'{k}={v}' for k, v in params.items())
            args.extend(['-d', regular])
            if self.session_id:
                args.extend(['--data-urlencode', f'sessionId={self.session_id}'])

        result = subprocess.run(args, capture_output=True, text=True, timeout=120)
        return json.loads(result.stdout)

    def register(self):
        """Register a new session."""
        result = self._curl('GET', 'register.fcgi', {'sessionId': '-1', 'viewId': '-1'})
        self.session_id = result['sessionId']
        self.view_id = result['viewId']
        return result

    def login(self):
        """Login as Operator."""
        return self._curl('POST', 'sessionLogin.fcgi', {'notauthuser': 'Operator'})

    def import_icjx(self, filepath):
        """Import an .icjx file via jobRestore.fcgi. Returns True on success."""
        url = f'http://{self.host}:{self.port}/jobRestore.fcgi'
        args = ['/usr/bin/curl', '-s', '-X', 'POST', url,
                '-F', f'file=@{filepath};type=application/octet-stream',
                '--form-string', f'sessionId={self.session_id}',
                '-F', f'viewId={self.view_id}']
        result = self._curl(None, None, multipart=args)
        return result.get('result', {}).get('type') == 'ok'

    def upload_pdf(self, filepath):
        """Upload a PDF file via jobSubmit.fcgi to Hold queue. Returns True on success."""
        url = f'http://{self.host}:{self.port}/jobSubmit.fcgi'
        filename = os.path.basename(filepath)
        args = ['/usr/bin/curl', '-s', '-X', 'POST', url,
                '-F', f'file=@{filepath};filename={filename}',
                '--form-string', f'sessionId={self.session_id}',
                '-F', f'viewId={self.view_id}',
                '-F', f'containerId={self.HOLD_CONTAINER}',
                '-F', 'hold=true']
        result = self._curl(None, None, multipart=args)
        return result.get('result', {}).get('type') == 'ok'

    def list_jobs(self, container_id=None):
        """List jobs in a container."""
        cid = container_id or self.HOLD_CONTAINER
        result = self._curl('GET', 'jobList.fcgi', {'containerId': str(cid)})
        for jl in result.get('jobLists', []):
            if jl['containerId'] == cid:
                return jl.get('jobs', [])
        return []

    def lock_job(self, job_id, container_id=None):
        """Lock a job for editing/printing."""
        cid = container_id or self.HOLD_CONTAINER
        result = self._curl('POST', 'jobLock.fcgi', {
            'action': 'lock',
            'jobId': str(job_id),
            'containerId': str(cid)
        })
        ok = result.get('result', {}).get('type') == 'ok'
        if not ok:
            details = result.get('result', {}).get('details', [])
            errors = [d.get('id', '') for d in details]
            print(f"  Lock error: {errors}")
        return ok

    def print_and_unlock(self, job_id, container_id=None, copies=1, delete_after=True):
        """Print a locked job and unlock it."""
        cid = container_id or self.HOLD_CONTAINER
        result = self._curl('POST', 'jobPrintAndUnlock.fcgi', {
            'jobId': str(job_id),
            'containerId': str(cid),
            'printMode': 'Print',
            'deleteJob': 'true' if delete_after else 'false',
            'numOfCopies': str(copies),
            'isLocked': 'true'
        })
        ok = result.get('result', {}).get('type') == 'ok'
        if not ok:
            details = result.get('result', {}).get('details', [])
            errors = [d.get('id', '') for d in details]
            print(f"  Print error: {errors}")
        return ok

    def delete_job(self, job_id, container_id=None):
        """Delete a job."""
        cid = container_id or self.HOLD_CONTAINER
        result = self._curl('POST', 'jobDelete.fcgi', {
            'jobId': str(job_id),
            'containerId': str(cid)
        })
        return result.get('result', {}).get('type') == 'ok'


def profiweb_print(filepath, host, port=30083, copies=1, delete_after=True, dry_run=False):
    """
    Print a file via ProfiWEB API.
    - .icjx files: imported via jobRestore.fcgi (preserves all embedded settings)
    - .pdf files: uploaded via jobSubmit.fcgi

    Returns dict with success status.
    """
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        return {"success": False, "error": f"File not found: {filepath}"}

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ('.icjx', '.pdf'):
        return {"success": False, "error": f"Unsupported file type: {ext}. Use .pdf or .icjx"}

    client = ProfiWebClient(host, port)

    # Step 1: Register + Login
    print(f"  Connecting to ProfiWEB at {host}:{port}...")
    client.register()
    client.login()
    print(f"  Session established")

    # Step 2: Get current job list (to detect the new job after upload)
    jobs_before = {j['jobId'] for j in client.list_jobs()}

    # Step 3: Upload/Import
    if ext == '.icjx':
        print(f"  Importing .icjx via jobRestore.fcgi...")
        if dry_run:
            print(f"  [DRY RUN] Would import {filename}")
            return {"success": True, "dry_run": True}
        success = client.import_icjx(filepath)
    else:
        print(f"  Uploading PDF via jobSubmit.fcgi...")
        if dry_run:
            print(f"  [DRY RUN] Would upload {filename}")
            return {"success": True, "dry_run": True}
        success = client.upload_pdf(filepath)

    if not success:
        return {"success": False, "error": f"Failed to upload/import {filename}"}

    print(f"  Upload OK")

    # Step 4: Find the new job
    time.sleep(1)
    jobs_after = client.list_jobs()
    new_job = None
    for j in jobs_after:
        if j['jobId'] not in jobs_before:
            new_job = j
            break

    if not new_job:
        # Fall back: find by name match (latest unedited)
        for j in reversed(jobs_after):
            name_match = os.path.splitext(filename)[0] if ext == '.icjx' else filename
            if name_match.split('.')[0] in j.get('name', ''):
                new_job = j
                break

    if not new_job:
        return {"success": False, "error": "Could not find imported job in Hold queue"}

    job_id = new_job['jobId']
    job_name = new_job.get('name', filename)
    print(f"  Job found: ID={job_id}, name={job_name}, status={new_job.get('status')}, pages={new_job.get('pages')}")

    # Step 5: Lock
    print(f"  Locking job...")
    if not client.lock_job(job_id):
        return {"success": False, "error": f"Failed to lock job {job_id}"}

    # Step 6: Print
    print(f"  Printing ({copies} copies, delete_after={delete_after})...")
    if not client.print_and_unlock(job_id, copies=copies, delete_after=delete_after):
        return {"success": False, "error": f"Failed to print job {job_id}"}

    print(f"  SUCCESS! Job {job_id} sent to printer")
    return {"success": True, "job_id": job_id, "job_name": job_name}


# ─── IPP Protocol Helpers ──────────────────────────────────────────────────

def build_ipp_print_job(printer_uri, file_data, job_name,
                        document_format="application/pdf",
                        sides=None, number_up=None):
    """Build an IPP Print-Job request payload."""
    buf = bytearray()

    # IPP version 2.0, Operation Print-Job (0x0002), Request ID 1
    buf += struct.pack('>BBHI', 2, 0, 0x0002, 1)

    # Operation attributes group (0x01)
    buf.append(0x01)

    def add_str(tag, name, value):
        buf.extend(struct.pack('>BH', tag, len(name)))
        buf.extend(name.encode())
        val = value.encode() if isinstance(value, str) else value
        buf.extend(struct.pack('>H', len(val)))
        buf.extend(val)

    def add_int(name, value):
        buf.extend(struct.pack('>BH', 0x21, len(name)))
        buf.extend(name.encode())
        buf.extend(struct.pack('>HI', 4, value))

    add_str(0x47, 'attributes-charset', 'utf-8')
    add_str(0x48, 'attributes-natural-language', 'en')
    add_str(0x45, 'printer-uri', printer_uri)
    add_str(0x42, 'requesting-user-name', 'auto-print')
    add_str(0x42, 'job-name', job_name)
    add_str(0x49, 'document-format', document_format)

    # Job attributes group (0x02)
    has_job_attrs = sides or number_up
    if has_job_attrs:
        buf.append(0x02)
        if sides:
            add_str(0x44, 'sides', sides)
        if number_up:
            add_int('number-up', number_up)

    # End of attributes (0x03)
    buf.append(0x03)

    # Append document data
    buf.extend(file_data)
    return bytes(buf)


def parse_ipp_response(data):
    """Parse an IPP response into a dict."""
    if len(data) < 8:
        return {"success": False, "error": f"Response too small: {len(data)} bytes"}

    status = struct.unpack('>H', data[2:4])[0]
    result = {
        "success": status < 0x0100,
        "status_code": f"0x{status:04x}",
        "attributes": {}
    }

    i = 8
    while i < len(data):
        tag = data[i]; i += 1
        if tag == 0x03:
            break
        if tag in (0x01, 0x02, 0x04, 0x05):
            continue
        if i + 2 > len(data):
            break
        name_len = struct.unpack('>H', data[i:i+2])[0]; i += 2
        name = data[i:i+name_len].decode('utf-8', errors='replace'); i += name_len
        val_len = struct.unpack('>H', data[i:i+2])[0]; i += 2
        val_raw = data[i:i+val_len]; i += val_len

        if tag in (0x21, 0x23) and val_len == 4:
            val = struct.unpack('>i', val_raw)[0]
        else:
            val = val_raw.decode('utf-8', errors='replace')
        result["attributes"][name] = val

    return result


def send_ipp_print(host, port, path, payload, timeout=60):
    """Send IPP print job via HTTP POST."""
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    conn.request("POST", path, body=payload, headers={
        "Content-Type": "application/ipp",
        "Content-Length": str(len(payload))
    })
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return parse_ipp_response(data)


# ─── ICJX File Handling ────────────────────────────────────────────────────

def extract_icjx(icjx_path):
    """
    Extract PDF and print settings from an .icjx file.

    .icjx structure:
      Outer tar -> binary file with ~41KB header -> gzipped inner tar
      Inner tar contains:
        - *.pre  -> the actual PDF file
        - *.dbm  -> print settings (binary format)
        - thumb/ -> thumbnails

    Returns:
        (pdf_data: bytes, settings: dict)
    """
    print(f"  Extracting .icjx: {os.path.basename(icjx_path)}")

    with tarfile.open(icjx_path, 'r:') as outer_tar:
        members = outer_tar.getnames()
        binary_member = None
        for m in outer_tar.getmembers():
            if m.isfile() and m.size > 1000:
                binary_member = m
                break

        if not binary_member:
            raise ValueError(f"No binary content found in .icjx outer tar. Members: {members}")

        binary_data = outer_tar.extractfile(binary_member).read()

    gz_offset = -1
    for i in range(len(binary_data) - 1):
        if binary_data[i] == 0x1f and binary_data[i+1] == 0x8b:
            gz_offset = i
            break

    if gz_offset < 0:
        raise ValueError("Could not find gzip stream in .icjx binary")

    gz_data = binary_data[gz_offset:]
    decompressed = gzip.decompress(gz_data)

    pdf_data = None
    settings = {}

    with tarfile.open(fileobj=io.BytesIO(decompressed), mode='r:') as inner_tar:
        for member in inner_tar.getmembers():
            if not member.isfile():
                continue
            name = member.name.lower()

            if name.endswith('.pre'):
                pdf_data = inner_tar.extractfile(member).read()
                print(f"  Extracted PDF: {member.name} ({len(pdf_data)} bytes)")

            elif name.endswith('.dbm'):
                dbm_data = inner_tar.extractfile(member).read()
                try:
                    settings.update(parse_dbm_settings(dbm_data, member.name))
                except Exception as e:
                    print(f"  Warning: Could not parse {member.name}: {e}")

    if pdf_data is None:
        raise ValueError("No PDF (.pre) file found in .icjx inner tar")

    if not pdf_data[:5] == b'%PDF-':
        raise ValueError(f"Extracted .pre file is not a valid PDF (starts with {pdf_data[:20]})")

    return pdf_data, settings


def parse_dbm_settings(dbm_data, filename=""):
    """Parse .dbm settings file (INI-like format)."""
    settings = {}
    text = dbm_data.decode('utf-8', errors='replace')

    config = configparser.ConfigParser()
    try:
        config.read_string(text)
        for section in config.sections():
            for key, value in config.items(section):
                settings[f"{section}.{key}"] = value
    except configparser.Error:
        for line in text.split('\n'):
            line = line.strip()
            if '=' in line and not line.startswith('#') and not line.startswith('['):
                key, _, value = line.partition('=')
                settings[key.strip()] = value.strip()

    if settings:
        print(f"  Parsed settings from {filename}: {len(settings)} entries")

    return settings


def icjx_settings_to_ipp(settings):
    """Convert .icjx print settings to IPP attributes."""
    ipp_attrs = {}

    for key, value in settings.items():
        key_lower = key.lower()

        if 'duplex' in key_lower:
            if value in ('1', 'true', 'on', 'DuplexTumble'):
                ipp_attrs['sides'] = 'two-sided-short-edge'
            elif value in ('DuplexNoTumble',):
                ipp_attrs['sides'] = 'two-sided-long-edge'
            elif value not in ('0', 'false', 'off', 'None', 'SimplexFront'):
                if 'duplex' in value.lower() or 'two' in value.lower():
                    ipp_attrs['sides'] = 'two-sided-long-edge'

        if 'numcopies' in key_lower or 'copies' in key_lower:
            try:
                copies = int(value)
                if copies > 1:
                    ipp_attrs['copies'] = copies
            except ValueError:
                pass

        if 'numberup' in key_lower or 'nup' in key_lower:
            try:
                nup = int(value)
                if nup in (2, 4, 6, 9, 16):
                    ipp_attrs['number-up'] = nup
            except ValueError:
                pass

    return ipp_attrs


# ─── IPP Print Function ──────────────────────────────────────────────────

def ipp_print(filepath, printer_host="192.168.1.131", printer_port=631,
              printer_path="/ipp", duplex=False, dry_run=False):
    """Print a file via IPP. For .icjx, extracts PDF first."""
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        return {"success": False, "error": f"File not found: {filepath}"}

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    ipp_overrides = {}

    if ext == '.icjx':
        print(f"  Extracting PDF from .icjx for IPP printing...")
        pdf_data, settings = extract_icjx(filepath)
        job_name = filename
        ipp_overrides = icjx_settings_to_ipp(settings)
        if ipp_overrides:
            print(f"  Mapped settings to IPP: {ipp_overrides}")
    elif ext == '.pdf':
        with open(filepath, 'rb') as f:
            pdf_data = f.read()
        job_name = filename
    else:
        return {"success": False, "error": f"Unsupported file type: {ext}. Use .pdf or .icjx"}

    sides = None
    if duplex:
        sides = 'two-sided-long-edge'
    elif 'sides' in ipp_overrides:
        sides = ipp_overrides['sides']

    number_up = ipp_overrides.get('number-up')
    printer_uri = f"ipp://{printer_host}:{printer_port}{printer_path}"

    print(f"  PDF size: {len(pdf_data)} bytes")
    print(f"  Printer: {printer_uri}")
    print(f"  Sides: {sides or 'one-sided (default)'}")
    if number_up:
        print(f"  N-up: {number_up}")

    if dry_run:
        print("  [DRY RUN] Would send print job - not actually printing")
        return {"success": True, "dry_run": True, "job_name": job_name}

    payload = build_ipp_print_job(
        printer_uri=printer_uri,
        file_data=pdf_data,
        job_name=job_name,
        sides=sides,
        number_up=number_up
    )

    print(f"  Sending IPP Print-Job ({len(payload)} bytes)...")
    result = send_ipp_print(printer_host, printer_port, printer_path, payload)

    if result['success']:
        job_id = result['attributes'].get('job-id', 'unknown')
        job_state = result['attributes'].get('job-state', 'unknown')
        print(f"  SUCCESS! Job ID: {job_id}, State: {job_state}")
    else:
        print(f"  FAILED! Status: {result.get('status_code', 'unknown')}")
        for k, v in result.get('attributes', {}).items():
            print(f"    {k} = {v}")

    return result


# ─── CLI Interface ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Auto-print PDF and .icjx files to Konica Minolta AccurioPrint 2100",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  profiweb  Import .icjx via ProfiWEB API (preserves ALL print settings)
            Upload PDF via ProfiWEB API (to Hold queue, then print)
  ipp       Direct PDF printing via IPP port 631 (limited settings)

Default: .icjx files use 'profiweb', .pdf files use 'ipp'

Examples:
  %(prog)s order.icjx                      # Import + print .icjx (ProfiWEB)
  %(prog)s *.icjx                           # Batch print all .icjx files
  %(prog)s document.pdf                     # Print PDF via IPP
  %(prog)s --mode profiweb document.pdf    # Print PDF via ProfiWEB
  %(prog)s --copies 3 order.icjx           # 3 copies via ProfiWEB
  %(prog)s --no-delete order.icjx          # Keep job after printing
  %(prog)s --duplex document.pdf           # Duplex via IPP
  %(prog)s --dry-run *.icjx               # Preview what would be printed
  %(prog)s --printer 10.0.0.50 doc.pdf    # Use different printer IP
        """
    )
    parser.add_argument('files', nargs='+', help='PDF or .icjx files to print')
    parser.add_argument('--printer', default='192.168.1.131',
                        help='Printer IP address (default: 192.168.1.131)')
    parser.add_argument('--mode', choices=['profiweb', 'ipp'],
                        help='Print mode (default: profiweb for .icjx, ipp for .pdf)')
    parser.add_argument('--copies', type=int, default=1,
                        help='Number of copies (ProfiWEB mode, default: 1)')
    parser.add_argument('--no-delete', action='store_true',
                        help='Keep job in queue after printing (ProfiWEB mode)')
    parser.add_argument('--duplex', action='store_true',
                        help='Force duplex printing (IPP mode)')
    parser.add_argument('--profiweb-port', type=int, default=30083,
                        help='ProfiWEB port (default: 30083)')
    parser.add_argument('--ipp-port', type=int, default=631,
                        help='IPP port (default: 631)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be printed without sending')

    args = parser.parse_args()

    results = []
    for filepath in args.files:
        print(f"\n{'='*60}")
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        # Determine mode
        mode = args.mode
        if not mode:
            mode = 'profiweb' if ext == '.icjx' else 'ipp'

        print(f"File: {filename}")
        print(f"Mode: {mode}")

        if mode == 'profiweb':
            result = profiweb_print(
                filepath,
                host=args.printer,
                port=args.profiweb_port,
                copies=args.copies,
                delete_after=not args.no_delete,
                dry_run=args.dry_run
            )
        else:
            result = ipp_print(
                filepath,
                printer_host=args.printer,
                printer_port=args.ipp_port,
                duplex=args.duplex,
                dry_run=args.dry_run
            )

        results.append((filepath, result))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    success = sum(1 for _, r in results if r.get('success'))
    failed = len(results) - success
    print(f"  {success} succeeded, {failed} failed out of {len(results)} total")
    for filepath, result in results:
        status = "OK" if result.get('success') else "FAILED"
        extra = ""
        if result.get('dry_run'):
            extra = " [DRY RUN]"
        elif result.get('job_id'):
            extra = f" (job {result['job_id']})"
        elif result.get('attributes', {}).get('job-id'):
            extra = f" (IPP job {result['attributes']['job-id']})"
        if not result.get('success') and result.get('error'):
            extra = f" - {result['error']}"
        print(f"  [{status}] {os.path.basename(filepath)}{extra}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
