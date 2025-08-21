#!/bin/bash

echo "Starting Open Interpreter installation..."
sleep 2
echo "This will take approximately 5 minutes..."
sleep 2

# Check if Rust is installed
if ! command -v rustc &> /dev/null
then
    echo "Rust is not installed. Installing now..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
else
    echo "Rust is already installed."
fi

# Install pyenv
curl https://pyenv.run | bash

# Define pyenv location
pyenv_root="$HOME/.pyenv/bin/pyenv"

python_version="3.11.7"

# Install specific Python version using pyenv
$pyenv_root init
$pyenv_root install $python_version --skip-existing
$pyenv_root shell $python_version

$pyenv_root exec pip install "open-interpreter[nova-prime]" --break-system-packages

echo ""
echo "Open Interpreter + Nova Prime has been installed. Run the following commands:"
echo ""
echo "  interpreter   # Classic CLI interface"
echo "  nova-prime    # Desktop assistant with voice ('hey nova')"
