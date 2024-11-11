const isWindows = process.platform === "win32";

module.exports = {
  apps: [
    {
      name: "dawn_bot",
      script: "main.py",
      interpreter: isWindows ? "venv\\Scripts\\pythonw.exe" : "venv/bin/python",
      ignore_watch: ["deploy", "\\.git", "*.log"],
      args: "farm",
    },
  ],
};
