const isWindows = process.platform === "win32";

module.exports = {
  apps: [
    {
      name: "dawn",
      script: "run.py",
      interpreter: isWindows ? "venv\\Scripts\\pythonw.exe" : "venv/bin/python",
      ignore_watch: ["deploy", "\\.git", "*.log"],
      args: "farm",
    },
    {
      name: "google-docs-updater_dawn",
      script: "google-docs-updater/main.py",
      interpreter: isWindows ? "venv\\Scripts\\pythonw.exe" : "venv/bin/python",
      ignore_watch: ["deploy", "\\.git", "*.log"],
    },
  ],
};
