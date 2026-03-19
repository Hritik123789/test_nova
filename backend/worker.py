#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CityPulse Background Worker for Render
Runs agents on a schedule to keep data fresh
"""

import os
import sys
import logging
import time
import schedule
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add agents directory to path
AGENTS_DIR = Path(__file__).parent.parent / 'agents'
sys.path.insert(0, str(AGENTS_DIR))


def run_agents():
    """Run all agents using the orchestrator"""
    logger.info("="*70)
    logger.info("Starting scheduled agent execution")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)
    
    try:
        # Import and run the orchestrator
        os.chdir(str(AGENTS_DIR))
        
        # Import the orchestrator
        from run_all_agents import AgentOrchestrator
        
        # Run with parallel execution and caching
        orchestrator = AgentOrchestrator(
            parallel=True,
            use_cache=True,
            cache_ttl_hours=1
        )
        
        exit_code = orchestrator.run_all()
        
        if exit_code == 0:
            logger.info("✅ All agents completed successfully")
        else:
            logger.warning(f"⚠️  Some agents failed (exit code: {exit_code})")
            
    except Exception as e:
        logger.error(f"❌ Error running agents: {e}", exc_info=True)
    
    logger.info("="*70)
    logger.info("Scheduled execution complete")
    logger.info(f"Next run in 1 hour")
    logger.info("="*70)
    logger.info("")


def main():
    """Main worker loop"""
    logger.info("="*70)
    logger.info("🕐 CityPulse Background Worker")
    logger.info("="*70)
    logger.info("")
    logger.info("Schedule: Every 1 hour")
    logger.info("Mode: Parallel execution with caching")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Agents directory: {AGENTS_DIR}")
    logger.info("")
    logger.info("="*70)
    logger.info("")
    
    # Run immediately on startup
    logger.info("Running initial data collection...")
    run_agents()
    
    # Schedule to run every 1 hour
    schedule.every(1).hours.do(run_agents)
    
    # Keep running
    logger.info("Worker is now running. Waiting for next scheduled run...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("")
            logger.info("="*70)
            logger.info("Worker stopped")
            logger.info("="*70)
            break
        except Exception as e:
            logger.error(f"Error in worker loop: {e}", exc_info=True)
            time.sleep(60)  # Wait a minute before retrying


if __name__ == "__main__":
    main()
