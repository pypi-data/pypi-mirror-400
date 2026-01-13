# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 0.8.0 - 2026-01-03

### Major Updates

- Updated JupyterLab core packages to 4.5+ (from 4.0)
  - `@jupyterlab/application`: ^4.0.0 → ^4.5.0
  - `@jupyterlab/apputils`: ^4.0.0 → ^4.6.0
  - `@jupyterlab/builder`: ^4.0.0 → ^4.5.0

### Development Dependencies

- **Breaking**: Migrated ESLint from v8 to v9 with flat config format
  - Created `eslint.config.mjs` using new flat config API
  - Updated `@typescript-eslint/*` packages to v8
  - Updated `eslint-config-prettier` to v10
- **Breaking**: Updated Stylelint from v15 to v16
  - Updated stylelint config packages to latest versions
  - Removed `stylelint-csstree-validator` (not compatible with Stylelint 16)
- Updated TypeScript from ~5.0.2 to ~5.9.0
  - Updated TypeScript target from ES2018 to ES2021
- Updated webpack loaders to latest major versions:
  - `css-loader`: ^6.7.1 → ^7.0.0
  - `source-map-loader`: ^1.0.2 → ^5.0.0
  - `style-loader`: ^3.3.1 → ^4.0.0
- Updated other dev dependencies:
  - `prettier`: ^3.0.0 → ^3.7.0
  - `@types/react`: ^18.0.26 → ^18.3.0
  - `yjs`: ^13.5.0 → ^13.6.0

### Python Support

- **Breaking**: Dropped Python 3.8 support (EOL October 2024)
- Updated minimum Python version from 3.8 to 3.9
- Added Python 3.14 to supported versions

### Build & CI/CD

- Fixed GitHub Actions workflow branch reference (main → master)
- Updated yarn.lock with all latest dependencies

### Code Quality

- Fixed all ESLint and Stylelint issues
- Formatted all code with Prettier
- Fixed CSS precision and formatting issues

<!-- <END NEW CHANGELOG ENTRY> -->

## 0.7.0

Add support for JupyterLab 4.x
