import subprocess

result = subprocess.run(
    ["node", "main.js"],
    capture_output=True,
    text=True
)

print(result.stdout)