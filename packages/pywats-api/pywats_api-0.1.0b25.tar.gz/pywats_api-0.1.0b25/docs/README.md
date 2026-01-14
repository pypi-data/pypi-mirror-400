# Documentation Folder Structure

This folder contains **official, user-facing documentation** that ships with `pip install pywats-api`.

## 📚 Published Documentation (in this folder)

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete installation, configuration, logging, and error handling guide

### Domain API Documentation
These files are included in the PyPI package:

- **[INDEX.md](INDEX.md)** - Documentation index and navigation
- **[PRODUCT.md](PRODUCT.md)** - Product domain API reference
- **[ASSET.md](ASSET.md)** - Asset domain API reference
- **[PRODUCTION.md](PRODUCTION.md)** - Production domain API reference
- **[REPORT.md](REPORT.md)** - Report domain API reference
- **[ANALYTICS.md](ANALYTICS.md)** - Analytics domain API reference
- **[SOFTWARE.md](SOFTWARE.md)** - Software domain API reference
- **[ROOTCAUSE.md](ROOTCAUSE.md)** - RootCause domain API reference
- **[PROCESS.md](PROCESS.md)** - Process domain API reference

### Module Usage Guides
Detailed guides with comprehensive examples:

- **[usage/](usage/)** - Legacy module guides (REPORT_MODULE.md, PRODUCT_MODULE.md, etc.)
  - Detailed usage patterns
  - Advanced examples
  - Factory method documentation

### Documentation Examples
Code snippets and examples embedded in documentation:

- **[examples/](examples/)** - Example code referenced in documentation
  - `basic_usage.py` - Getting started example

## 🔒 Internal Documentation (NOT published)

All internal documentation is in separate folders:

- **[internal/](internal/)** - Architecture, design docs, AI agent knowledge, internal guides
- **[archive/](archive/)** - Archived working notes and old documentation

**These folders are excluded from the pip package.**

## 📁 Folder Structure

```
docs/
├── INDEX.md              ✅ Published - Documentation index
├── README.md             ✅ Published - This file
├── PRODUCT.md            ✅ Published - Product domain
├── ASSET.md              ✅ Published - Asset domain
├── PRODUCTION.md         ✅ Published - Production domain
├── REPORT.md             ✅ Published - Report domain
├── ANALYTICS.md          ✅ Published - Analytics domain
├── SOFTWARE.md           ✅ Published - Software domain
├── ROOTCAUSE.md          ✅ Published - RootCause domain
├── PROCESS.md            ✅ Published - Process domain
├── usage/                ✅ Published - Detailed module guides
│   ├── REPORT_MODULE.md
│   ├── PRODUCT_MODULE.md
│   ├── PRODUCTION_MODULE.md
│   └── ...
├── examples/             ✅ Published - Documentation examples
│   └── basic_usage.py
├── internal/             ❌ NOT Published - Internal docs
│   ├── ARCHITECTURE.md
│   ├── WATS_DOMAIN_KNOWLEDGE.md
│   ├── api_specs/
│   └── ...
└── archive/              ❌ NOT Published - Archived notes
    └── ...
```

## ✅ Rule of Thumb

- **Files/folders in `docs/` root** → Published with pip package
- **Folders: `usage/`, `examples/`** → Published (user-facing)
- **Folders: `internal/`, `archive/`** → NOT Published (GitHub only)

## 🔄 Moving Documents

When creating new documentation:

- **User-facing API docs** → Put directly in `docs/`
- **Detailed usage guides** → Put in `docs/usage/`
- **Documentation examples** → Put in `docs/examples/`
- **Internal architecture/design** → Put in `docs/internal/`
- **Obsolete working notes** → Move to `docs/archive/`

## 📦 Packaging

Controlled by `MANIFEST.in` in the project root:
- **Includes:** `docs/*.md`, `docs/usage/`, `docs/examples/`
- **Excludes:** `docs/internal/`, `docs/archive/`
