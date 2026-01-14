# Sifts

AI/ML based code analysis tool with YAML configuration support.

## Productive use case

Sifts runs on AWS batch against different groups and roots. This execution
is made through the `sifts` binary and requires `prod_sifts` access.

## Dev/validation use case

On the other hand, the `sifts-validation` binary provides a way to execute
a fully local analysis with development permissions, requiring either a root
directory argument or a config file path and failing if none of these is provided:

```bash
Usage: sifts-validation [OPTIONS] [WORKING_DIR]
Try 'sifts-validation --help' for help.

Error: Missing None working-dir or --config. Must specify either --config or working-dir argument
```

This will run the analysis on your local machine against a given code
repository, leaving behind a JSON sarif file with the results.

## Standalone use case

Same CLI underneath but this binary provides no service keys in the environment,
meaning you must set it yourself. To do this, you can create a `.env`
file with the required variables:

```bash
export OPENAI_API_KEY=...
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_ROLE=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_USER_PRIVATE_KEY=...
export VOYAGE_API_KEY=...
```

Such that after `source .env` you can run the standalone binary in the universe
root without requiring the development environment to be setup:

```bash
nix run --impure sifts/\#.sifts-standalone --config config.yaml
```

Or directly from latest trunk commit:

```bash
nix run --impure 'git+ssh://git@gitlab.com/fluidattacks/universe?shallow=1&ref=trunk&dir=sifts#sifts-standalone' --config config.yaml
```

### Configuration Format

The configuration file follows this structure:

```yaml
analysis:
  working_dir: "." # Working directory (must exist)
  include_files:
    - "src/**/*.py" # Glob patterns for files to include
  exclude_files:
    - "tests/**" # Glob patterns for files to exclude
  lines_to_check: # Specific lines to check in specific files (must exist)
    - file: "src/cli.py"
      lines: [12, 45, 78]
    - file: "src/config.py" # You can specify multiple files
      lines: [10, 20]
    - file: "src/cli.py" # Entries with the same file path will be merged
      lines: [100, 200] # Will be combined with the previous entry for src/cli.py
  include_vulnerabilities_subcategories:
    - "SQL Injection"
    - "Cross-Site Scripting"
    - "Command Injection"
  exclude_vulnerabilities: [] # Vulnerabilities subcategories to exclude
  use_default_exclude_files: true # Use default exclude files list
  split_subdirectories: true # Split subdirectories for analysis

output:
  path: "reports/sarif.json" # Output file path (directory will be created if needed)
```

## Line Merging

When multiple entries in `lines_to_check` reference the same file path,
they will be automatically merged into a single entry with the combined list
of line numbers. Duplicate line numbers are automatically removed, and the
final list is sorted in ascending order.

For example, the above configuration will result in the following after
processing:

```yaml
lines_to_check:
  - file: "src/cli.py"
    lines: [12, 45, 78, 100, 200] # Combined from both entries
  - file: "src/config.py"
    lines: [10, 20]
```

## Sarif file visualization

After producing a JSON sarif file from the local analysis, you can navigate the
findings within a vscode based IDE and the `ms-sarifvscode.sarif-viewer`
extension by simply opening your target repository on your editor, then toggling
the **SARIF Results Panel** and indicating the log file to the extension if
needed.

## Debug

You can check progress on the locally stored entities with the help of a
sqlite client. Sifts entities get stored in `sifts.db` as the cpgs, predictions
and analysis stages are executed, therefore you can run the client to check the
content of the `snippets`, `embeddings`, `predictions` and `analysis` as the
analysis goes:

```bash
sqlite3 sifts.db
> .mode column
> .headers on
```

`.mode column` and `.headers on ` help to enhance visualization.
Once your client is set, you can do your queries, like:

```sql
SELECT 'snippets' as table_name, COUNT(*) as count FROM snippets
UNION ALL
SELECT 'embeddings', COUNT(*) FROM embeddings
UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis;
```

Output:

```bash
table_name   count
-----------  -----
snippets     1190
embeddings   1072
predictions  1072
analysis     160
```

### Debug with debugpy

You can also run a complete debug from sifts subprocesses with the native
vscode debugging tool. Check launch.json for details. To achieve this, a
debugging shell with the proper direnv setup is needed, meaning the debug
may take long the first time as the dev shell is prepared, but will go faster
next times since the env is pre-built (as soon as the debug shell remains open).
