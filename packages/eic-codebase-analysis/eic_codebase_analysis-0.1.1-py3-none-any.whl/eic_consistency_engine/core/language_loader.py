import importlib
import pkgutil
import os
import inspect
from pathlib import Path
from typing import Optional
from core.language_models import LanguageSupport
import lang

def load_language_support(language: str) -> Optional[LanguageSupport]:
    try:
        module = importlib.import_module(f"lang.{language}")
        
        # 1. Try exact name match convention
        class_name = f"{language[0].upper()}{language[1:]}Support"
        support_class = getattr(module, class_name, None)
        if support_class:
            return support_class()
            
        # 2. Search for any class ending in 'Support' defined in this module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.endswith("Support") and obj.__module__ == module.__name__:
                return obj()
                
    except (ImportError, AttributeError):
        pass
    return None

def detect_language(repo_path: Path) -> Optional[str]:
    repo_path = Path(repo_path)
    if not repo_path.exists():
        return None
        
    max_count = 0
    best_lang = None
    
    # Iterate over modules in lang package
    for finder, name, ispkg in pkgutil.iter_modules(lang.__path__):
        support = load_language_support(name)
        if not support:
            continue
            
        # Count files matching extensions
        count = 0
        # Optimization: Don't walk too deep for detection? 
        # Or just walk everything. For large repos this might be slow.
        # Let's limit to top level or first few levels or just count quickly.
        # For now, full walk is safer to find "src" etc.
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip .git etc
                if '.git' in dirs: dirs.remove('.git')
                
                for file in files:
                    if Path(file).suffix in support.extensions:
                        count += 1
        except Exception:
            pass
            
        if count > max_count:
            max_count = count
            best_lang = name
            
    return best_lang
