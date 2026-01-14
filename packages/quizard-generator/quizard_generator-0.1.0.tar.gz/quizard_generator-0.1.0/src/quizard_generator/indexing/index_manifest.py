"""
Index manifest management for tracking indexed files per domain.

Maintains a manifest file (.indexed_files.json) in each domain's storage
directory to track which files have been indexed, their hashes, and metadata.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)


class IndexManifest:
    """
    Manages manifest files that track indexed documents per domain.
    
    The manifest stores:
    - File paths and hashes for change detection
    - Document IDs assigned to each file
    - Number of nodes generated from each file
    - Timestamp of when each file was indexed
    """
    
    MANIFEST_FILENAME = ".indexed_files.json"
    
    def __init__(self, storage_path: str):
        """
        Initialise the index manifest.
        
        Args:
            storage_path: Path to domain's storage directory
        """
        self.storage_path = Path(storage_path)
        self.manifest_path = self.storage_path / self.MANIFEST_FILENAME
        self._manifest_data: Optional[Dict] = None
    
    def load(self) -> Dict:
        """
        Load manifest from disk.
        
        Returns:
            Manifest dictionary with indexed file information
        """
        if not self.manifest_path.exists():
            # return empty manifest
            return {
                "indexed_files": {},
                "last_updated": None
            }
        
        try:
            with open(self.manifest_path, 'r') as f:
                data = json.load(f)
                self._manifest_data = data
                return data
        except Exception as e:
            logger.error(f"Failed to load manifest from {self.manifest_path}: {e}")
            # return empty manifest on error
            return {
                "indexed_files": {},
                "last_updated": None
            }
    
    def save(self, manifest: Dict):
        """
        Save manifest to disk.
        
        Args:
            manifest: Manifest dictionary to save
        """
        # ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # update last_updated timestamp
        manifest['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self._manifest_data = manifest
            logger.info(f"Saved manifest to {self.manifest_path}")
            
        except Exception as e:
            logger.error(f"Failed to save manifest to {self.manifest_path}: {e}")
            raise
    
    def get_file_hash(self, filepath: str) -> str:
        """
        Calculate MD5 hash of a file for change detection.
        
        Args:
            filepath: Path to file
        
        Returns:
            MD5 hash as hexadecimal string
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {filepath}: {e}")
            raise
    
    def get_indexed_files(self, manifest: Optional[Dict] = None) -> Set[str]:
        """
        Get set of filenames that are already indexed.
        
        Args:
            manifest: Manifest dictionary (loads from disk if not provided)
        
        Returns:
            Set of indexed filenames
        """
        if manifest is None:
            manifest = self.load()
        
        return set(manifest.get('indexed_files', {}).keys())
    
    def get_new_files(self, all_files: List[str]) -> List[str]:
        """
        Identify files that are not in the manifest (new files).
        
        Args:
            all_files: List of file paths to check
        
        Returns:
            List of file paths that are new (not in manifest)
        """
        manifest = self.load()
        indexed_files = self.get_indexed_files(manifest)
        
        new_files = []
        for filepath in all_files:
            filename = Path(filepath).name
            if filename not in indexed_files:
                new_files.append(filepath)
        
        return new_files
    
    def get_modified_files(self, all_files: List[str]) -> List[str]:
        """
        Identify files that exist in manifest but have changed (different hash).
        
        Args:
            all_files: List of file paths to check
        
        Returns:
            List of file paths that have been modified
        """
        manifest = self.load()
        indexed_files = manifest.get('indexed_files', {})
        
        modified_files = []
        for filepath in all_files:
            filename = Path(filepath).name
            
            if filename in indexed_files:
                # file exists in manifest, check if hash changed
                old_hash = indexed_files[filename].get('file_hash')
                
                try:
                    current_hash = self.get_file_hash(filepath)
                    
                    if old_hash != current_hash:
                        modified_files.append(filepath)
                        logger.info(f"File modified: {filename}")
                except Exception as e:
                    logger.warning(f"Could not hash file {filepath}: {e}")
        
        return modified_files
    
    def get_deleted_files(self, current_files: List[str]) -> List[str]:
        """
        Identify files in manifest that no longer exist in data directory.
        
        Args:
            current_files: List of file paths that currently exist
        
        Returns:
            List of filenames that are in manifest but deleted from disk
        """
        manifest = self.load()
        indexed_files = self.get_indexed_files(manifest)
        
        current_filenames = {Path(f).name for f in current_files}
        deleted_files = indexed_files - current_filenames
        
        return list(deleted_files)
    
    def add_indexed_file(
        self,
        filepath: str,
        doc_ids: List[str],
        num_nodes: int
    ):
        """
        Add a newly indexed file to the manifest.
        
        Args:
            filepath: Path to the indexed file
            doc_ids: List of document IDs created from this file
            num_nodes: Number of nodes generated from this file
        """
        manifest = self.load()
        filename = Path(filepath).name
        
        # calculate file hash
        try:
            file_hash = self.get_file_hash(filepath)
        except Exception as e:
            logger.error(f"Failed to hash file {filepath}: {e}")
            file_hash = "unknown"
        
        # add file info to manifest
        manifest['indexed_files'][filename] = {
            "file_path": str(Path(filepath).absolute()),
            "file_hash": file_hash,
            "indexed_at": datetime.now().isoformat(),
            "num_nodes": num_nodes,
            "doc_ids": doc_ids
        }
        
        self.save(manifest)
    
    def remove_file(self, filename: str):
        """
        Remove a file from the manifest.
        
        Args:
            filename: Name of file to remove from manifest
        """
        manifest = self.load()
        
        if filename in manifest.get('indexed_files', {}):
            del manifest['indexed_files'][filename]
            self.save(manifest)
            logger.info(f"Removed {filename} from manifest")
    
    def get_file_doc_ids(self, filename: str) -> List[str]:
        """
        Get document IDs associated with a file.
        
        Args:
            filename: Name of file
        
        Returns:
            List of document IDs, or empty list if file not in manifest
        """
        manifest = self.load()
        file_info = manifest.get('indexed_files', {}).get(filename, {})
        return file_info.get('doc_ids', [])
    
    def get_stats(self) -> Dict:
        """
        Get statistics from the manifest.
        
        Returns:
            Dictionary with statistics about indexed files
        """
        manifest = self.load()
        indexed_files = manifest.get('indexed_files', {})
        
        total_nodes = sum(
            file_info.get('num_nodes', 0)
            for file_info in indexed_files.values()
        )
        
        return {
            "total_files": len(indexed_files),
            "total_nodes": total_nodes,
            "last_updated": manifest.get('last_updated')
        }
    
    def clear(self):
        """
        Clear the manifest (remove all tracked files).
        
        Useful when doing a full re-index.
        """
        manifest = {
            "indexed_files": {},
            "last_updated": None
        }
        self.save(manifest)
        logger.info("Cleared manifest")
