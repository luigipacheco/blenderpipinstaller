bl_info = {
    "name": "Pip Library Installer",
    "author": "Luis Pacheco",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Pip Installer",
    "description": "Install Python libraries via pip directly in Blender",
    "category": "Development",
}

import bpy
import subprocess
import sys
import os
import threading
from bpy.props import StringProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup

class PipInstallerProperties(PropertyGroup):
    library_name: StringProperty(
        name="Library Name",
        description="Name of the Python library to install",
        default=""
    )
    
    installing: BoolProperty(
        name="Installing",
        description="Installation in progress",
        default=False
    )
    
    last_result: StringProperty(
        name="Last Result",
        description="Result of last installation",
        default=""
    )
    
    library_installed: BoolProperty(
        name="Library Installed",
        description="Whether the library is currently installed",
        default=False
    )
    
    installed_version: StringProperty(
        name="Installed Version",
        description="Currently installed version of the library",
        default=""
    )

def get_python_executable():
    """Get the Python executable path for the current Blender installation"""
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    
    # On some systems, python.exe might be in Scripts folder
    if not os.path.exists(python_exe):
        python_exe = os.path.join(sys.prefix, 'Scripts', 'python.exe')
    
    # On Unix-like systems, it might just be 'python'
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    
    return python_exe

class PIP_OT_check_library(Operator):
    bl_idname = "pip.check_library"
    bl_label = "Check Library"
    bl_description = "Check if the specified library is installed"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.pip_installer_props
        library_name = props.library_name.strip()
        
        if not library_name:
            self.report({'ERROR'}, "Please enter a library name")
            return {'CANCELLED'}
        
        def check_thread():
            try:
                python_exe = get_python_executable()
                
                # Check if library is installed and get version
                result = subprocess.run([python_exe, "-m", "pip", "show", library_name], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # Parse version from output
                    version = "Unknown"
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                            break
                    
                    props.library_installed = True
                    props.installed_version = version
                    props.last_result = f"✓ {library_name} v{version} is installed"
                else:
                    props.library_installed = False
                    props.installed_version = ""
                    props.last_result = f"○ {library_name} is not installed"
                    
            except Exception as e:
                props.library_installed = False
                props.installed_version = ""
                props.last_result = f"✗ Error checking {library_name}: {str(e)}"
        
        thread = threading.Thread(target=check_thread)
        thread.daemon = True
        thread.start()
        
        return {'FINISHED'}

def get_python_executable():
    """Get the Python executable path for the current Blender installation"""
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    
    # On some systems, python.exe might be in Scripts folder
    if not os.path.exists(python_exe):
        python_exe = os.path.join(sys.prefix, 'Scripts', 'python.exe')
    
    # On Unix-like systems, it might just be 'python'
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    
    return python_exe

class PIP_OT_install_library(Operator):
    bl_idname = "pip.install_library"
    bl_label = "Install Library"
    bl_description = "Install the specified Python library"
    bl_options = {'REGISTER'}
    
    force_reinstall: BoolProperty(default=False)
    upgrade: BoolProperty(default=False)
    
    def execute(self, context):
        props = context.scene.pip_installer_props
        library_name = props.library_name.strip()
        
        if not library_name:
            self.report({'ERROR'}, "Please enter a library name")
            return {'CANCELLED'}
        
        if props.installing:
            self.report({'WARNING'}, "Installation already in progress")
            return {'CANCELLED'}
        
        # Start installation in background thread
        props.installing = True
        
        if self.force_reinstall:
            props.last_result = f"Reinstalling {library_name}..."
        elif self.upgrade:
            props.last_result = f"Upgrading {library_name}..."
        else:
            props.last_result = f"Installing {library_name}..."
        
        def install_thread():
            try:
                python_exe = get_python_executable()
                print(f"Using Python executable: {python_exe}")
                
                # Ensure pip is available
                subprocess.check_call([python_exe, "-m", "ensurepip", "--default-pip"], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Upgrade pip
                subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Build install command
                install_cmd = [python_exe, "-m", "pip", "install"]
                
                if self.force_reinstall:
                    install_cmd.extend(["--force-reinstall", "--no-deps"])
                elif self.upgrade:
                    install_cmd.append("--upgrade")
                
                install_cmd.append(library_name)
                
                # Install the requested library
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    action = "reinstalled" if self.force_reinstall else ("upgraded" if self.upgrade else "installed")
                    props.last_result = f"✓ Successfully {action} {library_name}"
                    print(f"Successfully {action} {library_name}")
                    
                    # Update installation status
                    props.library_installed = True
                    # Get new version info
                    version_result = subprocess.run([python_exe, "-m", "pip", "show", library_name], 
                                                  capture_output=True, text=True, timeout=30)
                    if version_result.returncode == 0:
                        for line in version_result.stdout.split('\n'):
                            if line.startswith('Version:'):
                                props.installed_version = line.split(':', 1)[1].strip()
                                break
                else:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    action = "reinstall" if self.force_reinstall else ("upgrade" if self.upgrade else "install")
                    props.last_result = f"✗ Failed to {action} {library_name}: {error_msg}"
                    print(f"Failed to {action} {library_name}: {error_msg}")
                    
            except subprocess.TimeoutExpired:
                props.last_result = f"✗ Installation of {library_name} timed out"
                print(f"Installation of {library_name} timed out")
            except Exception as e:
                props.last_result = f"✗ Error installing {library_name}: {str(e)}"
                print(f"Error installing {library_name}: {str(e)}")
            finally:
                props.installing = False
        
        # Start the installation thread
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
        return {'FINISHED'}

class PIP_OT_upgrade_pip(Operator):
    bl_idname = "pip.upgrade_pip"
    bl_label = "Upgrade Pip"
    bl_description = "Upgrade pip to the latest version"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.pip_installer_props
        
        if props.installing:
            self.report({'WARNING'}, "Installation already in progress")
            return {'CANCELLED'}
        
        props.installing = True
        props.last_result = "Upgrading pip..."
        
        def upgrade_thread():
            try:
                python_exe = get_python_executable()
                
                # Ensure pip and upgrade it
                subprocess.check_call([python_exe, "-m", "ensurepip", "--default-pip"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                result = subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                                      capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    props.last_result = "✓ Successfully upgraded pip"
                    print("Successfully upgraded pip")
                else:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    props.last_result = f"✗ Failed to upgrade pip: {error_msg}"
                    print(f"Failed to upgrade pip: {error_msg}")
                    
            except Exception as e:
                props.last_result = f"✗ Error upgrading pip: {str(e)}"
                print(f"Error upgrading pip: {str(e)}")
            finally:
                props.installing = False
        
        thread = threading.Thread(target=upgrade_thread)
        thread.daemon = True
        thread.start()
        
        return {'FINISHED'}

class PIP_PT_installer_panel(Panel):
    bl_label = "Pip Library Installer"
    bl_idname = "PIP_PT_installer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pip Installer"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.pip_installer_props
        
        # Library input
        col = layout.column(align=True)
        col.label(text="Python Library:")
        
        row = col.row(align=True)
        row.prop(props, "library_name", text="")
        
        # Check button
        check_row = row.row(align=True)
        if props.installing:
            check_row.enabled = False
        check_row.operator("pip.check_library", text="", icon='VIEWZOOM')
        
        # Show installation status if library is checked
        if props.library_name.strip() and props.last_result and not props.installing:
            if props.library_installed:
                status_box = layout.box()
                status_box.label(text=f"✓ {props.library_name} v{props.installed_version}", icon='CHECKMARK')
                
                # Options for installed library
                row = status_box.row(align=True)
                row.scale_y = 0.8
                
                upgrade_op = row.operator("pip.install_library", text="Upgrade", icon='FILE_REFRESH')
                upgrade_op.upgrade = True
                
                reinstall_op = row.operator("pip.install_library", text="Reinstall", icon='RECOVER_LAST')
                reinstall_op.force_reinstall = True
                
                if props.installing:
                    row.enabled = False
            else:
                # Library not installed - show install button
                col = layout.column(align=True)
                if props.installing:
                    col.enabled = False
                    col.operator("pip.install_library", text="Installing...", icon='TIME')
                else:
                    col.operator("pip.install_library", text="Install Library", icon='IMPORT')
        else:
            # Default install button when no check has been done
            col = layout.column(align=True)
            if props.installing:
                col.enabled = False
                col.operator("pip.install_library", text="Installing...", icon='TIME')
            else:
                col.operator("pip.install_library", text="Install Library", icon='IMPORT')
        
        # Utility buttons
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Utilities:")
        
        row = col.row(align=True)
        if props.installing:
            row.enabled = False
        row.operator("pip.upgrade_pip", text="Upgrade Pip", icon='FILE_REFRESH')
        
        # Status display
        if props.last_result:
            layout.separator()
            box = layout.box()
            box.label(text="Status:", icon='INFO')
            
            # Split long messages into multiple lines
            result_text = props.last_result
            max_chars = 35
            if len(result_text) > max_chars:
                words = result_text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    if len(current_line + word) > max_chars:
                        if current_line:
                            lines.append(current_line.strip())
                            current_line = word + " "
                        else:
                            lines.append(word)
                            current_line = ""
                    else:
                        current_line += word + " "
                
                if current_line:
                    lines.append(current_line.strip())
                
                for line in lines:
                    box.label(text=line)
            else:
                box.label(text=result_text)
        
        # Instructions
        layout.separator()
        box = layout.box()
        box.label(text="Instructions:", icon='QUESTION')
        box.label(text="1. Enter library name (e.g., 'numpy')")
        box.label(text="2. Click check button to verify status")
        box.label(text="3. Install/Upgrade/Reinstall as needed")
        box.label(text="4. Restart Blender to use the library")

# Registration
classes = [
    PipInstallerProperties,
    PIP_OT_check_library,
    PIP_OT_install_library,
    PIP_OT_upgrade_pip,
    PIP_PT_installer_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.pip_installer_props = bpy.props.PointerProperty(type=PipInstallerProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.pip_installer_props

if __name__ == "__main__":
    register()