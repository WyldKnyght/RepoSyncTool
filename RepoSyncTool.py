import os
import tkinter as tk
import tkinter.messagebox as messagebox
import re
import subprocess


def is_valid_repository_url(url):
    pattern = r'^https?://github\.com/.+/.+$'
    return re.match(pattern, url) is not None


def clone_and_sync_repository(forked_repo, local_folder):
    # Clone the forked repository to the local machine
    subprocess.run(["git", "clone", forked_repo], cwd=local_folder)

    # Change into the cloned directory
    repo_name = forked_repo.split("/")[-1].replace(".git", "")
    os.chdir(os.path.join(local_folder, repo_name))

    # Add the original repository as a remote
    original_repo = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True,
                                   text=True).stdout.strip()
    subprocess.run(["git", "remote", "add", "upstream", original_repo])

    # Fetch changes from the original repository
    subprocess.run(["git", "fetch", "upstream"])

    # Merge changes from the original repository into the local copy
    subprocess.run(["git", "merge", "upstream/master"])

    # Push the changes to the forked repository
    subprocess.run(["git", "push", "origin", "master"])


class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fork_Clone_Sync_Repo")

        self.forked_repo_label = tk.Label(self, text="Forked Repository URL:")
        self.forked_repo_label.pack()

        self.forked_repo_entry = tk.Entry(self, width=50)
        self.forked_repo_entry.pack()

        self.local_folder_label = tk.Label(self, text="Local PC Folder for Clone:")
        self.local_folder_label.pack()

        self.local_folder_entry = tk.Entry(self, width=50)
        self.local_folder_entry.pack()

        self.ok_button = tk.Button(self, text="Ok", command=self.ok_button_click)
        self.ok_button.pack()

        self.test_button = tk.Button(self, text="Test", command=self.test_button_click)
        self.test_button.pack()

    def ok_button_click(self):
        forked_repo = self.forked_repo_entry.get().strip()
        local_folder = self.local_folder_entry.get().strip()

        if not (forked_repo and local_folder):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Validate repository URL
        if not is_valid_repository_url(forked_repo):
            messagebox.showerror("Error", "Invalid repository URL.")
            return

        # Clear the fields
        self.forked_repo_entry.delete(0, tk.END)
        self.local_folder_entry.delete(0, tk.END)

        # Perform the clone and sync operation
        clone_and_sync_repository(forked_repo, local_folder)

    def test_button_click(self):
        # Run the test script
        local_folder = self.local_folder_entry.get().strip()
        script_path = os.path.join(local_folder, "update_mirror.sh")

        if not os.path.exists(script_path):
            messagebox.showerror("Error", "Test script not found.")
            return

        result = subprocess.run(["bash", script_path], capture_output=True, text=True)

        if result.returncode == 0:

            messagebox.showinfo("Test Result", "Test successful.")
        else:
            error_output = result.stderr.strip() if result.stderr else result.stdout.strip()
            messagebox.showerror("Test Result", f"Test failed:\n\n{error_output}")

        if __name__ == "__main__":
            # Create an instance of the AppGUI class
            app = AppGUI()

            # Start the Tkinter event loop
            app.mainloop()
