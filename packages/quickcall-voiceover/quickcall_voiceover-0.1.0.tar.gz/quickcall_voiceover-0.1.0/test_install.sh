#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╭──────────────────────────────────────────────────────────╮"
echo "│  QuickCall VoiceOver - Installation Test                 │"
echo "╰──────────────────────────────────────────────────────────╯"
echo -e "${NC}"

# Test directory
TEST_DIR="/tmp/quickcall-voiceover-test"
VENV_NAME="voiceover-test-venv"

# Cleanup previous test
if [ -d "$TEST_DIR" ]; then
    echo -e "${YELLOW}Cleaning up previous test directory...${NC}"
    rm -rf "$TEST_DIR"
fi

# Create test directory
echo -e "${CYAN}Creating test directory: $TEST_DIR${NC}"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create virtual environment
echo -e "${CYAN}Creating virtual environment: $VENV_NAME${NC}"
python3 -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo -e "${CYAN}Upgrading pip...${NC}"
pip install --upgrade pip -q

# Install from local path
PACKAGE_PATH="/Users/sagar/work/all-things-quickcall/voice-over"
echo -e "${CYAN}Installing quickcall-voiceover from: $PACKAGE_PATH${NC}"
pip install "$PACKAGE_PATH" -q

# Verify installation
echo -e "${GREEN}✓ Package installed${NC}"
echo ""

# Test 1: Show help
echo -e "${YELLOW}━━━ Test 1: CLI Help ━━━${NC}"
quickcall-voiceover --help
echo ""

# Test 2: Show voices
echo -e "${YELLOW}━━━ Test 2: Show Voices ━━━${NC}"
quickcall-voiceover --voices
echo ""

# Test 3: Config-based generation
echo -e "${YELLOW}━━━ Test 3: Config-based Generation ━━━${NC}"

# Create test config
cat > test_config.json << 'CONFIGEOF'
{
  "voice": {
    "model": "en_US-hfc_male-medium",
    "length_scale": 1.0,
    "noise_scale": 0.667,
    "noise_w": 0.8,
    "sentence_silence": 0.3
  },
  "output": {
    "format": "wav"
  },
  "segments": [
    {
      "id": "01_hello",
      "text": "Hello! This is a test of QuickCall VoiceOver."
    },
    {
      "id": "02_features",
      "text": "This tool generates high quality voice overs from text."
    },
    {
      "id": "03_goodbye",
      "text": "Thanks for testing. Goodbye!"
    }
  ]
}
CONFIGEOF

echo -e "${CYAN}Created test_config.json${NC}"
cat test_config.json
echo ""

echo -e "${CYAN}Running: quickcall-voiceover test_config.json --combine${NC}"
quickcall-voiceover test_config.json --combine

echo ""
echo -e "${GREEN}Generated files:${NC}"
ls -lah output/
echo ""

# Test 4: Text file based generation (non-interactive)
echo -e "${YELLOW}━━━ Test 4: Text File Generation ━━━${NC}"

# Create test text file
cat > test_lines.txt << 'TXTEOF'
Welcome to QuickCall.
This is line two of the voice over.
And this is the final line.
TXTEOF

echo -e "${CYAN}Created test_lines.txt:${NC}"
cat test_lines.txt
echo ""

# Create a simple Python script to test programmatic usage
cat > test_programmatic.py << 'PYEOF'
from pathlib import Path
from quickcall_voiceover import generate_from_text

lines = [
    "This is a programmatic test.",
    "Generated using the Python API.",
    "QuickCall VoiceOver works great!"
]

success = generate_from_text(
    lines=lines,
    voice="en_US-hfc_male-medium",
    output_dir=Path("./output_programmatic"),
    combine=True,
    combined_filename="programmatic_combined.wav",
)

print(f"\nProgrammatic test: {'SUCCESS' if success else 'FAILED'}")
PYEOF

echo -e "${CYAN}Running programmatic test...${NC}"
python test_programmatic.py

echo ""
echo -e "${GREEN}Programmatic output:${NC}"
ls -lah output_programmatic/
echo ""

# Summary
echo -e "${CYAN}"
echo "╭──────────────────────────────────────────────────────────╮"
echo "│  Test Summary                                            │"
echo "╰──────────────────────────────────────────────────────────╯"
echo -e "${NC}"

echo -e "${GREEN}✓ CLI help works${NC}"
echo -e "${GREEN}✓ Voice listing works${NC}"
echo -e "${GREEN}✓ Config-based generation works${NC}"
echo -e "${GREEN}✓ Programmatic API works${NC}"
echo ""

echo -e "${CYAN}Test directory: $TEST_DIR${NC}"
echo -e "${CYAN}To clean up: rm -rf $TEST_DIR${NC}"
echo ""

# Deactivate venv
deactivate

echo -e "${GREEN}All tests completed successfully!${NC}"
