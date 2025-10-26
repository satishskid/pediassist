"""
Cost tracking for LLM usage
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import structlog
from pathlib import Path

logger = structlog.get_logger()

@dataclass
class UsageRecord:
    """Record of LLM usage"""
    timestamp: datetime
    provider: str
    model: str
    tokens_used: int
    cost_usd: float
    request_type: str  # 'treatment_plan', 'communication', 'delegation'
    success: bool
    response_time_ms: Optional[int] = None

class CostTracker:
    """Tracks LLM usage costs and enforces limits"""
    
    def __init__(self, config):
        self.config = config
        self.usage_records: List[UsageRecord] = []
        self.monthly_budget = getattr(config, 'monthly_budget', 100.0)
        self.daily_budget = getattr(config, 'daily_budget', 10.0)
        self.cost_per_token = self._get_cost_per_token()
        
        # Storage for usage data
        data_dir = getattr(config, 'data_dir', Path('data'))
        self.usage_file = Path(data_dir) / "usage.json"
        self._load_usage_data()
    
    def _get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per token for different providers and models"""
        return {
            "openai": {
                "gpt-4": 0.03 / 1000,  # $0.03 per 1K tokens
                "gpt-4-turbo": 0.01 / 1000,
                "gpt-3.5-turbo": 0.002 / 1000,
            },
            "anthropic": {
                "claude-3-opus": 0.015 / 1000,
                "claude-3-sonnet": 0.003 / 1000,
                "claude-3-haiku": 0.00025 / 1000,
            },
            "azure_openai": {
                "gpt-4": 0.03 / 1000,
                "gpt-35-turbo": 0.002 / 1000,
            },
            "google": {
                "gemini-pro": 0.0005 / 1000,
                "gemini-pro-vision": 0.0025 / 1000,
            },
            "ollama": {
                "llama2": 0.0,  # Local model, no cost
                "mistral": 0.0,
                "codellama": 0.0,
            },
            "local": {
                "local-model": 0.0,  # Local model, no cost
            }
        }
    
    def calculate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Calculate cost for a request"""
        provider_costs = self.cost_per_token.get(provider, {})
        cost_per_token = provider_costs.get(model, 0.01 / 1000)  # Default fallback
        
        return tokens * cost_per_token
    
    async def track_request(
        self,
        provider: str,
        model: str,
        tokens_used: int,
        cost_usd: float,
        request_type: str,
        success: bool = True,
        response_time_ms: Optional[int] = None
    ):
        """Track a request for cost and usage monitoring"""
        
        record = UsageRecord(
            timestamp=datetime.utcnow(),
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            request_type=request_type,
            success=success,
            response_time_ms=response_time_ms
        )
        
        self.usage_records.append(record)
        
        # Persist to file
        self._save_usage_data()
        
        logger.info(
            "LLM usage tracked",
            provider=provider,
            model=model,
            tokens=tokens_used,
            cost_usd=cost_usd,
            request_type=request_type,
            success=success
        )
    
    async def can_make_request(self, estimated_cost: Optional[float] = None) -> bool:
        """Check if a request can be made within budget constraints"""
        
        # Check monthly budget
        monthly_usage = self.get_monthly_usage()
        if monthly_usage >= self.monthly_budget:
            logger.warning("Monthly budget exceeded", monthly_usage=monthly_usage, budget=self.monthly_budget)
            return False
        
        # Check daily budget
        daily_usage = self.get_daily_usage()
        if daily_usage >= self.daily_budget:
            logger.warning("Daily budget exceeded", daily_usage=daily_usage, budget=self.daily_budget)
            return False
        
        # Check if estimated cost would exceed budget
        if estimated_cost:
            if monthly_usage + estimated_cost > self.monthly_budget:
                logger.warning("Request would exceed monthly budget", 
                             current_usage=monthly_usage, 
                             estimated_cost=estimated_cost,
                             budget=self.monthly_budget)
                return False
            
            if daily_usage + estimated_cost > self.daily_budget:
                logger.warning("Request would exceed daily budget",
                             current_usage=daily_usage,
                             estimated_cost=estimated_cost,
                             budget=self.daily_budget)
                return False
        
        return True
    
    def get_monthly_usage(self) -> float:
        """Get total usage for current month"""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = sum(
            record.cost_usd for record in self.usage_records
            if record.timestamp >= start_of_month and record.success
        )
        
        return monthly_usage
    
    def get_daily_usage(self) -> float:
        """Get total usage for current day"""
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        daily_usage = sum(
            record.cost_usd for record in self.usage_records
            if record.timestamp >= start_of_day and record.success
        )
        
        return daily_usage
    
    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the specified period"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Filter records for the period
        period_records = [
            record for record in self.usage_records
            if start_date <= record.timestamp <= end_date
        ]
        
        # Calculate statistics
        total_requests = len(period_records)
        successful_requests = sum(1 for record in period_records if record.success)
        total_tokens = sum(record.tokens_used for record in period_records)
        total_cost = sum(record.cost_usd for record in period_records)
        
        # Provider breakdown
        provider_stats = {}
        for record in period_records:
            if record.provider not in provider_stats:
                provider_stats[record.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0,
                    "success_rate": 0.0
                }
            
            provider_stats[record.provider]["requests"] += 1
            provider_stats[record.provider]["tokens"] += record.tokens_used
            provider_stats[record.provider]["cost"] += record.cost_usd
        
        # Calculate success rates
        for provider, stats in provider_stats.items():
            provider_records = [r for r in period_records if r.provider == provider]
            successful = sum(1 for r in provider_records if r.success)
            stats["success_rate"] = successful / len(provider_records) if provider_records else 0.0
        
        # Request type breakdown
        request_type_stats = {}
        for record in period_records:
            if record.request_type not in request_type_stats:
                request_type_stats[record.request_type] = {
                    "requests": 0,
                    "cost": 0.0,
                    "avg_tokens": 0
                }
            
            request_type_stats[record.request_type]["requests"] += 1
            request_type_stats[record.request_type]["cost"] += record.cost_usd
        
        # Calculate averages
        for request_type, stats in request_type_stats.items():
            type_records = [r for r in period_records if r.request_type == request_type]
            stats["avg_tokens"] = sum(r.tokens_used for r in type_records) / len(type_records) if type_records else 0
        
        # Response time statistics
        response_times = [r.response_time_ms for r in period_records if r.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0.0,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "avg_cost_per_request": total_cost / total_requests if total_requests > 0 else 0.0,
            "avg_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0.0,
            "avg_response_time_ms": avg_response_time,
            "provider_breakdown": provider_stats,
            "request_type_breakdown": request_type_stats,
            "budget_status": {
                "monthly_budget": self.monthly_budget,
                "monthly_usage": self.get_monthly_usage(),
                "monthly_remaining": self.monthly_budget - self.get_monthly_usage(),
                "daily_budget": self.daily_budget,
                "daily_usage": self.get_daily_usage(),
                "daily_remaining": self.daily_budget - self.get_daily_usage()
            }
        }
    
    def _load_usage_data(self):
        """Load usage data from file"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    
                    # Convert back to UsageRecord objects
                    self.usage_records = []
                    for record_data in data.get("records", []):
                        record = UsageRecord(
                            timestamp=datetime.fromisoformat(record_data["timestamp"]),
                            provider=record_data["provider"],
                            model=record_data["model"],
                            tokens_used=record_data["tokens_used"],
                            cost_usd=record_data["cost_usd"],
                            request_type=record_data["request_type"],
                            success=record_data["success"],
                            response_time_ms=record_data.get("response_time_ms")
                        )
                        self.usage_records.append(record)
                
                logger.info(f"Loaded {len(self.usage_records)} usage records")
                
        except Exception as e:
            logger.error(f"Failed to load usage data: {e}")
            self.usage_records = []
    
    def _save_usage_data(self):
        """Save usage data to file"""
        try:
            # Convert to serializable format
            data = {
                "records": [
                    {
                        "timestamp": record.timestamp.isoformat(),
                        "provider": record.provider,
                        "model": record.model,
                        "tokens_used": record.tokens_used,
                        "cost_usd": record.cost_usd,
                        "request_type": record.request_type,
                        "success": record.success,
                        "response_time_ms": record.response_time_ms
                    }
                    for record in self.usage_records
                ],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Ensure directory exists
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up old usage records to prevent file bloat"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        old_count = len(self.usage_records)
        self.usage_records = [
            record for record in self.usage_records
            if record.timestamp >= cutoff_date
        ]
        
        new_count = len(self.usage_records)
        logger.info(f"Cleaned up usage records: {old_count - new_count} records removed, {new_count} kept")
        
        # Save cleaned data
        self._save_usage_data()