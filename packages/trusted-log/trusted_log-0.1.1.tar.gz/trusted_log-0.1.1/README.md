# Trusted Container Log

`trusted--log` provides transparency log-related APIs to complete behavioral recording throughout the entire lifecycle of Docker container images, including building, uploading, downloading, and deployment.

## Overview
The `TrustedLog` class provides methods for signing data lists and files with chain authentication support using the Sigstore library. It supports adding/updating signing content and resetting the sign list when needed. All signing operations are recorded in Sigstore's transparent log with unique log indices. The class requires proper Sigstore environment configuration and valid identity tokens for operation.

## Key Features

### Chain Authentication
- Immutable Chain Structure: Each entry is cryptographically linked to the previous one, creating an tamper-evident chain
- Sequence Integrity: Automatic sequence numbering and hash chaining ensure chronological order
- Chain Verification: Built-in methods to verify the integrity of the entire chain

### Flexible Entry Management
- Pending Entries: Add multiple entries before signing them as a batch
- File Signing: Direct file signing with automatic hash calculation and metadata inclusion
- Custom Data: Support for arbitrary data structures with optional metadata

### Backup and Recovery
- Chain Export/Import: Save and restore complete chain state
- Safe Recovery: Graceful handling of corrupted backup files
- State Persistence: Maintain chain continuity across application restarts

### Comprehensive Verification
- Sigstore Integration: Full compatibility with Sigstore verification workflows
- Policy-based Verification: Support for custom verification policies
- Detailed Reporting: Comprehensive verification results with error details

## API Documentation

### Quick start

```PYTHON
from trusted_log import TrustedLog
from sigstore.oidc import IdentityToken, Issuer

# Create identity token
issuer = Issuer.production()
identity_token = issuer.identity_token()

# Create TrustedLog instance
log = TrustedLog(identity_token=identity_token)

# Add entries and sign
log.add_entry({"action": "create_file", "filename": "test.txt"})
bundle = log.sign_pending_entries()
```

### Core Class: TrustedLog

The main transparent log class that provides chain authentication functionality.

#### Constructor

```PYTHON
TrustedLog(identity_token: Optional[IdentityToken] = None, chain_id: Optional[str] = None)
```

Parameters:

- `identity_token`: Sigstore identity token (optional)
- `chain_id`: Chain ID (optional, auto-generated if not provided)

#### Class methods

`from_backup_file`

```PYTHON
@classmethod
from_backup_file(cls, backup_file_path: str, identity_token: Optional[IdentityToken] = None) -> 'TrustedLog'
```

Construct a TrustedLog instance from a backup file.

Parameters:

- `backup_file_path`: Path to the backup file
- `identity_token`: Identity token (optional)

Returns:

- `TrustedLog`: Instance restored from backup file

Raises:

- `FileNotFoundError`: Backup file not found
- `ValueError`: Invalid backup file format

Example:

```PYTHON
from sigstore.oidc import Issuer

issuer = Issuer.production()
identity_token = issuer.identity_token()

# Restore from backup
log = TrustedLog.from_backup_file(
    backup_file_path="chain.sigstore.json",
    identity_token=identity_token
)
```

`from_backup_file_safe`

```PYTHON
@classmethod
from_backup_file_safe(cls, backup_file_path: str, identity_token: Optional[IdentityToken] = None) -> Optional['TrustedLog']
```

Safely construct an instance from a backup file, returning None on failure instead of raising exceptions.

Parameters:

- `backup_file_path`: Path to the backup file
- `identity_token`: Identity token (optional)

Returns:

- `TrustedLog` or `None`: Restored instance or None on failure

Example:

```PYTHON
log = TrustedLog.from_backup_file_safe("chain.sigstore.json")
if log is None:
    print("Failed to restore from backup")
```

#### Instance methods

`set_identity_token`

```PYTHON
set_identity_token(self, identity_token: IdentityToken) -> None
```

Set or update the identity token for the log.

Parameters:

- `identity_token`: The identity token to set

Raises:

- `ValueError`: If identity_token is `None`

`save_to_backup_file`

```PYTHON
save_to_backup_file(self, backup_file_path: str)
```

Save the current chain state to a backup file.

Parameters:

- `backup_file_path`: Path to the backup file

Example:

```PYTHON
log.save_to_backup_file("chain_backup.json")
```

`add_entry`

```PYTHON
add_entry(self, entry_data: dict) -> dict
```

Add entry to the pending signature list.

Parameters:

- `entry_data`: Entry data to be added

Returns:
- `dict`: Updated pending entries list

Example:

```PYTHON
log.add_entry({"action": "create_user", "user_id": "12345"})
log.add_entry({"action": "grant_permission", "permission": "read"})
```

`sign_pending_entries`

```PYTHON
sign_pending_entries(self) -> Bundle
```

Sign the pending entries list and submit to transparency log.

Returns:

- `Bundle`: A Sigstore bundle

Raises:

- `ValueError`: No pending entries to sign or identity token not set

Example:

```PYTHON
# Add entries
log.add_entry({"entry1": "data1"})
log.add_entry({"entry2": "data2"})

# Save pending entries to JSON file
with open("pending_entries.json", 'w', encoding='utf-8') as f:
    json.dump(log.pending_entries, f, ensure_ascii=False)

# Sign the entries
bundle = log.sign_pending_entries()

# Save the bundle
bundle_filename = "pending_entries.sigstore.json"
with open(bundle_filename, 'w', encoding='utf-8') as f:
    bundle_data = json.loads(bundle.to_json())
    json.dump(bundle_data, f, indent=2, ensure_ascii=False)

print(f"Log index: {bundle.log_entry.log_index}")
```

`sign_file`

```PYTHON
sign_file(self, file_path: str) -> Bundle
```

Sign the specified file and submit to transparency log.

Parameters:

- `file_path`: Path to the file to be signed

Returns:

- `Bundle`: A Sigstore bundle

Raises:

- `ValueError`: Identity token not set

Example:

```PYTHON
# Create a test file
with open("test.txt", "w") as f:
    f.write("test content")

# Sign the file
bundle = log.sign_file("test.txt")

# Save the bundle
bundle_filename = "test.txt.sigstore.json"
with open(bundle_filename, 'w', encoding='utf-8') as f:
    bundle_data = json.loads(bundle.to_json())
    json.dump(bundle_data, f, indent=2, ensure_ascii=False)

print(f"Log index: {bundle.log_entry.log_index}")
```

`sign_file_with_chain`

```PYTHON
sign_file_with_chain(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Bundle
```

Add file to the chain and sign it.

Parameters:

- `file_path`: Path to the file
- `metadata`: Optional metadata

Returns:

- `Bundle`: Sigstore bundle

`clear_pending_entries`

```PYTHON
clear_pending_entries(self)
```

Clear all pending entries from the signature list.

`verify_chain_integrity`

```PYTHON
verify_chain_integrity(self) -> bool
```

Verify chain integrity.

Returns:

- `bool`: Whether the chain integrity is valid

`verify_chain`

```PYTHON
verify_chain(self, sigstore_file_list: List, policy: VerificationPolicy) -> VerificationResult
```

Verify the entire chain using the provided Sigstore files and policy.

Parameters:

- `sigstore_file_list`: List of Sigstore files
- `policy`: Verification policy

Returns:

- `VerificationResult`: Verification result

Example:

```PYTHON
from sigstore.verify import policy
from pathlib import Path

# Create verification policy
my_policy = policy.Identity(
    identity="user@example.com",
    issuer="https://github.com/login/oauth",
)

# Get sigstore files
sigstore_files = list(Path(".").glob("entry*.sigstore.json"))

# Verify the chain
result = log.verify_chain(
    sigstore_file_list=sigstore_files,
    policy=my_policy,
)

if result.success:
    print(f"✓ Chain verification successful!")
    print(f"Verified entries: {result.verified_entries}/{result.total_entries}")
else:
    print("✗ Chain verification failed!")
    for error in result.errors:
        print(f"  - {error}")
```

`get_chain_summary`

```PYTHON
get_chain_summary(self) -> Dict[str, Any]
```

Get chain summary information.

Returns:

- `Dict[str, Any]`: Dictionary containing chain ID, total entries, current sequence, etc.

`get_verification_summary`

```PYTHON
get_verification_summary(self) -> Dict[str, Any]
```

Get summary information related to verification.

Returns:
- `Dict[str, Any]`: Verification summary information

`export_chain`

```PYTHON
export_chain(self) -> Dict[str, Any]
```

Export complete chain data.

Returns:
- `Dict[str, Any]`: Complete chain data

Example:

```PYTHON
chain_data = log.export_chain()
with open("chain.sigstore.json", "w") as f:
    json.dump(chain_data, f, indent=2)
```

`import_chain`

```PYTHON
import_chain(self, chain_data: Dict[str, Any])
```

Import chain data to continue an existing chain.

Parameters:

- `chain_data`: Chain data to import

#### Properties

`pending_entries`

```PYTHON
@property
pending_entries(self) -> dict
```

Get current pending entries.

`has_pending_entries`

```PYTHON
@property
has_pending_entries(self) -> bool
```

Check if there are any pending entries.

`chain_length`

```PYTHON
@property
chain_length(self) -> int
```

Get chain length.

`chain_id`

```PYTHON
@property
chain_id(self) -> str
```

Get chain ID.

### Data Classes

#### `ChainEntry`

Represents a single entry in the chain.

```PYTHON
@dataclass
class ChainEntry:
    sequence_number: int
    timestamp: str
    previous_hash: Optional[str]
    current_hash: str
    data: Dict[str, Any]
    signature_log_index: int
```

#### `VerificationResult`

Represents the result of chain verification.

```PYTHON
@dataclass
class VerificationResult:
    success: bool
    chain_id: str
    verified_entries: int
    total_entries: int
    errors: List[str]
    details: Dict[str, Any]
```

#### `SingleEntryVerificationResult`

Represents the result of single entry verification.

```PYTHON
@dataclass
class SingleEntryVerificationResult:
    success: bool
    errors: List[str]
    details: Dict[str, Any]
```

# Trouble shooting

1. `sigstore.oidc.IdentityError`
```txt
sigstore.oidc.IdentityError: Identity token is malformed or missing claims
```

Please check your server's date and time.

2. No attribute 'not_valid_after_utc'

```txt
AttributeError: 'cryptography.hazmat.bindings._rust.x509.Certificat' object has no attribute 'not_valid_after_utc'. Did you mean: 'not_valid_after'?
```

Please exec `pip install --upgrade sigstore cryptography`.
