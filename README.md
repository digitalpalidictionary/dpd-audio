# DPD Audio (Staging & Releases)

**CRITICAL: The development logic and scripts have moved to the root `audio/` directory.**

This directory (`resources/dpd_audio/`) is now primarily used for:
1.  **Staging area** for preparing audio releases.
2.  **Compatibility** with legacy tools that expect this path.

### Development
For all audio generation, database management, and error checking, use the scripts in the root `audio/` folder:

```bash
# Example: Generate audio
uv run python audio/bhashini/bhashini_generate_dpd.py
```

Refer to `audio/README.md` for full instructions.
