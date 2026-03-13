# -*- coding: utf-8 -*-
"""
CityPulse Agent Utilities
Common functions for path handling, cost logging, and schema standardization
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from filelock import FileLock


# Base directory (agents folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COST_LOG_FILE = os.path.join(BASE_DIR, 'cost_log.json')


def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_data_path(filename: str) -> str:
    """
    Get absolute path to a data file
    
    Args:
        filename: Name of the data file (e.g., 'news.json')
        
    Returns:
        Absolute path to the file in data/ directory
    """
    ensure_data_dir()
    return os.path.join(DATA_DIR, filename)


def load_json_data(filename: str, default: Any = None) -> Any:
    """
    Load JSON data from data/ directory
    
    Args:
        filename: Name of the data file
        default: Default value if file not found (None or [] or {})
        
    Returns:
        Loaded JSON data or default value
    """
    filepath = get_data_path(filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
            return content
    except FileNotFoundError:
        print(f"⚠️  File not found: {filename}")
        return default if default is not None else []
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON: {filename}")
        return default if default is not None else []


def save_json_data(filename: str, data: Any):
    """
    Save JSON data to data/ directory
    
    Args:
        filename: Name of the data file
        data: Data to save
    """
    filepath = get_data_path(filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to: {filepath}")


def create_standard_event(
    event_id: str,
    source: str,
    event_type: str,
    location: str,
    description: str,
    severity: str = "medium",
    metadata: Optional[Dict] = None,
    timestamp: Optional[str] = None
) -> Dict:
    """
    Create a standardized event structure
    
    Args:
        event_id: Unique event identifier
        source: Source agent (e.g., 'permit_monitor', 'social_listener')
        event_type: Type of event (e.g., 'permit_event', 'social_discussion')
        location: Location of the event
        description: Event description
        severity: Severity level (low, medium, high, critical)
        metadata: Additional event-specific data
        timestamp: ISO timestamp (auto-generated if not provided)
        
    Returns:
        Standardized event dictionary
    """
    return {
        "id": event_id,
        "source": source,
        "type": event_type,
        "location": location,
        "timestamp": timestamp or datetime.now().isoformat(),
        "description": description,
        "severity": severity,
        "metadata": metadata or {}
    }


def log_cost(
    agent_name: str,
    tokens_used: int,
    estimated_cost: float,
    model: str = "Amazon Nova",
    operation: str = "analysis",
    **extra_fields
):
    """
    Thread-safe cost logging to prevent concurrent write issues
    
    Args:
        agent_name: Name of the agent (e.g., 'social_listener')
        tokens_used: Total tokens used
        estimated_cost: Estimated cost in USD
        model: Model name
        operation: Operation type
        **extra_fields: Additional fields to include in log entry
    """
    log_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "operation": operation,
        "tokens_used": tokens_used,
        "estimated_cost": estimated_cost,
        **extra_fields
    }
    
    lock_file = COST_LOG_FILE + '.lock'
    
    try:
        # Use file lock to prevent concurrent writes
        with FileLock(lock_file, timeout=10):
            # Load existing logs
            if os.path.exists(COST_LOG_FILE):
                with open(COST_LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Append new entry
            logs.append(log_entry)
            
            # Save updated logs
            with open(COST_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
        
        print(f"💰 Cost logged: ${estimated_cost:.6f}")
        
    except Exception as e:
        print(f"⚠️  Could not log cost: {e}")


def get_total_cost() -> float:
    """
    Get total cost from all logged operations
    
    Returns:
        Total cost in USD
    """
    try:
        if os.path.exists(COST_LOG_FILE):
            with open(COST_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return sum(log.get('estimated_cost', 0) for log in logs)
        return 0.0
    except:
        return 0.0


# Legacy path compatibility (for gradual migration)
def get_legacy_path(relative_path: str) -> str:
    """
    Get absolute path for legacy relative paths
    
    Args:
        relative_path: Old-style relative path (e.g., 'news-synthesis/analyzed_news.json')
        
    Returns:
        Absolute path
    """
    return os.path.join(BASE_DIR, relative_path)
