"""Database helpers for DPD audio files."""

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, DpdAudio
from tools.printer import printer as pr


def create_audio_database(db_path: Optional[Path] = None) -> Path:
    """
    Create the audio database if it doesn't exist.

    Args:
        db_path: Path to the database file. If None, uses default location.

    Returns:
        Path to the created database file.
    """
    if db_path is None:
        db_path = Path(__file__).parent / "dpd_audio.db"

    # Create the database engine
    engine = create_engine(f"sqlite+pysqlite:///{db_path}", echo=False)

    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)

    return db_path


def get_audio_session(db_path: Optional[Path] = None) -> Session:
    """
    Get a database session for audio operations.

    Args:
        db_path: Path to the database file. If None, uses default location.

    Returns:
        SQLAlchemy session object.
    """
    if db_path is None:
        db_path = Path(__file__).parent / "dpd_audio.db"

    engine = create_engine(f"sqlite+pysqlite:///{db_path}", echo=False)
    SessionLocal = sessionmaker(bind=engine)

    return SessionLocal()


def populate_audio_database(
    db_path: Optional[Path] = None,
    male_folder: Optional[Path] = None,
    female_folder: Optional[Path] = None,
) -> None:
    """
    Populate the audio database with files from the specified folders.

    Args:
        db_path: Path to the database file. If None, uses default location.
        male_folder: Path to the male audio files folder. If None, uses default.
        female_folder: Path to the female audio files folder. If None, uses default.
    """
    if db_path is None:
        db_path = Path(__file__).parent / "dpd_audio.db"

    if male_folder is None:
        male_folder = Path(__file__).parent.parent / "mp3s" / "Kannada_kn-m4_Neutral"

    if female_folder is None:
        female_folder = Path(__file__).parent.parent / "mp3s" / "Kannada_kn-f4_Neutral"

    # Ensure folders exist
    if not male_folder.exists():
        raise FileNotFoundError(f"Male audio folder not found: {male_folder}")

    if not female_folder.exists():
        raise FileNotFoundError(f"Female audio folder not found: {female_folder}")

    # Create database if needed
    create_audio_database(db_path)

    # Get session
    session = get_audio_session(db_path)

    try:
        # Get all audio files from both folders, excluding files starting with "!"
        male_files = {
            f.stem: f for f in male_folder.glob("*.mp3") if not f.stem.startswith("!")
        }
        female_files = {
            f.stem: f for f in female_folder.glob("*.mp3") if not f.stem.startswith("!")
        }

        # Get all unique headwords (lemma_clean values)
        all_headwords = set(male_files.keys()) | set(female_files.keys())

        # Process each headword
        for headword in sorted(all_headwords):
            # Read the binary data for male and female audio files
            male_blob: Optional[bytes] = None
            female_blob: Optional[bytes] = None

            if headword in male_files:
                with open(male_files[headword], "rb") as f:
                    male_blob = f.read()

            if headword in female_files:
                with open(female_files[headword], "rb") as f:
                    female_blob = f.read()

            # Check if record already exists
            existing = (
                session.query(DpdAudio).filter(DpdAudio.lemma_clean == headword).first()
            )

            if existing:
                # Update existing record
                existing.male1 = male_blob  # type: ignore
                existing.female1 = female_blob  # type: ignore
            else:
                # Create new record
                audio_record = DpdAudio(
                    lemma_clean=headword, male1=male_blob, female1=female_blob
                )
                session.add(audio_record)

        # Commit all changes
        session.commit()

        pr.yes(
            f"Successfully populated audio database with {len(all_headwords)} entries"
        )

    except Exception as e:
        session.rollback()
        pr.red(f"Error populating audio database: {e}")
        raise
    finally:
        session.close()


def get_audio_record(headword: str, gender: str) -> Optional[bytes]:
    """
    Get audio data for a specific headword and gender.

    Args:
        headword: The lemma_clean value to search for.
        gender: 'male' or 'female' to specify which audio to return.

    Returns:
        Audio data as bytes if found, None otherwise.
    """
    db_path = Path(__file__).parent / "dpd_audio.db"
    session = get_audio_session(db_path)

    try:
        record = (
            session.query(DpdAudio).filter(DpdAudio.lemma_clean == headword).first()
        )
        if not record:
            return None

        gender = gender.lower()
        if gender == "male":
            return record.male1
        elif gender == "female":
            return record.female1
        else:
            raise ValueError("Gender must be 'male' or 'female'")
    finally:
        session.close()


def setup_audio_database(db_path: Optional[Path] = None) -> Path:
    """
    Create and populate the audio database in one step.

    Args:
        db_path: Path to the database file. If None, uses default location.

    Returns:
        Path to the created database file.
    """
    if db_path is None:
        db_path = Path(__file__).parent / "dpd_audio.db"

    # Create the database
    create_audio_database(db_path)

    # Populate with audio files
    populate_audio_database(db_path)

    return db_path


def clear_audio_database(db_path: Optional[Path] = None) -> None:
    """
    Clear all records from the audio database.

    Args:
        db_path: Path to the database file. If None, uses default location.
    """
    session = get_audio_session(db_path)

    try:
        session.query(DpdAudio).delete()
        session.commit()
        pr.yes("Audio database cleared")
    except Exception as e:
        session.rollback()
        pr.red(f"Error clearing audio database: {e}")
        raise
    finally:
        session.close()
