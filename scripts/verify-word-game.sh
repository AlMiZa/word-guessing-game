#!/bin/bash
# Word Game Implementation Verification Script

echo "==================================="
echo "Word Game Implementation Verification"
echo "==================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
total=0
passed=0

check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗${NC} $1 (missing)"
    fi
}

check_directory() {
    total=$((total + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (directory)"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗${NC} $1 (directory missing)"
    fi
}

echo "Backend Files:"
echo "---"
check_file "services/agent/src/agent.py"
check_file "services/agent/src/word_game_agent.py"
check_file "services/agent/src/supabase_client.py"
check_file "services/agent/pyproject.toml"
check_file "services/agent/supabase/schema.sql"
check_file "services/agent/supabase/README.md"

echo ""
echo "Frontend Files:"
echo "---"
check_file "services/web/app/(app)/word-game/page.tsx"
check_file "services/web/components/word-game-app.tsx"
check_file "services/web/components/word-game-session-view.tsx"
check_file "services/web/components/word-game-welcome.tsx"
check_file "services/web/components/livekit/agent-control-bar/word-game-control-bar.tsx"

echo ""
echo "Configuration Files:"
echo "---"
check_file ".env.example"
check_file "CLAUDE.md"
check_file "WORD-GAME-TESTING.md"

echo ""
echo "Docker Files:"
echo "---"
check_file "docker-compose.yml"
check_file "docker-compose.dev.yml"

echo ""
echo "==================================="
echo "Summary: $passed / $total checks passed"
echo "==================================="

if [ $passed -eq $total ]; then
    echo -e "${GREEN}All files verified! Ready for testing.${NC}"
    exit 0
else
    echo -e "${YELLOW}Some files are missing. Please review the output above.${NC}"
    exit 1
fi
