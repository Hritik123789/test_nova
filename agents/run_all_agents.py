# -*- coding: utf-8 -*-
"""
CityPulse Master Orchestrator
Runs all agents in sequence and generates complete dataset
Supports both sequential and parallel execution modes
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Global UTF-8 setting for all subprocesses
os.environ["PYTHONIOENCODING"] = "utf-8"

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class AgentOrchestrator:
    """Orchestrates execution of all CityPulse agents"""
    
    def __init__(self, parallel: bool = False, use_cache: bool = False, cache_ttl_hours: int = 6):
        """
        Initialize orchestrator
        
        Args:
            parallel: If True, run independent agents in parallel
            use_cache: If True, use cached data when available
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.base_dir = Path(__file__).parent
        self.results = []
        self.start_time = datetime.now()
        self.parallel = parallel
        self.use_cache = use_cache
        self.cache_ttl_hours = cache_ttl_hours
        self.print_lock = threading.Lock()  # For thread-safe printing
        
        # Import cache manager if caching enabled
        if self.use_cache:
            try:
                from cache_manager import get_cache_manager
                self.cache = get_cache_manager()
                print(f"💾 Cache enabled (TTL: {cache_ttl_hours} hours)")
            except ImportError:
                print("⚠️  Cache manager not found, disabling cache")
                self.use_cache = False
                self.cache = None
        else:
            self.cache = None
        
    def run_agent(self, script_path: str, name: str, env_vars: dict = None) -> bool:
        """
        Run a single agent script
        
        Args:
            script_path: Relative path to the script
            name: Display name of the agent
            env_vars: Optional environment variables
            
        Returns:
            True if successful, False otherwise
        """
        # Check cache first if enabled
        if self.use_cache and self.cache:
            cache_key = script_path.replace('/', '_').replace('\\', '_').replace('.py', '')
            cached_result = self.cache.get(cache_key, ttl_hours=self.cache_ttl_hours)
            
            if cached_result is not None:
                print(f"\n{'='*70}")
                print(f"💾 Using cached data: {name}")
                print('='*70)
                return True
        
        print(f"\n{'='*70}")
        print(f"🤖 Running: {name}")
        print('='*70)
        
        full_path = self.base_dir / script_path
        
        if not full_path.exists():
            print(f"⚠️  Script not found: {full_path}")
            return False
        
        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        # Add cache flag to environment
        if self.use_cache:
            env['USE_CACHE'] = 'true'
            env['CACHE_TTL_HOURS'] = str(self.cache_ttl_hours)
        
        try:
            result = subprocess.run(
                [sys.executable, str(full_path)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                cwd=str(full_path.parent),
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {name} completed successfully")
                
                # Cache success if enabled
                if self.use_cache and self.cache:
                    cache_key = script_path.replace('/', '_').replace('\\', '_').replace('.py', '')
                    self.cache.set(cache_key, {'success': True, 'timestamp': datetime.now().isoformat()})
                
                return True
            else:
                print(f"❌ {name} failed")
                print(f"   Script: {script_path}")
                if result.stderr:
                    error_msg = result.stderr[:500]  # First 500 chars
                    print(f"   Reason: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  {name} timed out (5 minutes)")
            print(f"   Script: {script_path}")
            return False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            print(f"   Script: {script_path}")
            return False
    
    def run_agent_parallel(self, script_path: str, name: str, env_vars: dict = None) -> dict:
        """
        Run a single agent script (parallel version with thread-safe printing)
        
        Args:
            script_path: Relative path to the script
            name: Display name of the agent
            env_vars: Optional environment variables
            
        Returns:
            Dict with 'name', 'success', and 'error' keys
        """
        with self.print_lock:
            print(f"\n{'='*70}")
            print(f"🤖 Starting: {name}")
            print('='*70)
        
        full_path = self.base_dir / script_path
        
        if not full_path.exists():
            with self.print_lock:
                print(f"⚠️  Script not found: {full_path}")
            return {'name': name, 'success': False, 'error': 'Script not found'}
        
        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        try:
            result = subprocess.run(
                [sys.executable, str(full_path)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                cwd=str(full_path.parent),
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                with self.print_lock:
                    print(f"✅ {name} completed successfully")
                return {'name': name, 'success': True, 'error': None}
            else:
                error_msg = result.stderr[:500] if result.stderr else 'Unknown error'
                with self.print_lock:
                    print(f"❌ {name} failed")
                    print(f"   Script: {script_path}")
                    print(f"   Reason: {error_msg}")
                return {'name': name, 'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            with self.print_lock:
                print(f"⏱️  {name} timed out (5 minutes)")
                print(f"   Script: {script_path}")
            return {'name': name, 'success': False, 'error': 'Timeout'}
        except Exception as e:
            with self.print_lock:
                print(f"❌ {name} error: {e}")
                print(f"   Script: {script_path}")
            return {'name': name, 'success': False, 'error': str(e)}
    
    def run_phase_1_agents(self):
        """Run Phase 1: Core Data Collection Agents"""
        print("\n" + "="*70)
        print("📊 PHASE 1: CORE DATA COLLECTION AGENTS")
        print("="*70)
        
        agents = [
            {
                'script': 'news-synthesis/local_news_agent_nova.py',
                'name': 'News Synthesis Agent (Nova 2 Lite)',
                'env': {'MAX_ARTICLES': '10'}
            },
            {
                'script': 'permit-monitor/permit_monitor_real.py',
                'name': 'Permit Monitor Agent (Real Scraping)',
                'env': {}
            },
            {
                'script': 'permit-monitor/bmc_ward_monitor.py',
                'name': 'BMC Ward Monitor (Ward-Level Permits)',
                'env': {}
            },
            {
                'script': 'social-listening/social_listener_nova.py',
                'name': 'Social Listening Agent (Reddit + Sentiment)',
                'env': {}
            },
            {
                'script': 'image_analysis_nova.py',
                'name': 'Visual Intelligence Agent (Nova 2 Omni)',
                'env': {}
            }
        ]
        
        if self.parallel:
            # Run agents in parallel (Phase 1 agents are independent)
            print(f"🚀 Running {len(agents)} agents in parallel...")
            
            with ThreadPoolExecutor(max_workers=len(agents)) as executor:
                # Submit all agents
                futures = {
                    executor.submit(
                        self.run_agent_parallel,
                        agent['script'],
                        agent['name'],
                        agent.get('env')
                    ): agent for agent in agents
                }
                
                # Collect results as they complete
                for future in as_completed(futures):
                    result = future.result()
                    self.results.append({
                        'phase': 'Phase 1',
                        'agent': result['name'],
                        'success': result['success']
                    })
        else:
            # Run agents sequentially
            for agent in agents:
                success = self.run_agent(
                    agent['script'],
                    agent['name'],
                    agent.get('env')
                )
                self.results.append({
                    'phase': 'Phase 1',
                    'agent': agent['name'],
                    'success': success
                })
    
    def run_phase_2_features(self):
        """Run Phase 2: User Features"""
        print("\n" + "="*70)
        print("🎯 PHASE 2: USER FEATURES")
        print("="*70)
        
        features = [
            {
                'script': 'features/morning_briefing_nova.py',
                'name': 'Morning Voice Briefing'
            },
            {
                'script': 'features/smart_alerts_nova.py',
                'name': 'Smart Alerts System'
            },
            {
                'script': 'features/safety_intelligence_nova.py',
                'name': 'Safety Intelligence'
            },
            {
                'script': 'features/investment_insights_nova.py',
                'name': 'Investment Insights'
            },
            {
                'script': 'features/community_pulse_nova.py',
                'name': 'Community Pulse'
            }
        ]
        
        if self.parallel:
            # Run features in parallel (Phase 2 depends on Phase 1 completion, but features are independent)
            print(f"🚀 Running {len(features)} features in parallel...")
            
            with ThreadPoolExecutor(max_workers=len(features)) as executor:
                # Submit all features
                futures = {
                    executor.submit(
                        self.run_agent_parallel,
                        feature['script'],
                        feature['name']
                    ): feature for feature in features
                }
                
                # Collect results as they complete
                for future in as_completed(futures):
                    result = future.result()
                    self.results.append({
                        'phase': 'Phase 2',
                        'agent': result['name'],
                        'success': result['success']
                    })
        else:
            # Run features sequentially
            for feature in features:
                success = self.run_agent(
                    feature['script'],
                    feature['name']
                )
                self.results.append({
                    'phase': 'Phase 2',
                    'agent': feature['name'],
                    'success': success
                })
    
    def verify_output_files(self):
        """Verify all expected output files exist"""
        print("\n" + "="*70)
        print("📁 VERIFYING OUTPUT FILES")
        print("="*70)
        
        expected_files = [
            'data/news.json',
            'data/permits.json',
            'data/bmc_permits.json',
            'data/social.json',
            'data/images.json',
            'data/morning_briefing.json',
            'data/smart_alerts.json',
            'data/safety_alerts.json',
            'data/investment_insights.json',
            'data/community_pulse.json',
            'cost_log.json'
        ]
        
        missing_files = []
        for file_path in expected_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                print(f"❌ {file_path} (missing)")
                missing_files.append(file_path)
        
        return len(missing_files) == 0
    
    def generate_summary(self):
        """Generate execution summary"""
        print("\n" + "="*70)
        print("📊 EXECUTION SUMMARY")
        print("="*70)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n⏱️  Total Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Results by phase
        print("\n" + "-"*70)
        print("Results by Phase:")
        print("-"*70)
        
        for phase in ['Phase 1', 'Phase 2']:
            phase_results = [r for r in self.results if r['phase'] == phase]
            success_count = sum(1 for r in phase_results if r['success'])
            total_count = len(phase_results)
            
            print(f"\n{phase}: {success_count}/{total_count} successful")
            for r in phase_results:
                status = "✅" if r['success'] else "❌"
                print(f"  {status} {r['agent']}")
        
        # Cost summary
        print("\n" + "-"*70)
        print("Cost Summary:")
        print("-"*70)
        
        try:
            cost_log_path = self.base_dir / 'cost_log.json'
            if cost_log_path.exists():
                with open(cost_log_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Handle malformed JSON (trailing commas, multiple objects)
                    try:
                        logs = json.loads(content)
                    except json.JSONDecodeError as e:
                        # Try to fix trailing comma
                        if content.rstrip().endswith(','):
                            content = content.rstrip().rstrip(',')
                            if not content.endswith(']'):
                                content += '\n]'
                            logs = json.loads(content)
                        else:
                            raise e
                
                total_cost = sum(log.get('estimated_cost', 0) for log in logs)
                print(f"\n💰 Total Cost: ${total_cost:.4f}")
                print(f"💰 Budget Used: {(total_cost/100)*100:.2f}%")
                print(f"💰 Remaining Budget: ${100 - total_cost:.2f}")
                
                # Cost by agent (group by agent_name, fallback to operation)
                print("\nCost by Agent:")
                agent_costs = {}
                for log in logs:
                    # Try to get agent name, fallback to operation, then to "unknown_agent"
                    agent = log.get('agent_name') or log.get('agent') or log.get('operation', 'unknown_agent')
                    cost = log.get('estimated_cost', 0)
                    agent_costs[agent] = agent_costs.get(agent, 0) + cost
                
                # Sort by cost (highest first)
                for agent, cost in sorted(agent_costs.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {agent}: ${cost:.4f}")
            else:
                print("⚠️  Cost log not found")
        except Exception as e:
            print(f"⚠️  Could not parse cost log (malformed JSON)")
            print(f"   Continuing without cost summary...")
        
        # Overall status
        print("\n" + "="*70)
        total_success = sum(1 for r in self.results if r['success'])
        total_agents = len(self.results)
        
        if total_success == total_agents:
            print("🎉 ALL AGENTS COMPLETED SUCCESSFULLY!")
            print("="*70)
            return True
        else:
            print(f"⚠️  {total_agents - total_success} AGENTS FAILED")
            print("="*70)
            return False
    
    def run_all(self):
        """Run complete orchestration"""
        print("="*70)
        print("🚀 CITYPULSE MASTER ORCHESTRATOR")
        print("="*70)
        print(f"\nMode: {'PARALLEL' if self.parallel else 'SEQUENTIAL'}")
        if self.use_cache:
            print(f"Cache: ENABLED (TTL: {self.cache_ttl_hours} hours)")
        else:
            print(f"Cache: DISABLED")
        print(f"Starting complete agent execution...")
        print(f"Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run Phase 1
        self.run_phase_1_agents()
        
        # Run Phase 2
        self.run_phase_2_features()
        
        # Verify outputs
        files_ok = self.verify_output_files()
        
        # Generate summary
        success = self.generate_summary()
        
        if success and files_ok:
            print("\n✅ Complete dataset generated successfully!")
            print("📦 All output files ready for frontend integration")
            return 0
        else:
            print("\n⚠️  Some agents failed or files are missing")
            print("📋 Check the logs above for details")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CityPulse Master Orchestrator')
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run agents in parallel for faster execution (no cost increase)'
    )
    parser.add_argument(
        '--cache',
        action='store_true',
        help='Use cached data when available (reduces cost for frequent runs)'
    )
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=6,
        help='Cache time-to-live in hours (default: 6)'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cached data before running'
    )
    
    args = parser.parse_args()
    
    # Clear cache if requested
    if args.clear_cache:
        try:
            from cache_manager import get_cache_manager
            cache = get_cache_manager()
            cache.clear_all()
            print("✓ Cache cleared\n")
        except ImportError:
            print("⚠️  Cache manager not found\n")
    
    orchestrator = AgentOrchestrator(
        parallel=args.parallel,
        use_cache=args.cache,
        cache_ttl_hours=args.cache_ttl
    )
    exit_code = orchestrator.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
