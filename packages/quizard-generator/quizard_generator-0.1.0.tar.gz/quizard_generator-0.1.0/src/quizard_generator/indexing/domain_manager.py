"""
Domain management for multi-domain quiz generation system.

Handles domain detection, validation, and path management for separating
different subject areas (maths, biology, chemistry, etc.).
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from quizard_generator.exceptions import DomainNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class DomainInfo:
    """Information about a domain."""
    name: str
    data_path: str
    storage_path: str
    num_files: int
    total_size: float
    is_indexed: bool
    last_updated: Optional[str] = None
    num_nodes: Optional[int] = None


class DomainManager:
    """
    Manages domain detection, validation, and path resolution.
    
    Provides functionality to:
    - List available domains from data directory
    - Validate domain existence
    - Get domain-specific paths for data and storage
    - Retrieve domain statistics
    """
    
    def __init__(self, base_data_dir: str = "data", base_storage_dir: str = "storage"):
        """
        Initialise the domain manager.
        
        Args:
            base_data_dir: Root directory containing domain subdirectories
            base_storage_dir: Root directory for domain-specific storage
        """
        self.base_data_dir = Path(base_data_dir)
        self.base_storage_dir = Path(base_storage_dir)
        
        # ensure base directories exist
        self.base_data_dir.mkdir(exist_ok=True)
        self.base_storage_dir.mkdir(exist_ok=True)
    
    def list_available_domains(self) -> List[str]:
        """
        Scan data directory for domain subdirectories.
        
        Returns:
            List of domain names (subdirectory names)
        """
        if not self.base_data_dir.exists():
            return []
        
        domains = []
        for item in self.base_data_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                domains.append(item.name)
        
        return sorted(domains)
    
    def validate_domain(self, domain: str) -> bool:
        """
        Check if domain exists in data directory.
        
        Args:
            domain: Domain name to validate
        
        Returns:
            True if domain exists, False otherwise
        """
        domain_path = self.base_data_dir / domain
        return domain_path.exists() and domain_path.is_dir()
    
    def get_data_path(self, domain: str) -> str:
        """
        Get the data directory path for a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Absolute path to data/{domain}/
        """
        return str((self.base_data_dir / domain).absolute())
    
    def get_storage_path(self, domain: str) -> str:
        """
        Get the storage directory path for a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Absolute path to storage/{domain}/
        """
        return str((self.base_storage_dir / domain).absolute())
    
    def get_domain_info(self, domain: str) -> DomainInfo:
        """
        Get detailed information about a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            DomainInfo object with domain statistics
        
        Raises:
            ValueError: If domain doesn't exist
        """
        if not self.validate_domain(domain):
            raise ValueError(f"Domain '{domain}' not found in {self.base_data_dir}")
        
        data_path = self.base_data_dir / domain
        storage_path = self.base_storage_dir / domain
        
        # count files and calculate total size
        num_files = 0
        total_size = 0
        
        for file_path in data_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                num_files += 1
                total_size += file_path.stat().st_size
        
        # check if indexed
        is_indexed = storage_path.exists() and (storage_path / 'docstore.json').exists()
        
        # get last updated time and node count if indexed
        last_updated = None
        num_nodes = None
        
        if is_indexed:
            manifest_path = storage_path / '.indexed_files.json'
            if manifest_path.exists():
                import json
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        last_updated = manifest.get('last_updated')
                        
                        # count total nodes
                        num_nodes = 0
                        for file_info in manifest.get('indexed_files', {}).values():
                            num_nodes += file_info.get('num_nodes', 0)
                except Exception as e:
                    logger.warning(f"Failed to read manifest for domain '{domain}': {e}")
        
        return DomainInfo(
            name=domain,
            data_path=str(data_path.absolute()),
            storage_path=str(storage_path.absolute()),
            num_files=num_files,
            total_size=total_size,
            is_indexed=is_indexed,
            last_updated=last_updated,
            num_nodes=num_nodes
        )
    
    def ensure_storage_directory(self, domain: str) -> str:
        """
        Ensure storage directory exists for a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Absolute path to storage directory
        """
        storage_path = self.base_storage_dir / domain
        storage_path.mkdir(parents=True, exist_ok=True)
        return str(storage_path.absolute())
    
    def format_size(self, size_bytes: float) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted string (e.g., "2.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def print_available_domains(self):
        """
        Print a formatted list of available domains with statistics.
        
        Useful for --list-domains command.
        """
        domains = self.list_available_domains()
        
        if not domains:
            print("\nNo domains found in data directory.")
            print(f"Please create subdirectories in {self.base_data_dir}/ for each subject domain.")
            print("\nExample structure:")
            print("  data/")
            print("  ├── maths/")
            print("  │   └── calculus.pdf")
            print("  └── biology/")
            print("      └── genetics.pdf")
            return
        
        print("\nAvailable Domains:")
        print("=" * 80)
        print()
        
        for domain in domains:
            try:
                info = self.get_domain_info(domain)
                
                print(f"{domain}")
                print(f"  Location: {info.data_path}")
                print(f"  Documents: {info.num_files} files ({self.format_size(info.total_size)})")
                
                if info.is_indexed:
                    nodes_str = f"{info.num_nodes} nodes" if info.num_nodes else "unknown nodes"
                    updated_str = f"Last updated: {info.last_updated}" if info.last_updated else ""
                    print(f"  Indexed: Yes ({nodes_str})")
                    if updated_str:
                        print(f"  {updated_str}")
                else:
                    print(f"  Indexed: No")
                
                print()
                
            except Exception as e:
                logger.error(f"Error getting info for domain '{domain}': {e}")
                print(f"{domain}")
                print(f"  Error: {e}")
                print()
        
        print("Tip: Use --index --domain <name> to index a domain")
        print("     Use --generate --domain <name> to generate quizzes")
    
    def validate_or_raise(self, domain: str):
        """
        Validate domain exists, raise exception if not.
        
        Args:
            domain: Domain name to validate
        
        Raises:
            DomainNotFoundError: If domain doesn't exist
        """
        if not self.validate_domain(domain):
            available = self.list_available_domains()
            raise DomainNotFoundError(domain, available)
    
    def validate_or_exit(self, domain: str):
        """
        Validate domain exists, exit with helpful message if not.
        
        Deprecated: Use validate_or_raise() instead for library usage.
        This method is kept for backward compatibility with main.py.
        
        Args:
            domain: Domain name to validate
        
        Raises:
            SystemExit: If domain doesn't exist
        """
        try:
            self.validate_or_raise(domain)
        except DomainNotFoundError as e:
            available = e.available_domains
            
            print(f"\nError: Domain '{domain}' not found in data directory.")
            print()
            
            if available:
                print("Available domains:")
                for d in available:
                    try:
                        info = self.get_domain_info(d)
                        status = "indexed" if info.is_indexed else "not indexed"
                        print(f"  - {d} ({info.num_files} files, {status})")
                    except:
                        print(f"  - {d}")
            else:
                print("No domains found.")
                print(f"\nPlease create {self.base_data_dir}/{domain}/ and add documents.")
            
            print()
            exit(1)
