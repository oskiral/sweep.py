# sweep.py
Simple python script to tidy up folder.

**IMPORTANT** : By default the script ignores dotfiles (like ".env", ".gitignore") and doesn't move them anywhere.

## Usage

Sort the current folder where the script is located:
```bash
python sweep.py
```

Run in specific path:
```bash
python sweep.py path/to/directory
```

Get help:
```bash
python sweep.py --help
```

See what would happen without actually moving any files:
```bash
python sweep.py --dry-run path/to/directory
```

Create folder for dotfiles (like: .env, .gitignore):
```bash
python sweep.py --config path/to/directory
```

Ignore files that .gitignore contains:
```bash
python sweep.py --gitignore path/to/directory
```

Revert the last organization (undo file moves):
```bash
python sweep.py --undo path/to/directory
```

## TODO
- [x] Command Line Interface (CLI)
- [x] Dry Run Mode
- [x] Undo Feature
- [x] Config file
- [ ] Progress Bar Integration
- [ ] Sorting by Date Option

### This project uses only Python standard libraries.