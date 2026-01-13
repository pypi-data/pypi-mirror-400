#!/usr/bin/env python
"""mod2pip - Generate pip requirements.txt file based on imports

Usage:
    mod2pip [options] [<path>]

Arguments:
    <path>                The path to the directory containing the application
                          files for which a requirements file should be
                          generated (defaults to the current working
                          directory).

Options:
    --use-local           Use ONLY local package info instead of querying PyPI.
    --pypi-server <url>   Use custom PyPi server.
    --proxy <url>         Use Proxy, parameter will be passed to requests
                          library. You can also just set the environments
                          parameter in your terminal:
                          $ export HTTP_PROXY="http://10.10.1.10:3128"
                          $ export HTTPS_PROXY="https://10.10.1.10:1080"
    --debug               Print debug information
    --ignore <dirs>...    Ignore extra directories, each separated by a comma
    --no-follow-links     Do not follow symbolic links in the project
    --encoding <charset>  Use encoding parameter for file open
    --savepath <file>     Save the list of requirements in the given file
    --print               Output the list of requirements in the standard
                          output
    --force               Overwrite existing requirements.txt
    --diff <file>         Compare modules in requirements.txt to project
                          imports
    --clean <file>        Clean up requirements.txt by removing modules
                          that are not imported in project
    --mode <scheme>       Enables dynamic versioning with <compat>,
                          <gt> or <no-pin> schemes.
                          <compat> | e.g. Flask~=1.1.2
                          <gt>     | e.g. Flask>=1.1.2
                          <no-pin> | e.g. Flask
    --scan-notebooks      Look for imports in jupyter notebook files.
    --include-transitive  Include transitive dependencies (experimental).
    --transitive-depth <n> Maximum depth for transitive dependency resolution (default: 2).
    --enhanced-detection  Enable enhanced import detection (dynamic imports, conda packages).
"""
from contextlib import contextmanager
import os
import sys
import re
import logging
import ast
import traceback
import json
from docopt import docopt
import requests
from yarg import json2package
from yarg.exceptions import HTTPError

from mod2pip import __version__

REGEXP = [re.compile(r"^import (.+)$"), re.compile(r"^from ((?!\.+).*?) import (?:.*)$")]
DEFAULT_EXTENSIONS = [".py", ".pyw"]

scan_noteboooks = False


class NbconvertNotInstalled(ImportError):
    default_message = (
        "In order to scan jupyter notebooks, please install the nbconvert and ipython libraries"
    )

    def __init__(self, message=default_message):
        super().__init__(message)


@contextmanager
def _open(filename=None, mode="r"):
    """Open a file or ``sys.stdout`` depending on the provided filename.

    Args:
        filename (str): The path to the file that should be opened. If
            ``None`` or ``'-'``, ``sys.stdout`` or ``sys.stdin`` is
            returned depending on the desired mode. Defaults to ``None``.
        mode (str): The mode that should be used to open the file.

    Yields:
        A file handle.

    """
    if not filename or filename == "-":
        if not mode or "r" in mode:
            file = sys.stdin
        elif "w" in mode:
            file = sys.stdout
        else:
            raise ValueError("Invalid mode for file: {}".format(mode))
    else:
        file = open(filename, mode)

    try:
        yield file
    finally:
        if file not in (sys.stdin, sys.stdout):
            file.close()


def get_all_imports(path, encoding="utf-8", extra_ignore_dirs=None, follow_links=True):
    imports = set()
    raw_imports = set()
    candidates = []
    ignore_errors = False
    ignore_dirs = [
        ".hg",
        ".svn",
        ".git",
        ".tox",
        "__pycache__",
        "env",
        "venv",
        ".venv",
        ".ipynb_checkpoints",
    ]

    if extra_ignore_dirs:
        ignore_dirs_parsed = []
        for e in extra_ignore_dirs:
            ignore_dirs_parsed.append(os.path.basename(os.path.realpath(e)))
        ignore_dirs.extend(ignore_dirs_parsed)

    extensions = get_file_extensions()

    walk = os.walk(path, followlinks=follow_links)
    for root, dirs, files in walk:
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        candidates.append(os.path.basename(root))
        py_files = [file for file in files if file_ext_is_allowed(file, DEFAULT_EXTENSIONS)]
        candidates.extend([os.path.splitext(filename)[0] for filename in py_files])

        files = [fn for fn in files if file_ext_is_allowed(fn, extensions)]

        for file_name in files:
            file_name = os.path.join(root, file_name)
            contents = read_file_content(file_name, encoding)

            try:
                # Enhanced import detection
                static_imports = _get_static_imports(contents)
                dynamic_imports = _get_dynamic_imports(contents)
                
                raw_imports.update(static_imports)
                raw_imports.update(dynamic_imports)
                
            except Exception as exc:
                if ignore_errors:
                    traceback.print_exc(exc)
                    logging.warn("Failed on file: %s" % file_name)
                    continue
                else:
                    logging.error("Failed on file: %s" % file_name)
                    raise exc

    # Clean up imports
    for name in [n for n in raw_imports if n]:
        # Sanity check: Name could have been None if the import
        # statement was as ``from . import X``
        # Cleanup: We only want to first part of the import.
        # Ex: from django.conf --> django.conf. But we only want django
        # as an import.
        cleaned_name, _, _ = name.partition(".")
        imports.add(cleaned_name)

    packages = imports - (set(candidates) & imports)
    logging.debug("Found packages: {0}".format(packages))

    with open(join("stdlib"), "r") as f:
        data = {x.strip() for x in f}

    return list(packages - data)


def _get_static_imports(contents):
    """Extract imports using AST parsing (existing method)."""
    imports = set()
    
    try:
        tree = ast.parse(contents)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for subnode in node.names:
                    if subnode.name:
                        imports.add(subnode.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except SyntaxError:
        # If AST parsing fails, fall back to regex
        imports.update(_get_regex_imports(contents))
    
    return imports


def _get_dynamic_imports(contents):
    """Extract dynamic imports using pattern matching."""
    imports = set()
    
    # Pattern 1: __import__('module_name')
    import_pattern1 = re.compile(r'__import__\s*\(\s*["\']([^"\']+)["\']')
    
    # Pattern 2: importlib.import_module('module_name')
    import_pattern2 = re.compile(r'import_module\s*\(\s*["\']([^"\']+)["\']')
    
    # Pattern 3: exec("import module_name") or eval("import module_name")
    exec_import_pattern = re.compile(r'(?:exec|eval)\s*\(\s*["\'].*?import\s+([a-zA-Z_][a-zA-Z0-9_]*)')
    
    # Pattern 4: Dynamic imports in f-strings or format strings
    fstring_import_pattern = re.compile(r'f["\'].*?import\s+([a-zA-Z_][a-zA-Z0-9_]*)')
    
    # Pattern 5: Conditional imports (try/except blocks)
    try_import_pattern = re.compile(r'try\s*:.*?import\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.DOTALL)
    
    # Pattern 6: Late imports (imports inside functions)
    function_import_pattern = re.compile(r'def\s+\w+.*?:\s*.*?import\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.DOTALL)
    
    patterns = [
        import_pattern1, import_pattern2, exec_import_pattern,
        fstring_import_pattern, try_import_pattern, function_import_pattern
    ]
    
    for pattern in patterns:
        matches = pattern.findall(contents)
        for match in matches:
            if match and not match.startswith('.'):  # Skip relative imports
                imports.add(match)
    
    # Additional pattern: Look for string literals that might be module names
    # This catches cases like: module_name = "requests"; __import__(module_name)
    string_literals = re.findall(r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']', contents)
    potential_modules = set()
    
    for literal in string_literals:
        # Check if this string appears in an import context
        if (f'__import__({literal})' in contents or 
            f'import_module({literal})' in contents or
            literal in _get_common_package_names()):
            potential_modules.add(literal)
    
    imports.update(potential_modules)
    
    return imports


def _get_regex_imports(contents):
    """Fallback regex-based import extraction."""
    imports = set()
    
    # Basic import patterns
    import_patterns = [
        re.compile(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
        re.compile(r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import', re.MULTILINE),
    ]
    
    for pattern in import_patterns:
        matches = pattern.findall(contents)
        imports.update(matches)
    
    return imports


def _get_common_package_names():
    """Return a set of common package names to help identify dynamic imports."""
    return {
        'requests', 'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn',
        'tensorflow', 'torch', 'flask', 'django', 'fastapi', 'sqlalchemy',
        'pytest', 'click', 'pydantic', 'aiohttp', 'boto3', 'redis',
        'celery', 'gunicorn', 'uvicorn', 'psycopg2', 'pymongo', 'pillow',
        'opencv', 'beautifulsoup4', 'lxml', 'yaml', 'toml', 'json5',
        'dateutil', 'pytz', 'arrow', 'pendulum', 'cryptography', 'jwt',
        'httpx', 'websockets', 'asyncio', 'multiprocessing', 'threading'
    }


def get_file_extensions():
    return DEFAULT_EXTENSIONS + [".ipynb"] if scan_noteboooks else DEFAULT_EXTENSIONS


def read_file_content(file_name: str, encoding="utf-8"):
    if file_ext_is_allowed(file_name, DEFAULT_EXTENSIONS):
        with open(file_name, "r", encoding=encoding) as f:
            contents = f.read()
    elif file_ext_is_allowed(file_name, [".ipynb"]) and scan_noteboooks:
        contents = ipynb_2_py(file_name, encoding=encoding)
    return contents


def file_ext_is_allowed(file_name, acceptable):
    return os.path.splitext(file_name)[1] in acceptable


def ipynb_2_py(file_name, encoding="utf-8"):
    """

    Args:
        file_name (str): notebook file path to parse as python script
        encoding  (str): encoding of file

    Returns:
        str: parsed string

    """
    exporter = PythonExporter()
    (body, _) = exporter.from_filename(file_name)

    return body.encode(encoding)


def generate_requirements_file(path, imports, symbol):
    with _open(path, "w") as out_file:
        logging.debug(
            "Writing {num} requirements: {imports} to {file}".format(
                num=len(imports), file=path, imports=", ".join([x["name"] for x in imports])
            )
        )
        fmt = "{name}" + symbol + "{version}"
        out_file.write(
            "\n".join(
                fmt.format(**item) if item["version"] else "{name}".format(**item)
                for item in imports
            )
            + "\n"
        )


def output_requirements(imports, symbol):
    generate_requirements_file("-", imports, symbol)


def get_imports_info(imports, pypi_server="https://pypi.python.org/pypi/", proxy=None):
    result = []

    for item in imports:
        try:
            logging.warning(
                'Import named "%s" not found locally. ' "Trying to resolve it at the PyPI server.",
                item,
            )
            response = requests.get("{0}{1}/json".format(pypi_server, item), proxies=proxy)
            if response.status_code == 200:
                if hasattr(response.content, "decode"):
                    data = json2package(response.content.decode())
                else:
                    data = json2package(response.content)
            elif response.status_code >= 300:
                raise HTTPError(status_code=response.status_code, reason=response.reason)
        except HTTPError:
            logging.warning('Package "%s" does not exist or network problems', item)
            continue
        logging.warning(
            'Import named "%s" was resolved to "%s:%s" package (%s).\n'
            "Please, verify manually the final list of requirements.txt "
            "to avoid possible dependency confusions.",
            item,
            data.name,
            data.latest_release_id,
            data.pypi_url,
        )
        result.append({"name": item, "version": data.latest_release_id})
    return result


def get_locally_installed_packages(encoding="utf-8"):
    """Enhanced package detection supporting conda, editable installs, and namespace packages."""
    packages = []
    ignore = ["tests", "_tests", "egg", "EGG", "info"]
    
    # Get packages from multiple sources
    packages.extend(_get_pip_packages(encoding, ignore))
    packages.extend(_get_conda_packages(encoding, ignore))
    packages.extend(_get_editable_packages(encoding, ignore))
    packages.extend(_get_namespace_packages(encoding, ignore))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_packages = []
    for pkg in packages:
        pkg_key = (pkg["name"], tuple(sorted(pkg["exports"])))
        if pkg_key not in seen:
            seen.add(pkg_key)
            unique_packages.append(pkg)
    
    return unique_packages


def _get_pip_packages(encoding="utf-8", ignore=None):
    """Get packages from standard pip/setuptools installations."""
    if ignore is None:
        ignore = ["tests", "_tests", "egg", "EGG", "info"]
    
    packages = []
    for path in sys.path:
        if not os.path.exists(path):
            continue
            
        for root, dirs, files in os.walk(path):
            # Look for dist-info and egg-info directories
            if any(suffix in root for suffix in [".dist-info", ".egg-info"]):
                top_level_file = None
                metadata_file = None
                
                # Find top_level.txt and METADATA/PKG-INFO
                for item in files:
                    if "top_level" in item.lower():
                        top_level_file = os.path.join(root, item)
                    elif item in ["METADATA", "PKG-INFO"]:
                        metadata_file = os.path.join(root, item)
                
                if top_level_file:
                    try:
                        with open(top_level_file, "r", encoding=encoding) as f:
                            top_level_modules = [m.strip() for m in f.read().strip().split("\n") if m.strip()]
                    except (IOError, UnicodeDecodeError):
                        continue
                else:
                    # Fallback: infer from package name
                    package_name = os.path.basename(root).split("-")[0]
                    top_level_modules = [package_name.replace("_", "").replace("-", "")]
                
                # Extract package name and version
                package_parts = os.path.basename(root).split("-")
                package_name = package_parts[0]
                version = None
                
                if len(package_parts) > 1:
                    version = package_parts[1].replace(".dist", "").replace(".egg", "")
                
                # Try to get version from metadata if not found
                if not version and metadata_file:
                    version = _extract_version_from_metadata(metadata_file, encoding)
                
                # Filter modules
                filtered_modules = [
                    module for module in top_level_modules
                    if module and module not in ignore and package_name not in ignore
                ]
                
                if filtered_modules:
                    packages.append({
                        "name": package_name,
                        "version": version,
                        "exports": filtered_modules,
                    })
    
    return packages


def _get_conda_packages(encoding="utf-8", ignore=None):
    """Get packages from conda environments."""
    if ignore is None:
        ignore = ["tests", "_tests", "egg", "EGG", "info"]
    
    packages = []
    
    # Check if we're in a conda environment
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if not conda_prefix:
        return packages
    
    # Look for conda-meta directory
    conda_meta_path = os.path.join(conda_prefix, "conda-meta")
    if not os.path.exists(conda_meta_path):
        return packages
    
    try:
        import json
        
        for filename in os.listdir(conda_meta_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(conda_meta_path, filename), "r", encoding=encoding) as f:
                        conda_info = json.load(f)
                    
                    package_name = conda_info.get("name", "")
                    version = conda_info.get("version", "")
                    
                    if package_name in ignore:
                        continue
                    
                    # Try to map conda package to Python import name
                    import_names = _get_conda_import_mapping(package_name)
                    
                    if import_names:
                        packages.append({
                            "name": package_name,
                            "version": version,
                            "exports": import_names,
                        })
                        
                except (json.JSONDecodeError, IOError):
                    continue
                    
    except ImportError:
        # json module not available, skip conda detection
        pass
    
    return packages


def _get_editable_packages(encoding="utf-8", ignore=None):
    """Get editable/development packages from .egg-link files."""
    if ignore is None:
        ignore = ["tests", "_tests", "egg", "EGG", "info"]
    
    packages = []
    
    for path in sys.path:
        if not os.path.exists(path):
            continue
            
        for filename in os.listdir(path):
            if filename.endswith(".egg-link"):
                egg_link_path = os.path.join(path, filename)
                package_name = filename[:-9]  # Remove .egg-link
                
                if package_name in ignore:
                    continue
                
                try:
                    with open(egg_link_path, "r", encoding=encoding) as f:
                        dev_path = f.readline().strip()
                    
                    # Try to find setup.py or pyproject.toml for package info
                    setup_py = os.path.join(dev_path, "setup.py")
                    pyproject_toml = os.path.join(dev_path, "pyproject.toml")
                    
                    import_names = []
                    version = None
                    
                    if os.path.exists(setup_py):
                        import_names, version = _parse_setup_py(setup_py, package_name)
                    elif os.path.exists(pyproject_toml):
                        import_names, version = _parse_pyproject_toml(pyproject_toml, package_name)
                    
                    if not import_names:
                        # Fallback: use package name
                        import_names = [package_name.replace("-", "_")]
                    
                    packages.append({
                        "name": package_name,
                        "version": version,
                        "exports": import_names,
                    })
                    
                except (IOError, UnicodeDecodeError):
                    continue
    
    return packages


def _get_namespace_packages(encoding="utf-8", ignore=None):
    """Get namespace packages (PEP 420) that don't have __init__.py files."""
    if ignore is None:
        ignore = ["tests", "_tests", "egg", "EGG", "info"]
    
    packages = []
    
    for path in sys.path:
        if not os.path.exists(path):
            continue
            
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            # Check if it's a directory without __init__.py (namespace package)
            if (os.path.isdir(item_path) and 
                not os.path.exists(os.path.join(item_path, "__init__.py")) and
                item not in ignore and
                not item.startswith(".")):
                
                # Check if it contains Python files
                has_python_files = False
                for root, dirs, files in os.walk(item_path):
                    if any(f.endswith((".py", ".pyx")) for f in files):
                        has_python_files = True
                        break
                
                if has_python_files:
                    packages.append({
                        "name": item,
                        "version": None,
                        "exports": [item],
                    })
    
    return packages


def _extract_version_from_metadata(metadata_file, encoding="utf-8"):
    """Extract version from METADATA or PKG-INFO file."""
    try:
        with open(metadata_file, "r", encoding=encoding) as f:
            for line in f:
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except (IOError, UnicodeDecodeError):
        pass
    return None


def _get_conda_import_mapping(conda_package_name):
    """Map conda package names to Python import names."""
    # Common conda package mappings
    conda_mappings = {
        "numpy": ["numpy"],
        "pandas": ["pandas"],
        "scipy": ["scipy"],
        "matplotlib": ["matplotlib"],
        "scikit-learn": ["sklearn"],
        "pillow": ["PIL"],
        "opencv": ["cv2"],
        "pytorch": ["torch"],
        "tensorflow": ["tensorflow"],
        "beautifulsoup4": ["bs4"],
        "pyyaml": ["yaml"],
        "python-dateutil": ["dateutil"],
        "msgpack-python": ["msgpack"],
    }
    
    return conda_mappings.get(conda_package_name, [conda_package_name.replace("-", "_")])


def _parse_setup_py(setup_py_path, package_name):
    """Parse setup.py to extract package info (simplified)."""
    # This is a simplified parser - in practice, you'd want more robust parsing
    import_names = [package_name.replace("-", "_")]
    version = None
    
    try:
        with open(setup_py_path, "r") as f:
            content = f.read()
            
        # Look for version
        import re
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            
        # Look for packages
        packages_match = re.search(r'packages\s*=\s*\[([^\]]+)\]', content)
        if packages_match:
            packages_str = packages_match.group(1)
            packages_list = [p.strip().strip('"\'') for p in packages_str.split(',')]
            import_names = [p for p in packages_list if p]
            
    except (IOError, UnicodeDecodeError):
        pass
    
    return import_names, version


def _parse_pyproject_toml(pyproject_path, package_name):
    """Parse pyproject.toml to extract package info (simplified)."""
    import_names = [package_name.replace("-", "_")]
    version = None
    
    try:
        # Simple TOML parsing without external dependencies
        with open(pyproject_path, "r") as f:
            content = f.read()
            
        # Look for version in [tool.poetry] or [project] sections
        import re
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            
    except (IOError, UnicodeDecodeError):
        pass
    
    return import_names, version


def get_import_local(imports, encoding="utf-8"):
    local = get_locally_installed_packages()
    result = []
    for item in imports:
        # search through local packages
        for package in local:
            # if candidate import name matches export name
            # or candidate import name equals to the package name
            # append it to the result
            if item in package["exports"] or item == package["name"]:
                result.append(package)

    # removing duplicates of package/version
    # had to use second method instead of the previous one,
    # because we have a list in the 'exports' field
    # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    result_unique = [i for n, i in enumerate(result) if i not in result[n + 1:]]

    return result_unique


def get_transitive_dependencies(packages, max_depth=2):
    """
    Resolve transitive dependencies for the given packages.
    
    Args:
        packages: List of package dictionaries with 'name' and 'version'
        max_depth: Maximum depth to resolve dependencies (default: 2)
    
    Returns:
        List of additional packages that are transitive dependencies
    """
    if max_depth <= 0:
        return []
    
    transitive_deps = set()
    processed_packages = set()
    
    def _get_package_dependencies(package_name, current_depth=0):
        if current_depth >= max_depth or package_name in processed_packages:
            return
        
        processed_packages.add(package_name)
        
        try:
            # Try to get dependencies from local installation first
            deps = _get_local_dependencies(package_name)
            
            if not deps:
                # Fallback to PyPI metadata (limited to avoid too many requests)
                deps = _get_pypi_dependencies(package_name)
            
            for dep in deps:
                dep_name = dep.split()[0].split('=')[0].split('<')[0].split('>')[0].split('!')[0].split('~')[0]
                if dep_name and dep_name not in processed_packages:
                    transitive_deps.add(dep_name)
                    # Recursively get dependencies
                    _get_package_dependencies(dep_name, current_depth + 1)
                    
        except Exception as e:
            logging.debug(f"Failed to get dependencies for {package_name}: {e}")
    
    # Process each package
    for package in packages:
        _get_package_dependencies(package['name'])
    
    # Convert to package format and filter out already included packages
    existing_names = {pkg['name'] for pkg in packages}
    result = []
    
    for dep_name in transitive_deps:
        if dep_name not in existing_names:
            # Try to find version info
            local_packages = get_locally_installed_packages()
            version = None
            
            for local_pkg in local_packages:
                if local_pkg['name'] == dep_name:
                    version = local_pkg['version']
                    break
            
            result.append({
                'name': dep_name,
                'version': version
            })
    
    return result


def _get_local_dependencies(package_name):
    """Get dependencies from locally installed package metadata."""
    dependencies = []
    
    for path in sys.path:
        if not os.path.exists(path):
            continue
            
        # Look for package metadata
        for root, dirs, files in os.walk(path):
            if package_name.lower() in root.lower() and any(suffix in root for suffix in [".dist-info", ".egg-info"]):
                # Look for METADATA or requires.txt
                metadata_files = ["METADATA", "PKG-INFO", "requires.txt"]
                
                for metadata_file in metadata_files:
                    metadata_path = os.path.join(root, metadata_file)
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                
                            # Parse dependencies from metadata
                            if metadata_file in ["METADATA", "PKG-INFO"]:
                                dependencies.extend(_parse_metadata_dependencies(content))
                            elif metadata_file == "requires.txt":
                                dependencies.extend(_parse_requires_txt(content))
                                
                        except (IOError, UnicodeDecodeError):
                            continue
                            
                if dependencies:
                    break
    
    return dependencies


def _parse_metadata_dependencies(content):
    """Parse dependencies from METADATA or PKG-INFO content."""
    dependencies = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('Requires-Dist:'):
            dep = line.split(':', 1)[1].strip()
            # Remove environment markers like "; python_version >= '3.6'"
            dep = dep.split(';')[0].strip()
            if dep:
                dependencies.append(dep)
    
    return dependencies


def _parse_requires_txt(content):
    """Parse dependencies from requires.txt content."""
    dependencies = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            dependencies.append(line)
    
    return dependencies


def _get_pypi_dependencies(package_name):
    """Get dependencies from PyPI metadata (limited use to avoid rate limiting)."""
    dependencies = []
    
    try:
        import json
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            info = data.get('info', {})
            requires_dist = info.get('requires_dist', [])
            
            if requires_dist:
                for req in requires_dist:
                    # Remove environment markers
                    dep = req.split(';')[0].strip()
                    if dep:
                        dependencies.append(dep)
                        
    except Exception as e:
        logging.debug(f"Failed to get PyPI dependencies for {package_name}: {e}")
    
    return dependencies


def get_pkg_names(pkgs):
    """Get PyPI package names from a list of imports.

    Args:
        pkgs (List[str]): List of import names.

    Returns:
        List[str]: The corresponding PyPI package names.

    """
    result = set()
    with open(join("mapping"), "r") as f:
        data = dict(x.strip().split(":") for x in f)
    for pkg in pkgs:
        # Look up the mapped requirement. If a mapping isn't found,
        # simply use the package name.
        result.add(data.get(pkg, pkg))
    # Return a sorted list for backward compatibility.
    return sorted(result, key=lambda s: s.lower())


def get_name_without_alias(name):
    if "import " in name:
        match = REGEXP[0].match(name.strip())
        if match:
            name = match.groups(0)[0]
    return name.partition(" as ")[0].partition(".")[0].strip()


def join(f):
    return os.path.join(os.path.dirname(__file__), f)


def parse_requirements(file_):
    """Parse a requirements formatted file.

    Traverse a string until a delimiter is detected, then split at said
    delimiter, get module name by element index, create a dict consisting of
    module:version, and add dict to list of parsed modules.

    If file ´file_´ is not found in the system, the program will print a
    helpful message and end its execution immediately.

    Args:
        file_: File to parse.

    Raises:
        OSerror: If there's any issues accessing the file.

    Returns:
        list: The contents of the file, excluding comments.
    """
    modules = []
    # For the dependency identifier specification, see
    # https://www.python.org/dev/peps/pep-0508/#complete-grammar
    delim = ["<", ">", "=", "!", "~"]

    try:
        f = open(file_, "r")
    except FileNotFoundError:
        print(f"File {file_} was not found. Please, fix it and run again.")
        sys.exit(1)
    except OSError as error:
        logging.error(f"There was an error opening the file {file_}: {str(error)}")
        raise error
    else:
        try:
            data = [x.strip() for x in f.readlines() if x != "\n"]
        finally:
            f.close()

    data = [x for x in data if x[0].isalpha()]

    for x in data:
        # Check for modules w/o a specifier.
        if not any([y in x for y in delim]):
            modules.append({"name": x, "version": None})
        for y in x:
            if y in delim:
                module = x.split(y)
                module_name = module[0]
                module_version = module[-1].replace("=", "")
                module = {"name": module_name, "version": module_version}

                if module not in modules:
                    modules.append(module)

                break

    return modules


def compare_modules(file_, imports):
    """Compare modules in a file to imported modules in a project.

    Args:
        file_ (str): File to parse for modules to be compared.
        imports (tuple): Modules being imported in the project.

    Returns:
        set: The modules not imported in the project, but do exist in the
            specified file.
    """
    modules = parse_requirements(file_)

    imports = [imports[i]["name"] for i in range(len(imports))]
    modules = [modules[i]["name"] for i in range(len(modules))]
    modules_not_imported = set(modules) - set(imports)

    return modules_not_imported


def diff(file_, imports):
    """Display the difference between modules in a file and imported modules."""  # NOQA
    modules_not_imported = compare_modules(file_, imports)

    logging.info(
        "The following modules are in {} but do not seem to be imported: "
        "{}".format(file_, ", ".join(x for x in modules_not_imported))
    )


def clean(file_, imports):
    """Remove modules that aren't imported in project from file."""
    modules_not_imported = compare_modules(file_, imports)

    if len(modules_not_imported) == 0:
        logging.info("Nothing to clean in " + file_)
        return

    re_remove = re.compile("|".join(modules_not_imported))
    to_write = []

    try:
        f = open(file_, "r+")
    except OSError:
        logging.error("Failed on file: {}".format(file_))
        raise
    else:
        try:
            for i in f.readlines():
                if re_remove.match(i) is None:
                    to_write.append(i)
            f.seek(0)
            f.truncate()

            for i in to_write:
                f.write(i)
        finally:
            f.close()

    logging.info("Successfully cleaned up requirements in " + file_)


def dynamic_versioning(scheme, imports):
    """Enables dynamic versioning with <compat>, <gt> or <non-pin> schemes."""
    if scheme == "no-pin":
        imports = [{"name": item["name"], "version": ""} for item in imports]
        symbol = ""
    elif scheme == "gt":
        symbol = ">="
    elif scheme == "compat":
        symbol = "~="
    return imports, symbol


def handle_scan_noteboooks():
    if not scan_noteboooks:
        logging.info("Not scanning for jupyter notebooks.")
        return

    try:
        global PythonExporter
        from nbconvert import PythonExporter
    except ImportError:
        raise NbconvertNotInstalled()


def init(args):
    global scan_noteboooks
    encoding = args.get("--encoding")
    extra_ignore_dirs = args.get("--ignore")
    follow_links = not args.get("--no-follow-links")
    include_transitive = args.get("--include-transitive", False)
    transitive_depth = int(args.get("--transitive-depth") or 2)
    enhanced_detection = args.get("--enhanced-detection", False)

    scan_noteboooks = args.get("--scan-notebooks", False)
    handle_scan_noteboooks()

    input_path = args["<path>"]

    if encoding is None:
        encoding = "utf-8"
    if input_path is None:
        input_path = os.path.abspath(os.curdir)

    if extra_ignore_dirs:
        extra_ignore_dirs = extra_ignore_dirs.split(",")

    path = (
        args["--savepath"] if args["--savepath"] else os.path.join(input_path, "requirements.txt")
    )
    if (
        not args["--print"]
        and not args["--savepath"]
        and not args["--force"]
        and os.path.exists(path)
    ):
        logging.warning("requirements.txt already exists, " "use --force to overwrite it")
        return

    # Enhanced import detection
    if enhanced_detection:
        logging.info("Using enhanced detection for conda packages and dynamic imports")
    
    candidates = get_all_imports(
        input_path,
        encoding=encoding,
        extra_ignore_dirs=extra_ignore_dirs,
        follow_links=follow_links,
    )
    candidates = get_pkg_names(candidates)
    logging.debug("Found imports: " + ", ".join(candidates))
    
    pypi_server = "https://pypi.python.org/pypi/"
    proxy = None
    if args["--pypi-server"]:
        pypi_server = args["--pypi-server"]

    if args["--proxy"]:
        proxy = {"http": args["--proxy"], "https": args["--proxy"]}

    if args["--use-local"]:
        logging.debug("Getting package information ONLY from local installation.")
        imports = get_import_local(candidates, encoding=encoding)
    else:
        logging.debug("Getting packages information from Local/PyPI")
        local = get_import_local(candidates, encoding=encoding)

        # check if candidate name is found in
        # the list of exported modules, installed locally
        # and the package name is not in the list of local module names
        # it add to difference
        difference = [
            x
            for x in candidates
            if
            # aggregate all export lists into one
            # flatten the list
            # check if candidate is in exports
            x.lower() not in [y for x in local for y in x["exports"]] and
            # check if candidate is package names
            x.lower() not in [x["name"] for x in local]
        ]

        imports = local + get_imports_info(difference, proxy=proxy, pypi_server=pypi_server)
    
    # Add transitive dependencies if requested
    if include_transitive:
        logging.info(f"Resolving transitive dependencies (depth: {transitive_depth})")
        try:
            transitive_deps = get_transitive_dependencies(imports, max_depth=transitive_depth)
            if transitive_deps:
                logging.info(f"Found {len(transitive_deps)} transitive dependencies")
                imports.extend(transitive_deps)
            else:
                logging.info("No additional transitive dependencies found")
        except Exception as e:
            logging.warning(f"Failed to resolve transitive dependencies: {e}")
    
    # sort imports based on lowercase name of package, similar to `pip freeze`.
    imports = sorted(imports, key=lambda x: x["name"].lower())

    if args["--diff"]:
        diff(args["--diff"], imports)
        return

    if args["--clean"]:
        clean(args["--clean"], imports)
        return

    if args["--mode"]:
        scheme = args.get("--mode")
        if scheme in ["compat", "gt", "no-pin"]:
            imports, symbol = dynamic_versioning(scheme, imports)
        else:
            raise ValueError(
                "Invalid argument for mode flag, " "use 'compat', 'gt' or 'no-pin' instead"
            )
    else:
        symbol = "=="

    if args["--print"]:
        output_requirements(imports, symbol)
        logging.info("Successfully output requirements")
    else:
        generate_requirements_file(path, imports, symbol)
        logging.info("Successfully saved requirements file in " + path)


def main():  # pragma: no cover
    args = docopt(__doc__, version=__version__)
    log_level = logging.DEBUG if args["--debug"] else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    try:
        init(args)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()  # pragma: no cover
