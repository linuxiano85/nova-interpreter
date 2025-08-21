import platform
import subprocess
import os
import shutil


class Os:
    def __init__(self, computer):
        self.computer = computer

    def get_selected_text(self):
        """
        Returns the currently selected text.
        """
        # Store the current clipboard content
        current_clipboard = self.computer.clipboard.view()
        # Copy the selected text to clipboard
        self.computer.clipboard.copy()
        # Get the selected text from clipboard
        selected_text = self.computer.clipboard.view()
        # Reset the clipboard to its original content
        self.computer.clipboard.copy(current_clipboard)
        return selected_text

    def notify(self, text):
        """
        Displays a notification on the computer.
        """
        try:
            title = "Open Interpreter"

            if len(text) > 200:
                text = text[:200] + "..."

            if "darwin" in platform.system().lower():  # Check if the OS is macOS
                text = text.replace('"', "'").replace("\n", " ")
                text = (
                    text.replace('"', "")
                    .replace("'", "")
                    .replace("“", "")
                    .replace("”", "")
                    .replace("<", "")
                    .replace(">", "")
                    .replace("&", "")
                )

                # Further sanitize the text to avoid errors
                text = text.encode("unicode_escape").decode("utf-8")

                ## Run directly
                script = f'display notification "{text}" with title "{title}"'
                subprocess.run(["osascript", "-e", script])

                # ## DISABLED OI-notifier.app
                # (This does not work. It makes `pip uninstall`` break for some reason!)

                # ## Use OI-notifier.app, which lets us use a custom icon

                # # Get the path of the current script
                # script_path = os.path.dirname(os.path.realpath(__file__))

                # # Write the notification text into notification_text.txt
                # with open(os.path.join(script_path, "notification_text.txt"), "w") as file:
                #     file.write(text)

                # # Construct the path to the OI-notifier.app
                # notifier_path = os.path.join(script_path, "OI-notifier.app")

                # # Call the OI-notifier
                # subprocess.run(["open", notifier_path])
            else:  # For other OS, use a general notification API
                try:
                    import plyer

                    plyer.notification.notify(title=title, message=text)
                except:
                    # Optional package
                    pass
        except Exception as e:
            # Notifications should be non-blocking
            if self.computer.verbose:
                print("Notification error:")
                print(str(e))

    def open_app(self, app_name: str):
        """
        Open a system application by name across operating systems.
        
        Args:
            app_name (str): Name of the application to open
            
        Returns:
            str: Status message indicating success or failure
        """
        try:
            system = platform.system().lower()
            if "darwin" in system:
                # macOS: use 'open -a "App Name"'
                subprocess.Popen(["open", "-a", app_name])
                return f"Launched {app_name}"
            elif "windows" in system:
                # Windows: use PowerShell Start-Process or cmd start
                cmd = [
                    "powershell", "-NoProfile", "-Command",
                    f"Start-Process -FilePath '{app_name}'"
                ]
                try:
                    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
                except Exception:
                    subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
                return f"Launched {app_name}"
            else:
                # Linux: try gtk-launch with .desktop ID, xdg-open if path, else PATH lookup
                desktop_id = app_name.lower().replace(" ", "-") + ".desktop"
                if shutil.which("gtk-launch"):
                    ret = subprocess.call(["gtk-launch", desktop_id])
                    if ret == 0:
                        return f"Launched {app_name}"
                if os.path.exists(app_name):
                    subprocess.Popen(["xdg-open", app_name])
                    return f"Launched {app_name}"
                exe = shutil.which(app_name)
                if exe:
                    subprocess.Popen([exe])
                    return f"Launched {app_name}"
            return f"Could not launch {app_name}"
        except Exception as e:
            return f"Error launching {app_name}: {e}"

    def open_steam_game(self, name_or_appid: str):
        """
        Open a Steam game by name (if installed) or appid.
        
        Args:
            name_or_appid (str): Game name or Steam AppID
            
        Returns:
            str: Status message indicating success or failure
        """
        try:
            # Try to use nova_prime services for enhanced Steam integration
            try:
                from nova_prime.services.steam import launch_game_by_name, launch_game_by_appid
                
                if name_or_appid.isdigit():
                    success = launch_game_by_appid(name_or_appid)
                    return f"Launched Steam game (AppID: {name_or_appid})" if success else f"Could not launch Steam game with AppID {name_or_appid}"
                else:
                    success = launch_game_by_name(name_or_appid)
                    return f"Launched Steam game '{name_or_appid}'" if success else f"Steam game '{name_or_appid}' not found"
                    
            except ImportError:
                # Fallback to basic implementation if nova_prime not available
                if name_or_appid.isdigit():
                    return self._launch_steam_by_appid(name_or_appid)
                else:
                    return f"Steam game launch by name requires Nova Prime package. Install with: pip install 'open-interpreter[nova-prime]'"
            
        except Exception as e:
            return f"Error launching Steam game '{name_or_appid}': {e}"
    
    def _launch_steam_by_appid(self, appid: str):
        """
        Launch a Steam game by AppID using steam:// protocol.
        
        Args:
            appid (str): Steam AppID
            
        Returns:
            str: Status message
        """
        try:
            system = platform.system().lower()
            steam_url = f"steam://rungameid/{appid}"
            
            if "darwin" in system:
                subprocess.Popen(["open", steam_url])
                return f"Launched Steam game (AppID: {appid})"
            elif "windows" in system:
                subprocess.Popen(["cmd", "/c", f"start {steam_url}"], shell=True)
                return f"Launched Steam game (AppID: {appid})"
            else:
                subprocess.Popen(["xdg-open", steam_url])
                return f"Launched Steam game (AppID: {appid})"
        except Exception as e:
            return f"Error launching Steam game with AppID {appid}: {e}"

    # Maybe run code should be here...?
