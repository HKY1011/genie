#!/usr/bin/env python3
"""
Quick health check for Genie Backend components
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_components():
    """Check if all components are working"""
    print("🔍 Genie Backend Health Check")
    print("=" * 40)
    
    checks = []
    
    # Check 1: Task Model
    try:
        from models.task_model import Task, TaskStatus
        task = Task("Health Check Task", "Testing task creation")
        checks.append(("Task Model", True, "✅ Task creation successful"))
    except Exception as e:
        checks.append(("Task Model", False, f"❌ Error: {e}"))
    
    # Check 2: JsonStore
    try:
        from storage.json_store import JsonStore
        store = JsonStore("health_check_data")
        checks.append(("JsonStore", True, "✅ Storage initialization successful"))
        import shutil
        shutil.rmtree("health_check_data", ignore_errors=True)
    except Exception as e:
        checks.append(("JsonStore", False, f"❌ Error: {e}"))
    
    # Check 3: TaskExtractionAgent
    try:
        from agents.task_extraction_agent import TaskExtractionAgent
        agent = TaskExtractionAgent()
        checks.append(("TaskExtractionAgent", True, "✅ Agent initialization successful"))
    except Exception as e:
        checks.append(("TaskExtractionAgent", False, f"❌ Error: {e}"))
    
    # Check 4: PlanningAgent
    try:
        from agents.planning_agent import PlanningAgent
        agent = PlanningAgent()
        checks.append(("PlanningAgent", True, "✅ Agent initialization successful"))
    except Exception as e:
        checks.append(("PlanningAgent", False, f"❌ Error: {e}"))
    
    # Check 5: GenieOrchestrator
    try:
        from agents.genieorchestrator_agent import GenieOrchestrator
        agent = GenieOrchestrator()
        checks.append(("GenieOrchestrator", True, "✅ Agent initialization successful"))
    except Exception as e:
        checks.append(("GenieOrchestrator", False, f"❌ Error: {e}"))
    
    # Check 6: Gemini API Client
    try:
        from integrations.gemini_api import GeminiAPIClient
        # This will fail without API key, but should not crash
        try:
            client = GeminiAPIClient()
            checks.append(("Gemini API Client", True, "✅ API client created"))
        except ValueError:
            checks.append(("Gemini API Client", True, "⚠️  No API key (expected)"))
    except Exception as e:
        checks.append(("Gemini API Client", False, f"❌ Error: {e}"))
    
    # Check 6: Perplexity API Client
    try:
        from integrations.perplexity_api import PerplexityAPIClient
        # This will fail without API key, but should not crash
        try:
            client = PerplexityAPIClient()
            checks.append(("Perplexity API Client", True, "✅ API client created"))
        except ValueError:
            checks.append(("Perplexity API Client", True, "⚠️  No API key (expected)"))
    except Exception as e:
        checks.append(("Perplexity API Client", False, f"❌ Error: {e}"))
    
    # Check 7: Environment Variables
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        env_vars = ["GEMINI_API_KEY", "PERPLEXITY_API_KEY"]
        env_status = []
        for var in env_vars:
            value = os.getenv(var)
            if value and value != f"your_{var.lower()}_here":
                env_status.append(f"✅ {var}: Set")
            else:
                env_status.append(f"⚠️  {var}: Not set")
        checks.append(("Environment Variables", True, " | ".join(env_status)))
    except Exception as e:
        checks.append(("Environment Variables", False, f"❌ Error: {e}"))
    
    # Check 9: Prompt Files
    try:
        extract_prompt = Path("prompts/extract_task.prompt")
        breakdown_prompt = Path("prompts/breakdown_chunk.prompt")
        orchestrator_prompt = Path("prompts/genieorchestrator.prompt")
        
        prompt_status = []
        if extract_prompt.exists():
            prompt_status.append("✅ extract_task.prompt")
        else:
            prompt_status.append("❌ extract_task.prompt")
            
        if breakdown_prompt.exists():
            prompt_status.append("✅ breakdown_chunk.prompt")
        else:
            prompt_status.append("❌ breakdown_chunk.prompt")
            
        if orchestrator_prompt.exists():
            prompt_status.append("✅ genieorchestrator.prompt")
        else:
            prompt_status.append("❌ genieorchestrator.prompt")
            
        checks.append(("Prompt Files", True, " | ".join(prompt_status)))
    except Exception as e:
        checks.append(("Prompt Files", False, f"❌ Error: {e}"))
    
    # Display results
    print("\nComponent Status:")
    print("-" * 40)
    
    all_passed = True
    for component, status, message in checks:
        print(f"{component:<20} {message}")
        if not status:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All components are working correctly!")
        print("\nTo test with real API calls:")
        print("1. Add your API keys to .env file (GEMINI_API_KEY, PERPLEXITY_API_KEY)")
        print("2. Run: python3 test_updated_agent.py (TaskExtractionAgent)")
        print("3. Run: python3 test_planning_agent.py (PlanningAgent)")
        print("4. Run: python3 test_genieorchestrator.py (GenieOrchestrator)")
    else:
        print("⚠️  Some components have issues. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = check_components()
    sys.exit(0 if success else 1) 