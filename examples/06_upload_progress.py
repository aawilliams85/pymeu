import os
from pymeu import MEUtility
from tqdm import tqdm

class ProgressTracker:
    def __init__(self, desc: str, total_bytes: int = 1):
        self.progress_bar = tqdm(total=total_bytes, desc=desc)

    def update(self, description: str, total_bytes: int, current_bytes: int):
        self.progress_bar.desc = description
        self.progress_bar.total = total_bytes
        self.progress_bar.n = current_bytes
        self.progress_bar.refresh()
        if current_bytes >= total_bytes:
            self.progress_bar.close()

base_path = os.path.abspath(os.path.dirname(__file__))
upload_file_path = os.path.join(base_path, 'YourProgram.mer')

tracker = ProgressTracker("Upload")
meu = MEUtility('YourPanelViewIpAddress')
meu.upload(upload_file_path, tracker.update, overwrite=True)