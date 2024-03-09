import subprocess

# Define the npm command to install the package
npm_command = ["npm", "install", "--save", "@ckeditor/ckeditor5-build-classic"]

# Execute the npm command
subprocess.run(npm_command)