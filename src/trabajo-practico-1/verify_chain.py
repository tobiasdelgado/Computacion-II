import os
from common import load_blockchain, calculate_block_hash


def recalculate_hash(block, previous_hash):
    """Recalculate hash for a block using common encryption function"""
    return calculate_block_hash(previous_hash, block["data"], block["timestamp"])


def verify_blockchain_integrity():
    blockchain = load_blockchain()

    if blockchain is None:
        return False

    if len(blockchain) == 0:
        print("✅ Blockchain is empty - no corruption possible")
        return True

    print(f"🔍 Verifying blockchain with {len(blockchain)} blocks...")
    corrupted_blocks = []
    previous_hash = "0"

    for i, block in enumerate(blockchain):
        expected_hash = recalculate_hash(block, previous_hash)
        stored_hash = block["hash"]
        stored_prev_hash = block["prev_hash"]

        if stored_prev_hash != previous_hash:
            corrupted_blocks.append(
                {
                    "block_index": i,
                    "error": "Previous hash mismatch",
                    "expected_prev": previous_hash,
                    "stored_prev": stored_prev_hash,
                }
            )

        if stored_hash != expected_hash:
            corrupted_blocks.append(
                {
                    "block_index": i,
                    "error": "Hash mismatch",
                    "expected_hash": expected_hash,
                    "stored_hash": stored_hash,
                }
            )

        previous_hash = stored_hash

    if len(corrupted_blocks) == 0:
        print("✅ Blockchain integrity verified - no corruption detected")
        return True
    else:
        print(f"❌ Blockchain corruption detected in {len(corrupted_blocks)} issues:")
        for corruption in corrupted_blocks:
            print(f"   Block #{corruption['block_index']}: {corruption['error']}")
        return False


def generate_report():
    blockchain = load_blockchain()
    if blockchain is None:
        return

    total_blocks = len(blockchain)
    alert_blocks = sum(1 for block in blockchain if block.get("alert", False))

    if total_blocks == 0:
        print("📊 No blocks to analyze for report")
        return

    frequency_values = []
    systolic_values = []
    diastolic_values = []
    oxygen_values = []

    for block in blockchain:
        data = block["data"]
        frequency_values.append(data["frequency"]["mean"])
        systolic_values.append(data["pressure"]["mean"][0])
        diastolic_values.append(data["pressure"]["mean"][1])
        oxygen_values.append(data["oxygen"]["mean"])

    avg_frequency = sum(frequency_values) / len(frequency_values)
    avg_systolic = sum(systolic_values) / len(systolic_values)
    avg_diastolic = sum(diastolic_values) / len(diastolic_values)
    avg_oxygen = sum(oxygen_values) / len(oxygen_values)

    report_content = f"""BLOCKCHAIN ANALYSIS REPORT
{"=" * 50}

SUMMARY:
- Total blocks: {total_blocks}
- Blocks with alerts: {alert_blocks}
- Alert percentage: {(alert_blocks / total_blocks) * 100:.1f}%

ANALYSIS:
- Normal frequency range: 60-100 bpm (Current: {avg_frequency:.1f})
- Normal systolic range: 90-140 mmHg (Current: {avg_systolic:.1f})
- Normal diastolic range: 60-90 mmHg (Current: {avg_diastolic:.1f})
- Normal oxygen range: 95-100% (Current: {avg_oxygen:.1f})

"""

    base_path = os.path.dirname(__file__)

    with open(os.path.join(base_path, "report.txt"), "w") as f:
        f.write(report_content)

    print("📈 Report generated successfully:")


if __name__ == "__main__":
    print("BLOCKCHAIN VERIFICATION")
    print("=" * 40)

    integrity_ok = verify_blockchain_integrity()

    generate_report()

    print("\n" + "=" * 40)
    if integrity_ok:
        print("✅ Blockchain verification completed successfully")
    else:
        print("❌ Blockchain verification completed with errors")
