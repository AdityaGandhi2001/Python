# Subprocess is used to call the external commands:
import subprocess

result = subprocess.run(["ls", "-l"], capture_output=True, text=True)
print("Return Code:", result.returncode)
print("Output", result.stdout)
print("Error:", result.stderr)
process = subprocess.Popen(
    ['ls,', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
print("stdput", stdout)

total = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(total.stderr)
print(total.stdout)
print(total.returncode)
