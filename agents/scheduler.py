# -*- coding: utf-8 -*-
"""
CityPulse Data Refresh Scheduler
Automatically runs all agents every 3-4 hours to keep data fresh
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_all_agents():
    """Run all agents using run_all_agents.py"""
    logger.info("="*70)
    logger.info("Starting scheduled agent execution")
    logger.info("="*70)
    
    try:
        # Run agents with parallel execution and caching
        result = subprocess.run(
            [sys.executable, 'run_all_agents.py', '--parallel', '--cache'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=os.path.dirname(__file__),
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ All agents completed successfully")
            logger.info(f"Output preview: {result.stdout[:500]}")
        else:
            logger.error(f"❌ Agents failed with return code {result.returncode}")
            logger.error(f"Error: {result.stderr[:500]}")
        
    except subprocess.TimeoutExpired:
        logger.error("⏱️  Agent execution timed out (30 minutes)")
    except Exception as e:
        logger.error(f"❌ Error running agents: {e}")
    
    logger.info("="*70)
    logger.info("Scheduled execution complete")
    logger.info(f"Next run in 1 hour")
    logger.info("="*70)
    logger.info("")


def main():
    """Main scheduler loop"""
    logger.info("="*70)
    logger.info("🕐 CityPulse Data Refresh Scheduler")
    logger.info("="*70)
    logger.info("")
    logger.info("Schedule: Every 1 hour")
    logger.info("Mode: Parallel execution with caching")
    logger.info("Started at: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*70)
    logger.info("")
    
    # Run immediately on startup
    logger.info("Running initial data collection...")
    run_all_agents()
    
    # Schedule to run every 1 hour
    schedule.every(1).hours.do(run_all_agents)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("")
        logger.info("="*70)
        logger.info("Scheduler stopped by user")
        logger.info("="*70)


if __name__ == "__main__":
    main()
