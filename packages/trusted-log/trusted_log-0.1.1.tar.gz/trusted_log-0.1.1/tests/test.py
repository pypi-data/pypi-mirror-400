import json
import hashlib

from sigstore.oidc import Issuer
from sigstore.verify.verifier import Verifier
from sigstore.verify import policy
from sigstore.models import Bundle
from sigstore import hashes as sigstore_hashes
from trusted_log import TrustedLog
from pathlib import Path

TEST_FILE = "test.txt"
with open(TEST_FILE, "w") as f:
    f.write("test content")

_ASSETS = (Path(__file__).parent / "").resolve()
def asset(name: str) -> Path:
    return _ASSETS / name

def generate_file_digest(file_path: str) -> bytes:
    """Generate SHA-256 digest of the specified file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.digest()

def test_sign_file(chain_tlog: TrustedLog):
    print("Signing a file...")

    bundle = chain_tlog.sign_file(TEST_FILE)

    bundle_filename = f"{TEST_FILE}.sigstore.json"
    with open(bundle_filename, 'w', encoding='utf-8') as f:
        bundle_data = json.loads(bundle.to_json())
        json.dump(bundle_data, f, indent=2, ensure_ascii=False)
    print(f"Bundle saved to: {bundle_filename}")
    print(f"Signing a file completed.")
    print(f"https://search.sigstore.dev/?logIndex={bundle.log_entry.log_index}")

def test_sign_pending_entries(chain_tlog: TrustedLog):
    print("Signing pending entries...")

    chain_tlog.add_entry({"entry1": "data1"})
    chain_tlog.add_entry({"entry2": "data2"})

    with open("pending_entries.json", 'w', encoding='utf-8') as f:
        json.dump(chain_tlog.pending_entries, f, ensure_ascii=False)

    bundle = chain_tlog.sign_pending_entries()

    bundle_filename = "pending_entries.sigstore.json"
    with open(bundle_filename, 'w', encoding='utf-8') as f:
        bundle_data = json.loads(bundle.to_json())
        json.dump(bundle_data, f, indent=2, ensure_ascii=False)
    print(f"Bundle saved to: {bundle_filename}")
    print(f"Signing pending entries completed.")
    print(f"https://search.sigstore.dev/?logIndex={bundle.log_entry.log_index}")

def test_verify(email_addr: str):
    print("Verifying...")

    my_policy = policy.Identity(
        identity=email_addr,
        issuer="https://github.com/login/oauth",
    )

    verifier = Verifier.production()

    # Verify using file
    file_content = Path(TEST_FILE).read_bytes()
    verifier.verify_artifact(
        file_content,
        Bundle.from_json(asset(f"{TEST_FILE}.sigstore.json").read_bytes()),
        policy.UnsafeNoOp()
    )

    # Verify using file digest
    file_content_digest = generate_file_digest(TEST_FILE)
    file_content_hashed = sigstore_hashes.Hashed(
        digest=file_content_digest, algorithm=sigstore_hashes.HashAlgorithm.SHA2_256
    )
    verifier.verify_artifact(
        file_content_hashed,
        Bundle.from_json(asset(f"{TEST_FILE}.sigstore.json").read_bytes()),
        policy.UnsafeNoOp()
    )

    # Verify using pending entries
    json_content = Path("pending_entries.json").read_bytes()
    verifier.verify_artifact(
        json_content,
        Bundle.from_json(asset("pending_entries.sigstore.json").read_bytes()),
        policy.UnsafeNoOp()
    )
    print("Verification successful using `no-op` policy")

    verifier.verify_artifact(
        file_content,
        Bundle.from_json(asset(f"{TEST_FILE}.sigstore.json").read_bytes()),
        my_policy
    )
    verifier.verify_artifact(
        file_content_hashed,
        Bundle.from_json(asset(f"{TEST_FILE}.sigstore.json").read_bytes()),
        my_policy
    )
    verifier.verify_artifact(
        json_content,
        Bundle.from_json(asset("pending_entries.sigstore.json").read_bytes()),
        my_policy
    )
    print("Verification successful using email identity policy")

    Path(f"{TEST_FILE}.sigstore.json").unlink()
    Path("pending_entries.sigstore.json").unlink()
    Path("pending_entries.json").unlink()
    print("Verifying completed.")

def test_sign_with_chain(chain_tlog: TrustedLog):
    # Add the first entries and sign
    chain_tlog.add_entry({"action1": "create_user"})
    chain_tlog.add_entry({"action2": "grant_permission"})
    with open("entry1.json", 'w', encoding='utf-8') as f:
        json.dump(chain_tlog.pending_entries, f, ensure_ascii=False)
    bundle1 = chain_tlog.sign_pending_entries()
    log_index1 = bundle1.log_entry.log_index

    # Save the first bundle
    bundle_filename = f"entry1_{log_index1}.sigstore.json"
    with open(bundle_filename, 'w', encoding='utf-8') as f:
        bundle_data = json.loads(bundle1.to_json())
        json.dump(bundle_data, f, indent=2, ensure_ascii=False)
    print(f"First signature completed, Bundle saved to: {bundle_filename}")
    print(f"https://search.sigstore.dev/?logIndex={bundle1.log_entry.log_index}")

    # Add the second batch of entries and sign them
    # They will contain the hash of the previous batch
    chain_tlog.add_entry({"action3": "update_user"})
    chain_tlog.add_entry({"action4": "revoke_permission"})
    with open("entry2.json", 'w', encoding='utf-8') as f:
        json.dump(chain_tlog.pending_entries, f, ensure_ascii=False)
    bundle2 = chain_tlog.sign_pending_entries()
    log_index2 = bundle2.log_entry.log_index

    # Save the second bundle
    bundle_filename = f"entry2_{log_index2}.sigstore.json"
    with open(bundle_filename, 'w', encoding='utf-8') as f:
        bundle_data = json.loads(bundle2.to_json())
        json.dump(bundle_data, f, indent=2, ensure_ascii=False)
    print(f"Second signature completed, Bundle saved to: {bundle_filename}")
    print(f"https://search.sigstore.dev/?logIndex={bundle2.log_entry.log_index}")

    # Get chain summary
    summary = chain_tlog.get_chain_summary()
    print(f"Chain summary: {json.dumps(summary, indent=2)}")

    # Export chain data
    chain_data = chain_tlog.export_chain()
    with open("chain.sigstore.json", "w") as f:
        json.dump(chain_data, f, indent=2)
    print("Chain data exported to chain.sigstore.json")
    print("Signing with chain completed.")

def test_verify_chain(identity_token, email_addr: str):
    print("Verifying chain...")

    my_policy = policy.Identity(
        identity=email_addr,
        issuer="https://github.com/login/oauth",
    )

    try:
        chain_tlog = TrustedLog.from_backup_file(
            identity_token=identity_token,
            backup_file_path="chain.sigstore.json"
        )
        print(f"Successfully restored chain: {chain_tlog.chain_id}")
        print(f"Chain length: {chain_tlog.chain_length}")
        print(f"Chain summary: {chain_tlog.get_chain_summary()}")

        sigstore_files = list(Path(".").glob("entry*.sigstore.json"))
        # Verify each entry in the chain
        result = chain_tlog.verify_chain(
            sigstore_file_list=sigstore_files,
            policy=my_policy,
        )
        if result.success:
            print("🎉 Chain verification successful!")
            print(f"Chain ID: {result.chain_id}")
            print(f"Verified entries: {result.verified_entries}/{result.total_entries}")
            print("Verification details:", result.details)
        else:
            print("❌ Chain verification failed!")
            for error in result.errors:
                print(f"  - {error}")

        # Get verification summary
        summary = chain_tlog.get_verification_summary()
        print("Verification summary:", json.dumps(summary, indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Failed to restore from backup: {e}")


if __name__ == "__main__":
    email_addr = input("Please input the email address used for signing: ").strip()
    issuer = Issuer.production()
    identity_token = issuer.identity_token()

    chain_tlog = TrustedLog(identity_token)

    test_sign_with_chain(chain_tlog)
    test_verify_chain(identity_token, email_addr)

    test_sign_file(chain_tlog)
    test_sign_pending_entries(chain_tlog)
    test_verify(email_addr)

    Path(TEST_FILE).unlink()
