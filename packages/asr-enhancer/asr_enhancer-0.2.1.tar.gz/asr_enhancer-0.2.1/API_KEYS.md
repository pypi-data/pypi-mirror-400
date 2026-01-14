# API Keys

## Dev Key (Expires after 2 hours)
```
sk-asr-2024-prod-key-001-xyz789
```
- **Usage**: Testing and development
- **Expiration**: 2 hours after first use
- **Server behavior**: Stops when key expires

## Client Keys (No expiration)
```
sk-asr-2024-prod-key-002-abc123
sk-asr-2024-prod-key-003-def456
sk-asr-2024-prod-key-004-ghi789
sk-asr-2024-prod-key-005-jkl012
sk-asr-2024-prod-key-006-mno345
sk-asr-2024-prod-key-007-pqr678
sk-asr-2024-prod-key-008-stu901
sk-asr-2024-prod-key-009-vwx234
sk-asr-2024-prod-key-010-yz0567
```
- **Usage**: Give to clients for production use
- **Expiration**: Never
- **Server behavior**: Works forever, no rotation needed

## Usage Examples

### Start server with dev key (testing):
```bash
python -m asr_enhancer.api.main --cpu --keys "sk-asr-2024-prod-key-001-xyz789"
```

### Start server with client key (production):
```bash
python -m asr_enhancer.api.main --cpu --keys "sk-asr-2024-prod-key-002-abc123"
```

### Start server with GPU:
```bash
python -m asr_enhancer.api.main --gpu --keys "sk-asr-2024-prod-key-003-def456"
```
