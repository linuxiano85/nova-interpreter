from typing import Callable, Dict, Optional

class Tray:
    """
    System tray integration using PySide6.
    
    Note: This is a placeholder implementation. The actual implementation
    requires the PySide6 package which is only installed with [nova-prime] extras.
    """
    
    def __init__(self, app, translations: Dict[str, str], toggle_listen_cb: Callable, 
                 open_cb: Callable, quit_cb: Callable, is_listening_fn: Callable):
        self.app = app
        self.tr = translations
        self.toggle_listen_cb = toggle_listen_cb
        self.open_cb = open_cb
        self.quit_cb = quit_cb
        self._is_listening_fn = is_listening_fn
        
        # Try to import optional dependencies
        try:
            from PySide6.QtGui import QIcon, QAction
            from PySide6.QtWidgets import QSystemTrayIcon, QMenu
            
            self.icon = QIcon()  # TODO: set app icon
            self.tray = QSystemTrayIcon(self.icon)
            self.menu = QMenu()

            self.toggle_action = QAction(self.tr["tray.toggle_listen"])
            self.toggle_action.triggered.connect(toggle_listen_cb)
            self.menu.addAction(self.toggle_action)

            self.open_action = QAction(self.tr["tray.open"])
            self.open_action.triggered.connect(open_cb)
            self.menu.addAction(self.open_action)

            self.menu.addSeparator()
            self.quit_action = QAction(self.tr["tray.quit"])
            self.quit_action.triggered.connect(quit_cb)
            self.menu.addAction(self.quit_action)

            self.tray.setContextMenu(self.menu)
            self.tray.setToolTip(self.tr["tray.title"])
            self.tray.show()
            self.update()
            
        except ImportError:
            # PySide6 not available, create dummy tray
            self.tray = None
            self.toggle_action = None

    def update(self):
        if self.toggle_action:
            if self._is_listening_fn():
                self.toggle_action.setText(self.tr["tray.listen_on"])
            else:
                self.toggle_action.setText(self.tr["tray.listen_off"])