import os
import time
from typing import List, Optional

from PySide6 import QtCore, QtGui, QtWidgets
import json
import re
import html

from .db import connect, init_db, search, clear_all, delete_file, get_stats, DB_PATH
from .indexer import IndexerThread, _get_drives


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "supersearch_config.json")
BYTES_TO_MB = 1.0 / 1048576.0


class ResultsModel(QtGui.QStandardItemModel):
    def __init__(self):
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(["Name", "Path", "Ext", "Size(MB)", "Modified"])

    def load(self, rows: List[tuple], query: str = ""):
        IMG_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico'}
        VIDEO_EXTS = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v', 'mpg', 'mpeg', '3gp'}
        WORD_EXTS = {'doc', 'docx', 'docm', 'dot', 'dotx', 'dotm'}
        EXCEL_EXTS = {'xls', 'xlsx', 'xlsm', 'xlsb', 'xlt', 'xltx', 'xltm', 'csv'}
        PPT_EXTS = {'ppt', 'pptx', 'pptm', 'pot', 'potx', 'potm', 'pps', 'ppsx', 'ppsm'}
        CODE_EXTS = {'py', 'js', 'ts', 'java', 'c', 'cpp', 'cc', 'h', 'hpp', 'cs', 'go', 'rs', 'php', 'rb', 'html', 'css', 'json', 'xml', 'yaml', 'yml', 'sql', 'sh', 'bat', 'ps1', 'lua', 'pl', 'swift', 'kt'}

        self.setRowCount(0)
        for r in rows:
            name, path, dir, ext, size, mtime, is_dir = r
            size_mb = (size * BYTES_TO_MB) if size is not None else None
            if query:
                name_esc = html.escape(name)
                q_esc = html.escape(query)
                pattern = re.compile(re.escape(q_esc), re.IGNORECASE)
                name_html = pattern.sub(lambda m: f'<span style="background-color:#fff59d">{m.group(0)}</span>', name_esc)
            else:
                name_html = html.escape(name)
            name_item = QtGui.QStandardItem()
            name_item.setData(name_html, QtCore.Qt.DisplayRole)

            path_item = QtGui.QStandardItem(path)
            path_item.setForeground(QtGui.QBrush(QtGui.QColor("#666666")))
            path_item.setToolTip(path)

            ext_text = "Folder" if is_dir else ext or ""
            ext_item = QtGui.QStandardItem(ext_text)
            if is_dir:
                ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#2979ff")))  # Blue for folders
            elif ext:
                ext_lower = ext.lower()
                if ext_lower in IMG_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#8bc34a")))  # Light green for images
                elif ext_lower in VIDEO_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#e91e63")))  # Pink for videos
                elif ext_lower in WORD_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#2b579a")))  # Word Blue
                elif ext_lower in EXCEL_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#217346")))  # Excel Green
                elif ext_lower in PPT_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#d24726")))  # PowerPoint Red
                elif ext_lower in CODE_EXTS:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#9c27b0")))  # Purple for source code
                else:
                    ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#555555")))  # Dark grey for files
            else:
                ext_item.setForeground(QtGui.QBrush(QtGui.QColor("#555555")))  # Dark grey for files

            items = [
                name_item,
                path_item,
                ext_item,
                QtGui.QStandardItem(f"{size_mb:.2f}" if size_mb is not None else ""),
                QtGui.QStandardItem(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)) if mtime else ""),
            ]
            for it in items:
                it.setEditable(False)
            self.appendRow(items)


class MainWindow(QtWidgets.QMainWindow):
    reindex_finished = QtCore.Signal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.reindex_finished.connect(self.on_reindex_finished)
        self.setWindowTitle("SuperSearch")
        self.resize(1000, 600)

        self.conn = connect()
        init_db(self.conn)

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Type to search…")
        self.search_edit.textChanged.connect(self.on_query_changed)

      

        # Menu Bar
        menubar = QtWidgets.QMenuBar()
        index_menu = menubar.addMenu("Index")
        help_menu = menubar.addMenu("Help")
        help_act = help_menu.addAction("About")
        help_act.triggered.connect(self.on_about)   
        
        # add_dir_act = index_menu.addAction("Add Index Dir")
        # add_dir_act.triggered.connect(self.on_add_dir)
        
        # clear_dirs_act = index_menu.addAction("Clear Dirs")
        # clear_dirs_act.triggered.connect(self.on_clear_dirs)
        
        config_act = index_menu.addAction("Index Dirs…")
        config_act.triggered.connect(self.on_config_index_dirs)

        self.reindex_btn = index_menu.addAction("Reindex")
        self.reindex_btn.triggered.connect(self.on_reindex)
        self.stats_btn = index_menu.addAction("Storage Stats")
        self.stats_btn.triggered.connect(self.on_stats)

        self.roots_label = QtWidgets.QLabel("")
        self.roots_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.roots_label.installEventFilter(self)

        self.status_bar = self.statusBar()
        self.setAcceptDrops(True)

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_open_item)
        self.model = ResultsModel()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.setColumnWidth(0, 200)
        self.table.setItemDelegateForColumn(0, HtmlDelegate(self.table))
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)

        top_bar = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top_bar)
        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(self.roots_label)

        # process_bar = QtWidgets.QWidget()
        self.process_bar = QtWidgets.QProgressBar()
        self.process_bar.setRange(0, 100)
        self.process_bar.setTextVisible(False)
        self.process_bar.setValue(0)
        self.process_bar.setFixedHeight(3)  # Make it thin

        self.setMenuBar(menubar)
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        v.setContentsMargins(1, 1, 1, 1)
        v.addWidget(self.process_bar)
        v.addWidget(top_bar)
        v.addWidget(self.table)
        self.setCentralWidget(central)

        self.indexer: Optional[IndexerThread] = None
        self.roots: List[str] = []

        self.status_bar.showMessage("Ready")
        self.load_roots()
        self.update_roots_label()

    def on_query_changed(self, text: str):
        rows = search(self.conn, text, limit=1000)
        self.model.load(rows, text)
        self.status_bar.showMessage(f"{len(rows)} results")

    def on_reindex(self):
        if self.indexer and self.indexer.is_alive():
            return
        self.status_bar.showMessage("Indexing…")
        self.reindex_btn.setEnabled(False)
        
        # Close connection and delete DB file for fresh start
        try:
            self.conn.close()
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
        except Exception:
            pass
            
        # Re-initialize DB
        self.conn = connect()
        init_db(self.conn)

        roots = self.roots if self.roots else None
        self.process_bar.setRange(0,0)
        self.process_bar.setValue(0)
        self.indexer = IndexerThread(roots=roots, on_done=self.reindex_finished.emit)
        self.indexer.start()

    def on_reindex_finished(self, total: int, dur: float):
        self.process_bar.setRange(0, 100)
        self.process_bar.setValue(100)
        self.reindex_btn.setEnabled(True)
        self.status_bar.showMessage(f"Indexed {total} files in {dur:.1f}s")
        # Refresh results for current query
        self.on_query_changed(self.search_edit.text())

    def current_row_path(self, index: QtCore.QModelIndex) -> Optional[str]:
        if not index.isValid():
            return None
        row = index.row()
        path_index = self.model.index(row, 1)
        return self.model.data(path_index)

    def on_open_item(self, index: QtCore.QModelIndex):
        path = self.current_row_path(index)
        if path and os.path.exists(path):
            os.startfile(path)

    def on_context_menu(self, pos):
        idx = self.table.indexAt(pos)
        path = self.current_row_path(idx)
        if not path:
            return
        menu = QtWidgets.QMenu(self)
        open_file = menu.addAction("Open")
        open_folder = menu.addAction("Open containing folder")
        menu.addSeparator()
        copy_fullpath = menu.addAction("Copy full path")
        copy_fullname = menu.addAction("Copy file name")
        menu.addSeparator()
        # transcode_action = menu.addAction("Convert to UTF-8")
        # delete_action = menu.addAction("Delete")
        
        act = menu.exec(self.table.viewport().mapToGlobal(pos))
        if act == open_file:
            self.on_open_item(idx)
        elif act == open_folder:
            folder = os.path.dirname(path)
            if os.path.isdir(folder):
                os.startfile(folder)
        elif act == copy_fullpath:
            QtGui.QGuiApplication.clipboard().setText(path)
            self.status_bar.showMessage("Copied full path")
        elif act == copy_fullname:
            QtGui.QGuiApplication.clipboard().setText(os.path.basename(path))
            self.status_bar.showMessage("Copied file name")
        elif act == transcode_action:
            self.transcode_item(path)
        elif act == delete_action:
            self.delete_item(idx, path)

    def transcode_item(self, path: str):
        """Attempts to convert a text file to UTF-8."""
        if os.path.isdir(path):
            QtWidgets.QMessageBox.warning(self, "Invalid Operation", "Cannot transcode a directory.")
            return

        # Simple heuristic to detect if binary
        try:
            with open(path, "rb") as f:
                raw = f.read(8192)
            if b"\0" in raw:
                QtWidgets.QMessageBox.warning(self, "Invalid Operation", "File appears to be binary.")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return

        # Attempt to decode with common encodings
        encodings = ["utf-8", "gb18030", "cp1252", "shift_jis", "big5", "latin1"]
        content = None
        detected = None
        
        # Re-read full content
        try:
            with open(path, "rb") as f:
                raw_full = f.read()
            
            for enc in encodings:
                try:
                    content = raw_full.decode(enc)
                    detected = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                QtWidgets.QMessageBox.warning(self, "Failed", "Could not detect text encoding.")
                return
            
            # Write back as utf-8
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.status_bar.showMessage(f"Converted from {detected} to UTF-8")
            QtWidgets.QMessageBox.information(self, "Success", f"File converted to UTF-8.\n(Detected source: {detected})")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to transcode:\n{e}")

    def delete_item(self, index: QtCore.QModelIndex, path: str):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Delete File")
        msg.setText(f"Are you sure you want to permanently delete:\n{path}?")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        
        if msg.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                # Remove from DB
                delete_file(self.conn, path)
                
                # Remove from View
                self.model.removeRow(index.row())
                self.status_bar.showMessage("Deleted")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete:\n{e}")

    def on_add_dir(self):
        dlg = QtWidgets.QFileDialog(self, "Choose index directory")
        dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dlg.setOption(QtWidgets.QFileDialog.Option.ShowDirsOnly, True)
        dlg.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        if dlg.exec():
            sel = dlg.selectedFiles()
            changed = False
            for p in sel:
                if p and p not in self.roots:
                    self.roots.append(p)
                    changed = True
            if changed:
                self.update_roots_label()
                self.save_roots()
                self.on_reindex()

    def on_clear_dirs(self):
        if self.roots:
            self.roots = []
            self.update_roots_label()
            self.save_roots()
            self.on_reindex()

    def update_roots_label(self):
        if not self.roots:
            full_text = "None index"
        else:
            shown = ", ".join(self.roots[:3])
            more = len(self.roots) - 3
            if more > 0:
                full_text = f"Roots: {shown} (+{more})"
            else:
                full_text = f"Roots: {shown}"
        
        fm = QtGui.QFontMetrics(self.roots_label.font())
        elided = fm.elidedText(full_text, QtCore.Qt.TextElideMode.ElideRight, 100)
        self.roots_label.setText(elided)
        # Set full text as tooltip just in case, though we have a click handler too
        self.roots_label.setToolTip(full_text)

    def load_roots(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                roots = data.get("roots") or []
                if isinstance(roots, list):
                    self.roots = [str(p) for p in roots if isinstance(p, str)]
        except Exception:
            pass

    def save_roots(self):
        try:
            data = {"roots": self.roots}
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_config_index_dirs(self):
        dlg = IndexDirsDialog(self.roots, self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_roots = dlg.roots()
            if new_roots != self.roots:
                self.roots = new_roots
                self.update_roots_label()
                self.save_roots()
                self.on_reindex()

    def on_stats(self):
        dlg = StorageStatsDialog(self.conn, self)
        dlg.exec()

    def on_about(self):
        copyright_text = """
        <hr>
        <p style='font-size:10px; color:#666;'>
        <b>Third Party Licenses:</b><br>
        This program uses PySide6 (LGPLv3).<br>
        PySide6 Copyright: <a href='https://www.qt.io/'>https://www.qt.io/</a><br>
        LGPLv3 License: <a href='https://www.gnu.org/licenses/lgpl-3.0.txt'>https://www.gnu.org/licenses/lgpl-3.0.txt</a><br>
        PySide6 Source: <a href='https://code.qt.io/cgit/pyside/pyside6.git/'>https://code.qt.io/cgit/pyside/pyside6.git/</a>
        </p>
        """
        QtWidgets.QMessageBox.about(
            self,
            "About SuperSearch",
            "<h3>SuperSearch</h3>"
            "<p>A fast local file search tool powered by Python and Qt.</p>"
            "<p>Version: 2026.1.4</p>"
            "<p>License: MIT</p>"
            "<p>Author: Ke Yingjie</p>"
            "<p>Email: yingjieke@gmail.com</p>"
            f"{copyright_text}"
        )

    def eventFilter(self, obj, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        added = False
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                # normalize path separators
                path = os.path.normpath(path)
                if path not in self.roots:
                    self.roots.append(path)
                    added = True
        if added:
            self.update_roots_label()
            self.save_roots()
            self.status_bar.showMessage("Folders added to index")
            self.on_reindex()

    def eventFilter(self, obj, event):
        if obj is self.roots_label and event.type() == QtCore.QEvent.MouseButtonRelease:
            text = self.roots_info_text()
            pos = self.roots_label.mapToGlobal(QtCore.QPoint(0, self.roots_label.height()))
            QtWidgets.QToolTip.showText(pos, text, self.roots_label)
            return True
        return super().eventFilter(obj, event)

    def roots_info_text(self) -> str:
        if not self.roots:
            return "Roots: Auto (fixed drives)"
        shown = "\n".join(self.roots)
        return f"Index Directories:\n{shown}"

class HtmlDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        doc = QtGui.QTextDocument()
        doc.setHtml(index.data())
        doc.setTextWidth(option.rect.width())
        painter.translate(option.rect.topLeft())
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        doc = QtGui.QTextDocument()
        doc.setHtml(index.data())
        doc.setTextWidth(option.rect.width())
        size = doc.size().toSize()
        return size
class IndexDirsDialog(QtWidgets.QDialog):
    def __init__(self, roots: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Index Directories")
        self.resize(600, 400)
        self.setAcceptDrops(True)
        self.list = QtWidgets.QListWidget()
        self.list.addItems(roots)
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        add_btn = QtWidgets.QPushButton("Add…")
        remove_btn = QtWidgets.QPushButton("Remove")
        clear_btn = QtWidgets.QPushButton("Clear")
        ok_btn = QtWidgets.QPushButton("OK")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        add_btn.clicked.connect(self.on_add)
        remove_btn.clicked.connect(self.on_remove)
        clear_btn.clicked.connect(self.on_clear)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(add_btn)
        btns.addWidget(remove_btn)
        btns.addWidget(clear_btn)
        btns.addStretch(1)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.list)
        layout.addLayout(btns)

    def on_add(self):
        dlg = QtWidgets.QFileDialog(self, "Choose directories")
        dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dlg.setOption(QtWidgets.QFileDialog.Option.ShowDirsOnly, True)
        dlg.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        if dlg.exec():
            sel = dlg.selectedFiles()
            existing = set(self.roots())
            for p in sel:
                if p and p not in existing:
                    self.list.addItem(p)
                    existing.add(p)

    def on_remove(self):
        for it in self.list.selectedItems():
            row = self.list.row(it)
            self.list.takeItem(row)

    def on_clear(self):
        self.list.clear()

    def roots(self) -> List[str]:
        return [self.list.item(i).text() for i in range(self.list.count())]

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        existing = set(self.roots())
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                path = os.path.normpath(path)
                if path not in existing:
                    self.list.addItem(path)
                    existing.add(path)


class StorageStatsDialog(QtWidgets.QDialog):
    CATEGORIES = {
        "Apps & Data": {"exts": {"exe", "msi", "bat", "sh", "dll", "bin", "iso"}, "color": "#FFD700"},
        "Images": {"exts": {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico", "tiff"}, "color": "#FFA500"},
        "Audio": {"exts": {"mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"}, "color": "#FF6347"},
        "Video": {"exts": {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v"}, "color": "#BA55D3"},
        "Archives": {"exts": {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"}, "color": "#4169E1"},
        "Documents": {"exts": {"doc", "docx", "pdf", "txt", "xls", "xlsx", "ppt", "pptx", "md", "csv", "rtf"}, "color": "#2E8B57"},
        "Others": {"exts": set(), "color": "#A9A9A9"}
    }

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Storage Stats")
        self.resize(600, 500)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        
        # Left: Cylinder Chart
        self.chart_widget = QtWidgets.QWidget()
        self.chart_widget.setFixedWidth(150)
        self.chart_layout = QtWidgets.QVBoxLayout(self.chart_widget)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.setSpacing(0)
        self.layout.addWidget(self.chart_widget)

        # Right: Details
        self.details_widget = QtWidgets.QWidget()
        self.details_layout = QtWidgets.QVBoxLayout(self.details_widget)
        self.header_label = QtWidgets.QLabel("Calculating...")
        self.header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: gray;")
        self.details_layout.addWidget(self.header_label)
        self.details_list = QtWidgets.QListWidget()
        self.details_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.details_layout.addWidget(self.details_list)
        self.layout.addWidget(self.details_widget)

    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.2f} MB"
        else:
            return f"{size_bytes/(1024**3):.2f} GB"

    def load_data(self):
        rows = get_stats(self.conn)
        
        # Aggregate data
        cat_sizes = {k: 0 for k in self.CATEGORIES}
        total_size = 0
        
        for ext, size, count in rows:
            if not size:
                continue
            size = int(size)
            ext_lower = ext.lower()
            found = False
            for cat, info in self.CATEGORIES.items():
                if ext_lower in info["exts"]:
                    cat_sizes[cat] += size
                    found = True
                    break
            if not found:
                cat_sizes["Others"] += size
            total_size += size

        # Update Header
        self.header_label.setText(f"Total Indexed Size: {self.format_size(total_size)}")

        # Draw Chart (Top to Bottom: Others -> Documents -> ... -> Apps)
        # We want to mimic the image which often stacks largest at bottom or specific order.
        # Let's just stack them in order of definition or size.
        # The image has a specific order. Let's stick to the order in CATEGORIES.
        
        # Clear previous chart items
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create segments
        # To make it look like a cylinder, we can just use colored frames.
        # We add them to QVBoxLayout. To handle "Remaining" space, we might just fill the rest with gray?
        # Since we only know indexed size, let's treat the whole height as "Total Indexed".
        
        sorted_cats = list(self.CATEGORIES.keys())
        
        # Details List
        self.details_list.clear()
        
        for cat in sorted_cats:
            size = cat_sizes[cat]
            if size == 0:
                continue
            
            # Detail Item
            item = QtWidgets.QListWidgetItem()
            widget = QtWidgets.QWidget()
            h = QtWidgets.QHBoxLayout(widget)
            h.setContentsMargins(5, 5, 5, 5)
            
            dot = QtWidgets.QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background-color: {self.CATEGORIES[cat]['color']}; border-radius: 6px;")
            
            name = QtWidgets.QLabel(cat)
            name.setStyleSheet("font-weight: bold;")
            
            size_lbl = QtWidgets.QLabel(self.format_size(size))
            size_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            
            h.addWidget(dot)
            h.addWidget(name)
            h.addStretch(1)
            h.addWidget(size_lbl)
            
            item.setSizeHint(widget.sizeHint())
            self.details_list.addItem(item)
            self.details_list.setItemWidget(item, widget)

            # Chart Segment
            # Height proportional to size/total_size * container_height?
            # Layouts handle proportions via stretch factors.
            # However, stretch factors are integers.
            # Let's try to use stretch factors based on percentage * 100.
            if total_size > 0:
                stretch = int((size / total_size) * 1000)
                if stretch > 0:
                    seg = QtWidgets.QWidget()
                    seg.setStyleSheet(f"background-color: {self.CATEGORIES[cat]['color']}; border-radius: 0px;")
                    self.chart_layout.addWidget(seg, stretch)
        
        # Add a bottom rounded look or top rounded look?
        # The image is a 3D cylinder. A simple flat stack is acceptable for a desktop app constrained by standard widgets.
        # To make it look slightly better, we can put the chart in a container with rounded corners.
        self.chart_widget.setStyleSheet("background-color: #F0F0F0; border-radius: 10px; overflow: hidden;")

