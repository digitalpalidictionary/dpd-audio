# DPD Audio Database

Simple audio retrieval for DPD pronunciations.

## Quick Start

```python
from resources.dpd_audio.db.db_helpers import setup_audio_database, get_audio_record

# Set up database once
setup_audio_database()

# Get audio data directly
audio_data = get_audio_record("pāṇi", "male")
audio_data = get_audio_record("pāṇi", "female")
```

## Requirements

- Database must exist at `resources/dpd_audio/db/dpd_audio.db`
- Use `"male"` or `"female"` strings for gender parameter

## Database Setup

To create and populate the database:

```python
from resources.dpd_audio.db.db_helpers import setup_audio_database

# Create and populate database in one step
db_path = setup_audio_database()
```

## Returns

- Audio data as bytes (MP3 format)
- `None` if lemma not found
- Raises `FileNotFoundError` if database doesn't exist
