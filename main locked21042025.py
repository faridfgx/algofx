import sys
import os
import datetime
import hashlib
import base64
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from algorithm_ide import AlgorithmIDE

# Import from the correct module
from real_time_execution import patch_real_time_execution, patched_execute
from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler

class SimpleExpirationChecker:
    def __init__(self):
        self.expiration_date = datetime.datetime(2025, 4, 22)
        self._config_file = self._get_config_path()
        
    def _get_config_path(self):
        """Get a suitable path for storing configuration data"""
        paths = [
            os.path.join(os.path.expanduser("~"), ".app_config"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "FxApp", "config.dat"),
            os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "fx_config.dat"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".app_data")
        ]
        
        # Try to use the first writable path
        for path in paths:
            try:
                dir_path = os.path.dirname(path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                # Test if we can write to this location
                with open(path, 'a+'):
                    return path
            except:
                continue
                
        # Fallback to current directory
        return ".app_data"
    
    def _encode_expiration(self):
        """Encode the expiration date with a simple obfuscation"""
        date_str = self.expiration_date.strftime("%Y%m%d")
        encoded = ""
        for char in date_str:
            encoded += chr(ord(char) + 5)  # Simple character shifting
        return base64.b64encode(encoded.encode()).decode()
    
    def _verify_integrity(self):
        """Verify the integrity of the application"""
        try:
            # Check if current date is before expiration date
            if datetime.datetime.now() > self.expiration_date:
                return False
                
            # Secondary check: look for stored expiration data
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    content = f.read().strip()
                    # If file exists but is empty or corrupted, create it
                    if not content:
                        self._write_verification_data()
                        return True
                    
                    # Check if the content matches our encoded expiration
                    parts = content.split('|')
                    if len(parts) != 2:
                        return False
                    
                    encoded_date, checksum = parts
                    expected_checksum = hashlib.md5(encoded_date.encode()).hexdigest()[:8]
                    
                    # If checksums don't match, the file was tampered with
                    if checksum != expected_checksum:
                        return False
                    
                    # Verify the encoded date matches our expiration date
                    expected_encoded = self._encode_expiration()
                    return encoded_date == expected_encoded
            else:
                # If config file doesn't exist, create it
                self._write_verification_data()
                return True
                
        except Exception:
            # Any exception is treated as a verification failure
            return False
            
        return True
    
    def _write_verification_data(self):
        """Write verification data to the config file"""
        try:
            encoded_date = self._encode_expiration()
            checksum = hashlib.md5(encoded_date.encode()).hexdigest()[:8]
            with open(self._config_file, 'w') as f:
                f.write(f"{encoded_date}|{checksum}")
            return True
        except:
            return False
    
    def is_valid(self):
        """Check if the application is still valid to run"""
        # Multiple checks for better protection
        time_check = datetime.datetime.now() <= self.expiration_date
        integrity_check = self._verify_integrity()
        
        # Both checks must pass
        return time_check and integrity_check

def show_expiration_message():
    """Show a message that the application has expired"""
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Application Expired")
    msg.setText("This application has expired.")
    msg.setInformativeText("Please download the latest version to continue using this application.")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def main():
    # Check if the application is still valid to run
    checker = SimpleExpirationChecker()
    
    if not checker.is_valid():
        show_expiration_message()
        sys.exit(0)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for modern look

    app.setWindowIcon(QIcon("fxlogo.png"))  # Set before creating any windows

    # Apply our real-time execution patch
    # Directly patch the execution method in FrenchAlgorithmCompiler class
    FrenchAlgorithmCompiler._original_execute = FrenchAlgorithmCompiler.execute
    FrenchAlgorithmCompiler.execute = patched_execute

    # Create the IDE instance
    ide = AlgorithmIDE()
    
    # Don't use PyQtInputFixer since we've implemented our own patching
    # ide.compiler = PyQtInputFixer.patch_compiler(ide.compiler)
    
    ide.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()