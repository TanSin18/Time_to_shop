# Legacy Code

This directory contains the original implementation files from version 1.0.

## Files

- `scorer.py`: Original monolithic prediction script
- `__init__.py`: Original empty init file

## Important Notes

⚠️ **These files are kept for reference only and should not be used in production.**

The code has been completely refactored in v2.0 with:
- Modular architecture
- Better error handling
- Configuration management
- Type safety
- Modern Python practices

## Migration

If you're still using the old code, please refer to [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) for instructions on migrating to v2.0.

## Why Keep These?

These files are preserved to:
1. Provide reference for understanding the original implementation
2. Help with migration from v1.0 to v2.0
3. Maintain project history

## Differences from v2.0

| Aspect | v1.0 (Legacy) | v2.0 (Current) |
|--------|---------------|----------------|
| Structure | Single file | Modular packages |
| Configuration | Hardcoded | Environment vars |
| Error handling | Minimal | Comprehensive |
| Type hints | None | Full coverage |
| Testing | None | Unit tests |
| Documentation | Limited | Extensive |
| CLI | None | Full CLI |

See the main [README.md](../README.md) for current documentation.
