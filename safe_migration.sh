#!/bin/bash
# Safe Migration Script for Raspberry Pi Kiosk
# Run this script on your Raspberry Pi to safely update to the new version

set -e  # Exit on error

echo "======================================"
echo "Kiosk Safe Migration Script"
echo "======================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory (look for .git folder or any known file)
if [ ! -d ".git" ] && [ ! -f "config.json" ]; then
    echo -e "${RED}Error: Not in the announcements_kiosk directory${NC}"
    echo "Please cd to /home/annkiosk/announcements_kiosk first"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backing up important files...${NC}"
BACKUP_DIR=~/kiosk_migration_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup config files
if [ -f "config.json" ]; then
    echo "  - Backing up config.json"
    cp config.json "$BACKUP_DIR/"
fi

if [ -d "pipiosk_v1" ]; then
    echo "  - Backing up pipiosk_v1/ folder"
    cp -r pipiosk_v1 "$BACKUP_DIR/"
fi

# Backup HTML files
if [ -d "html" ]; then
    echo "  - Backing up html/ folder"
    cp -r html "$BACKUP_DIR/"
fi

# Backup custom HTML files
for file in Joke_of_the_day.html kid_of_the_month.html; do
    if [ -f "$file" ]; then
        echo "  - Backing up $file"
        cp "$file" "$BACKUP_DIR/"
    fi
done

# Backup any custom scripts
if [ -f "auto_Click.py" ]; then
    echo "  - Backing up auto_Click.py"
    cp auto_Click.py "$BACKUP_DIR/"
fi

echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"
echo ""

echo -e "${YELLOW}Step 2: Cleaning up deleted files from Git tracking...${NC}"
# Remove deleted files from git tracking
git rm --quiet "MONTHLY ATTENDANCE ROSTER.xlsx" 2>/dev/null || true
git rm --quiet "attendance roster test.pdf" 2>/dev/null || true
git rm --quiet "highlevel_example.py" 2>/dev/null || true
git rm --quiet "slideshow_v1.py" 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned up old files${NC}"
echo ""

echo -e "${YELLOW}Step 3: Temporarily moving files that might conflict...${NC}"
# Move files that exist in both local and new repo
TEMP_MOVE=()
if [ -f "config.json" ]; then
    mv config.json config.json.tmp
    TEMP_MOVE+=("config.json")
    echo "  - Moved config.json aside temporarily"
fi

echo -e "${GREEN}✓ Files moved${NC}"
echo ""

echo -e "${YELLOW}Step 4: Pulling latest code from GitHub...${NC}"
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 5: Restoring your files...${NC}"
# Restore temporarily moved files, keeping YOUR version
for file in "${TEMP_MOVE[@]}"; do
    if [ -f "${file}.tmp" ]; then
        mv -f "${file}.tmp" "${file}"
        echo "  - Restored your ${file}"
    fi
done
echo -e "${GREEN}✓ Files restored${NC}"
echo ""

echo -e "${YELLOW}Step 6: Ensuring your configuration is in place...${NC}"

# Restore config.json if it exists in new repo
if [ ! -f "config.json" ] && [ -f "$BACKUP_DIR/config.json" ]; then
    echo "  - Restoring config.json to repository root"
    cp "$BACKUP_DIR/config.json" ./
fi

# Restore pipiosk_v1 folder
if [ -d "$BACKUP_DIR/pipiosk_v1" ]; then
    echo "  - Restoring pipiosk_v1/ folder"
    cp -r "$BACKUP_DIR/pipiosk_v1" ./
fi

# Restore html folder (merge with any new files)
if [ -d "$BACKUP_DIR/html" ]; then
    echo "  - Restoring html/ folder"
    mkdir -p html
    cp -r "$BACKUP_DIR/html/"* html/ 2>/dev/null || true
fi

echo -e "${GREEN}✓ Configuration restored${NC}"
echo ""

echo -e "${YELLOW}Step 7: Setting up new kiosk controller...${NC}"

# Make scripts executable
chmod +x kiosk_controller.py kiosk_manager.py html_generator.py

# Check if service needs updating
if [ -f "/etc/systemd/system/kiosk.service" ]; then
    echo ""
    echo -e "${YELLOW}Your systemd service exists. To update it:${NC}"
    echo "  sudo cp kiosk.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl restart kiosk.service"
    echo ""
    echo "Or you can do that manually later."
    echo ""
    read -p "Update systemd service now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo cp kiosk.service /etc/systemd/system/
        sudo systemctl daemon-reload
        echo -e "${GREEN}✓ Service file updated${NC}"
    fi
fi

echo ""
echo -e "${GREEN}======================================"
echo "Migration Complete!"
echo "======================================${NC}"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify your config: python3 kiosk_manager.py config"
echo "2. Test the new controller: python3 kiosk_controller.py"
echo "3. If it works, restart the service:"
echo "   sudo systemctl restart kiosk.service"
echo "4. Check status: sudo systemctl status kiosk.service"
echo "5. Watch logs: sudo journalctl -u kiosk.service -f"
echo ""
echo -e "${GREEN}Your old files are safely backed up at:${NC}"
echo "  $BACKUP_DIR"
echo ""
echo "If anything goes wrong, you can restore from there!"
echo ""
