from PyQt6.QtWidgets import QFileDialog,QListWidgetItem
from abstract_utilities.robust_readers import define_defaults
import os,sys
# — UI helpers —
def browse_dir(self):
    start = self.dir_in.text() or os.getcwd()
    d = QFileDialog.getExistingDirectory(self, "Choose directory", start)
    if not d:
        return

    # Normalize once, early
    d = os.path.realpath(os.path.expanduser(d))

    # Defensive: GVFS can give stale mounts
    if not os.path.isdir(d):
        raise ValueError(f"Selected path is not a valid directory: {d}")

    self.dir_in.setText(d)
def on_dir_edit_finished(self):
    try:
        resolved = resolve_directory_input(self.dir_in.text())
        self.dir_in.setText(resolved)
    except Exception:
        pass  # let validation handle it later  
def make_params(self):
    self.dir_in.editingFinished.connect(self.on_dir_edit_finished)
    directory = resolve_directory_input(self.dir_in.text())

    # strings
    s_raw = [s.strip() for s in self.strings_in.text().split(",") if s.strip()]
    # allowed_exts: allow "ts,tsx" or "ts|tsx"
    e_raw = self.allowed_exts_in.text().strip()
    allowed_exts: Union[bool, Set[str]] = None
    if e_raw:
        splitter = '|' if '|' in e_raw else ','
        exts_list = [e.strip() for e in e_raw.split(splitter) if e.strip()]
        allowed_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    # unallowed_exts similar
    ee_raw = self.exclude_exts_in.text().strip()
    exclude_exts: Union[bool, Set[str]] = None
    if ee_raw:
        splitter = '|' if '|' in ee_raw else ','
        exts_list = [e.strip() for e in ee_raw.split(splitter) if e.strip()]
        exclude_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    # allowed_types
    at_raw = self.allowed_types_in.text().strip()
    allowed_types: Union[bool, Set[str]] = None
    if at_raw:
        allowed_types = {e.strip() for e in at_raw.split(',') if e.strip()}
    # exclude_types
    et_raw = self.exclude_types_in.text().strip()
    exclude_types: Union[bool, Set[str]] = None
    if et_raw:
        exclude_types = {e.strip() for e in et_raw.split(',') if e.strip()}
    # allowed_dirs
    ad_raw = self.allowed_dirs_in.text().strip()
    allowed_dirs: Union[bool, List[str]] = None
    if ad_raw:
        allowed_dirs = [e.strip() for e in ad_raw.split(',') if e.strip()]
    # exclude_dirs
    ed_raw = self.exclude_dirs_in.text().strip()
    exclude_dirs: Union[bool, List[str]] = None
    if ed_raw:
        exclude_dirs = [e.strip() for e in ed_raw.split(',') if e.strip()]
    # exclude_patterns
    ap_raw = self.allowed_patterns_in.text().strip()
    allowed_patterns: Union[bool, List[str]] = None
    if ap_raw:
        allowed_patterns = [e.strip() for e in ap_raw.split(',') if e.strip()]
    # exclude_patterns
    ep_raw = self.exclude_patterns_in.text().strip()
    exclude_patterns: Union[bool, List[str]] = None
    if ep_raw:
        exclude_patterns = [e.strip() for e in ep_raw.split(',') if e.strip()]
    # add
    add = self.chk_add.isChecked()
    # spec_line
    spec_line = self.spec_spin.value()
    spec_line = False if spec_line == 0 else int(spec_line)
    recursive=self.chk_recursive.isChecked()
    strings=s_raw
    total_strings=self.chk_total.isChecked()
    parse_lines=self.chk_parse.isChecked()
    spec_line=spec_line
    get_lines=self.chk_getlines.isChecked()
    cfg = define_defaults(
                allowed_exts=allowed_exts,
                exclude_exts=exclude_exts,
                allowed_types=allowed_types,
                exclude_types=exclude_types,
                allowed_dirs=allowed_dirs,
                exclude_dirs=exclude_dirs,
                allowed_patterns=allowed_patterns,
                exclude_patterns=exclude_patterns,
                add=add
            )
    return {
        "directory":directory,
        "get_lines":get_lines,
        "spec_line":spec_line,
        "parse_lines":parse_lines,
        "total_strings":total_strings,
        "strings":strings,
        "recursive":recursive,
        "cfg":cfg
     }
