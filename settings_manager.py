import json
import os
import sys
import traceback
from PyQt5.QtCore import QSettings

class SettingsManager:
    def __init__(self, app_name="AlgoFX"):
        self.app_name = app_name
        self.qsettings = QSettings(app_name, app_name)
        
        # Determine correct base path for the settings file
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        self.json_file_path = os.path.join(base_path, "settings.json")
        print(f"Settings file path: {self.json_file_path}")
        print(f"Path exists: {os.path.exists(self.json_file_path)}")
        
        # Try to create a writeable settings directory
        self.user_data_dir = os.path.join(os.path.expanduser("~"), f".{app_name}")
        if not os.path.exists(self.user_data_dir):
            try:
                os.makedirs(self.user_data_dir)
                print(f"Created user data directory: {self.user_data_dir}")
            except Exception as e:
                print(f"Failed to create user data directory: {e}")
        
        # Always use a writeable location for the "expired" flag
        self.user_settings_path = os.path.join(self.user_data_dir, "settings_applied.json")
        
    def load_initial_settings(self):
        """
        Load settings from JSON file if it exists and hasn't been processed yet
        Returns True if settings were loaded from JSON, False otherwise
        """
        # First check if we've already applied settings
        if os.path.exists(self.user_settings_path):
            try:
                with open(self.user_settings_path, 'r') as f:
                    user_data = json.load(f)
                    if user_data.get("settings_applied", False):
                        print("Settings were already applied (user data record)")
                        return False
            except Exception as e:
                print(f"Error reading user settings state: {e}")
                
        # Check if JSON file exists
        if not os.path.exists(self.json_file_path):
            print(f"JSON settings file not found: {self.json_file_path}")
            return False
            
        try:
            # Print raw file contents for debugging
            print(f"Attempting to read settings file: {self.json_file_path}")
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                raw_content = file.read()
                print(f"Raw file contents: {raw_content}")
                
            # Load the JSON file
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                print("Successfully opened settings file")
                settings_data = json.load(file)
                print(f"Loaded settings data: {settings_data}")
                
            # Apply each setting from the JSON to QSettings
            if "error_language" in settings_data:
                language = settings_data["error_language"]
                # Convert language format if needed
                ui_language = "العربية" if language.lower() == "arabic" else "Français"
                param_language = "arabic" if language.lower() == "arabic" else "french"
                
                self.qsettings.setValue("error_language", ui_language)
                self.qsettings.setValue("error_language_param", param_language)
                print(f"Set language to {ui_language} ({param_language})")
                
            if "autocomplete_enabled" in settings_data:
                self.qsettings.setValue("autocomplete_enabled", settings_data["autocomplete_enabled"])
                print(f"Set autocomplete to {settings_data['autocomplete_enabled']}")
                
            if "input_type" in settings_data:
                # Convert "console" or "window" to 1 or 2
                input_type = 1 if settings_data["input_type"].lower() == "console" else 2
                self.qsettings.setValue("input_type", input_type)
                print(f"Set input type to {input_type} ({settings_data['input_type']})")
                
            if "dark_mode" in settings_data:
                self.qsettings.setValue("dark_mode", settings_data["dark_mode"])
                print(f"Set dark mode to {settings_data['dark_mode']}")
                
            # Sync QSettings to ensure values are saved
            self.qsettings.sync()
            
            # Mark settings as applied in user directory (which should be writeable)
            self._mark_as_applied()
            
            print("Successfully applied all settings")
            return True
            
        except Exception as e:
            print(f"Error loading settings from JSON: {str(e)}")
            traceback.print_exc()
            return False
        
    def _mark_as_applied(self):
        """Mark that settings have been applied in a user-writeable location"""
        try:
            # Write to user directory instead of bundle directory
            with open(self.user_settings_path, 'w') as file:
                json.dump({"settings_applied": True}, file)
                
            print(f"Marked settings as applied at {self.user_settings_path}")
            
            # Also try to mark the original file if possible
            try:
                if os.path.exists(self.json_file_path) and os.access(self.json_file_path, os.W_OK):
                    with open(self.json_file_path, 'r', encoding='utf-8') as file:
                        settings_data = json.load(file)
                    
                    settings_data["expired"] = True
                    
                    with open(self.json_file_path, 'w', encoding='utf-8') as file:
                        json.dump(settings_data, file, indent=4, ensure_ascii=False)
                    
                    print("Also marked original settings file as expired")
            except Exception as e:
                print(f"Could not modify original settings file (expected in PyInstaller): {e}")
                
        except Exception as e:
            print(f"Error marking settings as applied: {str(e)}")
            traceback.print_exc()

    def extract_and_expire_settings(self):
        """
        Extract settings from settings.json file and mark it as expired.
        This is useful when running the app for the first time.
        Returns a dictionary of the extracted settings or None if no settings were found.
        """
        # Check if settings were already applied
        if os.path.exists(self.user_settings_path):
            try:
                with open(self.user_settings_path, 'r') as f:
                    user_data = json.load(f)
                    if user_data.get("settings_applied", False):
                        print("Settings were already applied (user data record)")
                        return None
            except Exception as e:
                print(f"Error reading user settings state: {e}")
        
        # Check if JSON file exists
        if not os.path.exists(self.json_file_path):
            print(f"JSON settings file not found: {self.json_file_path}")
            return None
        
        try:
            # Load the JSON file
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                print("Successfully opened settings file")
                settings_data = json.load(file)
                print(f"Loaded settings data: {settings_data}")
            
            # Mark settings as applied
            self._mark_as_applied()
            
            print("Successfully extracted settings")
            return settings_data
            
        except Exception as e:
            print(f"Error extracting settings from JSON: {str(e)}")
            traceback.print_exc()
            return None