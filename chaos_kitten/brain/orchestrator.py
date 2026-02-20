"""The Brain Orchestrator - Main agent logic using LangGraph."""

from typing import Any, Dict, List
from pathlib import Path
import time


class Orchestrator:
    """Main agent orchestrator that coordinates attacks.
    
    This class uses LangGraph to create an agentic workflow that:
    1. Parses the OpenAPI spec
    2. Plans attack strategies
    3. Executes attacks
    4. Analyzes results
    5. Generates reports
    """
    
    def __init__(self, config: Dict[str, Any], resume: bool = False) -> None:
        """Initialize the orchestrator.
        
        Args:
            config: Configuration dictionary from chaos-kitten.yaml
            resume: Whether to resume from a previous checkpoint
        """
        self.config = config
        self.resume = resume
        
        # State tracking
        self.completed_profiles: List[str] = []
        self.vulnerabilities: List[Dict[str, Any]] = []
        
        # Import here to avoid circular dependencies
        from chaos_kitten.utils.checkpoint import load_checkpoint, calculate_config_hash
        
        self.checkpoint_path = Path(config.get("checkpoint_path", ".chaos-checkpoint.json"))
        
        if self.resume:
            checkpoint = load_checkpoint(self.checkpoint_path)
            if checkpoint:
                current_hash = calculate_config_hash(config)
                if checkpoint.config_hash == current_hash:
                    print(f"🔄 Resuming scan from {time.ctime(checkpoint.timestamp)}")
                    self.completed_profiles = checkpoint.completed_profiles
                    self.vulnerabilities = checkpoint.vulnerabilities
                else:
                    print("⚠️  Config changed! Invalidating checkpoint and starting fresh.")
            else:
                print("⚠️  No valid checkpoint found. Starting fresh.")

    async def run(self) -> Dict[str, Any]:
        """Run the full security scan.
        
        Returns:
            Scan results including vulnerabilities found
        """
        from chaos_kitten.utils.checkpoint import save_checkpoint, clean_checkpoint, CheckpointData, calculate_config_hash
        import time
        from chaos_kitten.paws.executor import Executor
        
        target_url = self.config.get("target", {}).get("base_url")
        if not target_url:
            raise ValueError("Target URL not configured")
            
        print(f"🚀 Starting scan against {target_url}")
        
        # Simulate attack profiles (since parser/planner aren't fully implemented yet)
        attack_profiles = ["sql_injection", "xss", "idor", "broken_auth", "ssrf"]
        
        # Filter out already completed profiles if resuming
        remaining_profiles = [p for p in attack_profiles if p not in self.completed_profiles]
        
        if not remaining_profiles:
            print("✨ All profiles already completed!")
            return {"vulnerabilities": self.vulnerabilities}
            
        for profile in remaining_profiles:
            print(f"\n⚡ Running attack profile: {profile}")
            
            # TODO: Actual attack logic here
            # For now, simulate work and finding vulnerabilities
            await self._simulate_attack(profile)
            
            self.completed_profiles.append(profile)
            
            # Save checkpoint
            checkpoint = CheckpointData(
                target_url=target_url,
                config_hash=calculate_config_hash(self.config),
                completed_profiles=self.completed_profiles,
                vulnerabilities=self.vulnerabilities,
                timestamp=time.time()
            )
            save_checkpoint(checkpoint, self.checkpoint_path)
            print(f"💾 Checkpoint saved after {profile}")
            
        # Clean up checkpoint on successful completion
        clean_checkpoint(self.checkpoint_path)
        print("\n✅ Scan completed successfully! Checkpoint cleaned up.")
            
        return {"vulnerabilities": self.vulnerabilities}

    async def _simulate_attack(self, profile: str) -> None:
        """Simulate an attack profile for demonstration."""
        import asyncio
        import random
        
        # Simulate work
        await asyncio.sleep(1)
        
        # Simulate finding a vulnerability occasionally
        if random.random() < 0.3:
            vuln = {
                "type": profile,
                "severity": "high",
                "description": f"Found a {profile} vulnerability!"
            }
            self.vulnerabilities.append(vuln)
            print(f"🔥 FOUND VULNERABILITY: {profile}")
