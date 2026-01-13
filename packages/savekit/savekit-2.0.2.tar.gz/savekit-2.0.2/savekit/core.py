import json
import os
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Text, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

Base = declarative_base()

class StoreItem(Base):
    """
    SQLAlchemy model representing a key-value pair in the store.
    """
    __tablename__ = "store"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)


class SaveKit:
    """
    SaveKit: A lightweight persistent key-value storage system using SQLite via SQLAlchemy.

    This class allows storing primitive types, complex objects, and Pydantic BaseModel instances.
    It supports context manager usage, project-root storage, and safe session handling.

    Attributes:
        engine (Engine): SQLAlchemy engine connected to the SQLite database.
        SessionLocal (sessionmaker): SQLAlchemy session factory.
        _session (Session | None): Internal session for context manager usage.

    Methods:
        set_item(key, value): Add or update a key-value pair.
        get_item(key, default=None, model=None): Retrieve a value by key, optionally as a Pydantic model.
        delete_item(key): Delete a key-value pair.
        get_all_items(): Return all key-value pairs.
        clear_store(): Remove all entries from the store.
        export_store(export_path): Export all data to a JSON file.
        import_store(import_path): Import data from a JSON file.
        reload_store(): Reload all items from the database.
    """

    def __init__(self, db_name: str = "savekit"):
        """
        Initialize the SaveKit instance with a database in the project-root store folder.

        Args:
            db_name (str): Base name for the SQLite database file (default: 'savekit').
        """

        if db_name.endswith(".db"):
            raise RuntimeError(f"db_name must not end with '.db'")

        venv_dir = self.__get_root_venv()

        if venv_dir is None:
            raise RuntimeError(
                "Project root with a '.venv' folder not found. "
                "Please create a virtual environment by running 'python -m venv .venv' in the project root."
            )

        store_dir = venv_dir / "store"

        if not store_dir.exists():
            try:
                os.makedirs(store_dir, exist_ok=True)
            except Exception as e:
                raise RuntimeError("Failed to create 'store' directory in project root.") from e

        try:
            db_path = store_dir / f"{db_name}.db"
            db_url = f"sqlite:///{db_path}"

            self.engine = create_engine(db_url, echo=False, future=True)
            Base.metadata.create_all(self.engine)
            self.sessionDBLocal = sessionmaker(bind=self.engine, future=True)
        except Exception as e:
            raise RuntimeError(f"Error initializing database: {e}")

        self._session: Session | None = None

    def __enter__(self):
        """
        Enter the runtime context related to this object, opening a session.
        """
        try:
            self._session = self.sessionDBLocal()
        except Exception as e:
            raise RuntimeError(f"Failed to open session: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context, closing the session if open.
        """
        if self._session:
            self._session.close()
            self._session = None

    def __get_root_venv(self) -> Path | None:
        """
        Searches for the project root directory by looking for a '.venv' folder.

        The search starts from the directory of the current file and moves up
        through all parent directories until it finds a folder named '.venv'.

        Returns:
            Path | None: The Path object pointing to the project root if a '.venv'
                         folder is found, otherwise None.
        """
        venv_folder_name = ".venv"
        path = Path(__file__).resolve()
        for parent in [path.parent] + list(path.parents):
            if (parent / venv_folder_name).exists() and (parent / venv_folder_name).is_dir():
                return parent
        return None

    @property
    def sessionDB(self) -> Session:
        """
        Return the active session, or create a temporary one if not using context manager.

        Returns:
            Session: SQLAlchemy session.
        """
        if self._session is None:
            return self.sessionDBLocal()
        return self._session

    def set_item(self, key: str, value):
        """
        Store a value associated with a key. Supports Pydantic models and JSON-serializable objects.

        Args:
            key (str): Unique key for the value.
            value: Any JSON-serializable object or Pydantic BaseModel.
        """
        try:
            value_to_store = json.dumps(value.dict()) if isinstance(value, BaseModel) else json.dumps(value)
        except Exception as e:
            raise ValueError(f"Failed to serialize value: {e}")

        s = self.sessionDB
        try:
            item = s.execute(select(StoreItem).where(StoreItem.key == key)).scalar_one_or_none()
            if item:
                item.value = value_to_store
            else:
                item = StoreItem(key=key, value=value_to_store)
                s.add(item)
            s.commit()
        except Exception as e:
            s.rollback()
            raise RuntimeError(f"Error saving item to DB: {e}")
        finally:
            if self._session is None:
                s.close()

    def get_item(self, key: str, default=None, model: type[BaseModel] | None = None):
        """
        Retrieve a value by key, optionally as a Pydantic model.

        Args:
            key (str): Key to retrieve.
            default: Value to return if key is not found (default: None).
            model (BaseModel type, optional): Pydantic model to parse the value into.

        Returns:
            The stored value, parsed into the model if provided, or the default.
        """
        s = self.sessionDB
        try:
            item = s.execute(select(StoreItem).where(StoreItem.key == key)).scalar_one_or_none()
            if not item:
                return default

            try:
                value = json.loads(item.value)
            except json.JSONDecodeError:
                value = item.value

            if model and issubclass(model, BaseModel):
                try:
                    return model.parse_obj(value)
                except Exception:
                    return default
            return value
        except Exception:
            return default
        finally:
            if self._session is None:
                s.close()

    def delete_item(self, key: str):
        """
        Delete a key-value pair from the store.

        Args:
            key (str): Key to delete.
        """
        s = self.sessionDB
        try:
            item = s.execute(select(StoreItem).where(StoreItem.key == key)).scalar_one_or_none()
            if item:
                s.delete(item)
                s.commit()
        except Exception as e:
            s.rollback()
            raise RuntimeError(f"Error deleting item: {e}")
        finally:
            if self._session is None:
                s.close()

    def get_all_items(self):
        """
        Return all stored key-value pairs.

        Returns:
            dict: All items as a dictionary.
        """
        s = self.sessionDB
        result = {}
        try:
            items = s.execute(select(StoreItem)).scalars().all()
            for item in items:
                try:
                    result[item.key] = json.loads(item.value)
                except json.JSONDecodeError:
                    result[item.key] = item.value
        except Exception as e:
            raise RuntimeError(f"Error fetching all items: {e}")
        finally:
            if self._session is None:
                s.close()
        return result

    def clear_store(self):
        """
        Remove all entries from the store.
        """
        s = self.sessionDB
        try:
            s.query(StoreItem).delete()
            s.commit()
        except Exception as e:
            s.rollback()
            raise RuntimeError(f"Error clearing store: {e}")
        finally:
            if self._session is None:
                s.close()

    def export_store(self, export_path: str):
        """
        Export all stored data to a JSON file.

        Args:
            export_path (str): File path to save the exported data.
        """
        try:
            data = self.get_all_items()
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to export store: {e}")

    def import_store(self, import_path: str):
        """
        Import data from a JSON file, replacing current store content.

        Args:
            import_path (str): Path to the JSON file to import.
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read import file: {e}")

        self.clear_store()
        for key, value in data.items():
            try:
                self.set_item(key, value)
            except Exception as e:
                print(f"Error importing key {key}: {e}")

    def reload_store(self):
        """
        Reload all items from the database.

        Returns:
            dict: All items in the store.
        """
        return self.get_all_items()
