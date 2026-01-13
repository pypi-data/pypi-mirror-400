# Slurmfile Remaining Usage Report

This document tracks where the Slurmfile configuration abstraction is still used in the codebase.
The Slurmfile is an internal, private API that will be removed in a future release.

## Summary

The Slurmfile is a TOML configuration file that allows users to define cluster connection settings,
environments, and defaults. While it remains functional, it is considered internal infrastructure
and should not be documented in public-facing documentation.

## Files Using Slurmfile

### Core Configuration (`src/slurm/config.py`)
**Purpose:** Primary implementation of Slurmfile loading and parsing.

- `SlurmfileEnvironment` dataclass - resolved configuration for an environment
- `load_environment()` - loads and merges Slurmfile configuration
- `resolve_slurmfile_path()` - path resolution with discovery
- `discover_slurmfile()` - upward search for Slurmfile
- `_normalize_slurmfile_path()` - path normalization
- `_parse_slurmfile()` - TOML parsing
- `_resolve_environment()` - environment merging logic
- `_instantiate_callbacks()` - callback instantiation from config

**Status:** Internal API, not exported in public `__init__.py`

### Cluster (`src/slurm/cluster.py`)
**Purpose:** Uses Slurmfile for cluster construction and workflow support.

Key usages:
- `Cluster.from_env()` - constructs cluster from Slurmfile environment
- `_render_workflow_slurmfile()` - creates minimal Slurmfile for nested workflows
- `_handle_workflow_slurmfile()` - uploads Slurmfile to job directory for workflow execution
- `slurmfile_path` attribute - stores path to loaded Slurmfile
- Various error handling with `SlurmfileInvalidError`

**Status:** `from_env()` is public API but Slurmfile details are implementation

### Errors (`src/slurm/errors.py`)
**Purpose:** Defines Slurmfile-specific error classes.

- `SlurmfileError` - base class for Slurmfile errors
- `SlurmfileNotFoundError` - Slurmfile not found
- `SlurmfileInvalidError` - invalid TOML or schema
- `SlurmfileEnvironmentNotFoundError` - environment not in Slurmfile

**Status:** Exported in `__init__.py` for user error handling

### Runner (`src/slurm/runner.py`)
**Purpose:** Loads cluster from Slurmfile in remote job execution.

- Uses `SLURM_SDK_SLURMFILE` environment variable
- Loads cluster configuration for workflow child task submission

**Status:** Internal implementation detail

### Rendering (`src/slurm/rendering.py`)
**Purpose:** Exports Slurmfile path to job environment.

- Sets `SLURM_SDK_SLURMFILE` environment variable in job scripts

**Status:** Internal implementation detail

### Task (`src/slurm/task.py`)
**Purpose:** Error messages reference Slurmfile as a cause.

- Error messages mention "Slurmfile not found" as common cause

**Status:** User-facing error messages (acceptable)

### Examples (`src/slurm/examples/workflow_graph_visualization.py`)
**Purpose:** Example showing Slurmfile usage in CLI arguments.

- Docstring mentions `--slurmfile` argument

**Status:** Example code, mirrors Cluster.add_argparse_args() functionality

## Public API Exports

From `src/slurm/__init__.py`:
- `SlurmfileError` - base exception class

These remain exported for backwards compatibility with users catching these exceptions.

## Recommendations

1. **Do not add new Slurmfile documentation** to `docs/` directory
2. **Error classes remain exported** for exception handling compatibility
3. **from_env() remains public** but implementation details are internal
4. **Consider deprecation warnings** in future releases before removal
