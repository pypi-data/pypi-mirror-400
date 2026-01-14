# Text Only Scanner 📝🔍

`text_only_scanner` helps teams ensure only human-readable text files pass validation. It
scans files (or directories) and rejects anything editors would struggle to open or read —
including binary files, files containing many control characters, and printable-but-high-entropy
blobs (e.g., encoded/encrypted payloads). 🚫🔒

## Objective 🎯

Prevent non-human-readable files from slipping into pipelines or tests. The library flags
files that are likely binary, contain unusual control characters, or appear to be encoded
or encrypted text that isn't meant to be read directly. This keeps downstream tooling and
review processes clean and predictable. ✅

## Use Cases

- Detect accidental binary outputs in repositories and CI. 🧪
- Block files that hide encoded/encrypted content where plain text is expected. 🔐
- Serve as a pre-commit or CI gate to ensure only code are in the pipeline
, not access/secret keys or tokens or binary files. ⛔️➡️✅

## Usage

From Python:

```py
from text_only_scanner.detector import is_text_file, filter_text_files

print(is_text_file("somefile.txt"))

accepted, rejected = filter_text_files(["a.txt", "b.bin"])
print("accepted:", accepted)
print("rejected:", rejected)
```

Command-line (module):

```bash
python -m text_only_scanner.cli file1.txt file2.bin
# prints accepted files to stdout, rejected to stderr and exits non-zero if any rejected
```

Notes:

- The detector combines several heuristics: NUL bytes, control-character ratios, printable
 vs letter ratios, and Shannon entropy to identify suspicious files. It is conservative —
 intended to reduce false negatives while keeping false positives low. ⚖️

Recursive usage:

```bash
# Recurse into directories and check all files inside
python -m text_only_scanner.cli -r pass_folder fail_folder
```
