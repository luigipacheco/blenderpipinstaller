# Pip Library Installer for Blender

A Blender add-on that allows you to install, manage, and uninstall Python libraries directly within Blender using pip.

## Features

- Install Python libraries via pip directly in Blender
- Check library installation status and version
- Upgrade existing libraries
- Force reinstall libraries if needed
- Uninstall libraries
- Upgrade pip itself
- User-friendly interface in the Text Editor sidebar
- Real-time status updates
- Detailed error reporting

## Requirements

- Blender 4.2.0 or newer
- Internet connection for downloading packages

## Installation

1. In Blender, go to Edit > Preferences > Add-ons
2. Click "Install..." and select the downloaded zip file
3. Enable the add-on by checking the box next to "Pip Library Installer"

## Usage

1. Open the Text Editor in Blender
2. Look for the "Pip Installer" tab in the sidebar
3. Enter the name of the Python library you want to install (e.g., "numpy")
4. Click the magnifying glass icon to check if the library is already installed
5. Use the appropriate button to:
   - Install a new library
   - Upgrade an existing library
   - Force reinstall a library
   - Uninstall a library
6. Check the status box for operation results
7. Restart Blender to use the newly installed library

## Common Operations

### Installing a Library
1. Enter the library name
2. Click "Install Library"
3. Wait for the installation to complete
4. Check the status for success or error messages

### Upgrading a Library
1. Enter the library name
2. Click the check button to verify it's installed
3. Click "Upgrade" to update to the latest version

### Uninstalling a Library
1. Enter the library name
2. Click the check button to verify it's installed
3. Click "Uninstall" to remove the library

### Upgrading Pip
1. Click the "Upgrade Pip" button in the Utilities section
2. Wait for the upgrade to complete
3. Check the status for success or error messages

## Troubleshooting

### Installation Hangs
- Check your internet connection
- Try upgrading pip first
- Check if the library name is correct
- Try force reinstalling the library

### Library Not Found
- Verify the library name is correct
- Check if the library is available on PyPI
- Try installing with a specific version (e.g., "numpy==1.21.0")

### Permission Errors
- Run Blender as administrator
- Check if the Python environment is writable
- Verify you have sufficient disk space

## Notes

- Some libraries may require additional system dependencies
- Large libraries may take longer to install
- Always restart Blender after installing new libraries
- The add-on requires an internet connection to download packages



## Author

Luis Pacheco 
