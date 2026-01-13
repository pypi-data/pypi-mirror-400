# vyre

**vyre** is a Python-based application runner and package manager.
It allows you to build, install, run, list, export, verify, and uninstall self-contained applications packaged as `.vy` files.

Version: **0.2.0**

---

## Features

- Build applications into a single `.vy` package
- Install and uninstall applications locally
- Run applications by package name, app name, directory, or `.vy` file
- Isolated runtime environment (applications only see their own `content/` directory)
- Manifest-based configuration using `build.json`
- Deterministic builds and installs with controlled timing
- Uses only the Python standard library

---

## Application Structure

A vyre application must follow this structure:

MyApp/
├── content/
│   ├── main.py
│   └── other_files.py
├── build.json
├── README.md        (optional)
└── LICENSE          (optional)

---

## Rules

- `content/` is the runtime root of the application
- Only files inside `content/` are visible at runtime
- The entry file must exist inside `content/`

---

## build.json Format

Example:

{
  "author": "john",
  "app_name": "helloapp",
  "version": "1.0.0",
  "entry_file": "main.py",
  "deps": ["colorama"],
  "readme": "README.md",
  "license": "LICENSE"
}

---

## Required fields

- author
- app_name
- version
- entry_file

---

## Optional fields

- deps  
  A list of Python package dependencies required by the application.
  These are standard pip package names.

Example:

"deps": ["colorama", "requests"]

---

## Automatically generated

- package_name: vyre.<author>.<app_name>

---

## Commands

Build an application

vyre build MyApp/ --verbose

Creates a `.vy` file in the current directory.

---

Install a package

vyre install vyre.john.helloapp-1.0.0.vy

Installed location:

~/.local/share/vyre/vyre.john.helloapp/

---

Run an application

vyre run vyre.john.helloapp
vyre run helloapp
vyre run path/to/app/
vyre run app.vy

Arguments after the application name are passed directly to the application.

---

List installed applications

vyre list

Output format:

package_name - app_name - version - author

---

Application information

vyre info vyre.john.helloapp

Displays metadata including version, author, entry file, and timestamps.

---

Uninstall an application

vyre uninstall vyre.john.helloapp

---

Verify a package

vyre verify app.vy

Validates package structure and metadata.

---

Export an installed application

vyre export vyre.john.helloapp

Creates a `.vy` file from an installed application.

---

Version

vyre version

---

Runtime Isolation

- Applications run with `content/` as the working directory
- PYTHONPATH is set so imports resolve only inside the application
- Applications cannot access files outside their own package by default

---

License

Please read the LICENSE file before using this.