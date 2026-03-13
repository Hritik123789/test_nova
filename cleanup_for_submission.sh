#!/bin/bash
# Cleanup script - Remove Ollama files before GitHub submission

echo "🧹 Cleaning up Ollama files for submission..."

# Remove Ollama agent files
rm -f agents/news-synthesis/local_news_agent_simple.py
rm -f agents/news-synthesis/local_news_agent.py
rm -f agents/bridge_to_permits.py
rm -f agents/OLLAMA_SETUP.md
rm -f agents/test_workflow.py

# Remove development docs that mention Ollama
rm -f agents/TEST_NOVA_NOW.md
rm -f agents/AWS_CREDIT_STRATEGY.md
rm -f CITYPULSE_GAP_ANALYSIS.md
rm -f REALISTIC_7DAY_PLAN.md

# Remove cost tracking (optional - contains development data)
rm -f agents/cost_log.json

# Remove cached Ollama results
rm -f agents/news-synthesis/analyzed_news.json
rm -f agents/permit-monitor/pending_investigations.json

echo "✅ Cleanup complete!"
echo ""
echo "Files removed:"
echo "  - Ollama agent scripts"
echo "  - Development documentation"
echo "  - Cost logs"
echo "  - Cached results"
echo ""
echo "Ready for GitHub submission! 🚀"
