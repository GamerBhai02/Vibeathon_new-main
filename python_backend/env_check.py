"""Environment variable validation for the application."""
import os
import sys
from typing import Dict, List, Tuple

def check_env_var(var_name: str, required: bool = True, default: str = None) -> Tuple[bool, str]:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    
    if value:
        return True, f"✓ {var_name}: Set"
    elif default:
        return True, f"⚠ {var_name}: Not set (using default: {default})"
    elif required:
        return False, f"✗ {var_name}: REQUIRED but not set"
    else:
        return True, f"○ {var_name}: Optional, not set"

def validate_environment() -> Dict[str, List[str]]:
    """Validate all environment variables."""
    results = {
        "errors": [],
        "warnings": [],
        "info": []
    }
    
    # Required environment variables
    required_vars = [
        ("GEMINI_API_KEY", True, None),
    ]
    
    # Optional environment variables with defaults
    optional_vars = [
        ("DATABASE_URL", False, "sqlite:///./agentverse.db"),
        ("CHROMA_DB_PATH", False, "./chroma_db"),
        ("CORS_ORIGINS", False, "http://localhost:3000,http://localhost:5173"),
        ("JWT_SECRET", False, "dev-secret-change-in-production"),
        ("JUDGE0_API_URL", False, None),
        ("JUDGE0_API_KEY", False, None),
        ("YOUTUBE_API_KEY", False, None),
    ]
    
    print("=" * 60)
    print("Environment Variable Validation")
    print("=" * 60)
    print()
    
    # Check required variables
    print("Required Variables:")
    for var_name, required, default in required_vars:
        success, message = check_env_var(var_name, required, default)
        print(f"  {message}")
        if not success:
            results["errors"].append(message)
    
    print()
    print("Optional Variables:")
    for var_name, required, default in optional_vars:
        success, message = check_env_var(var_name, required, default)
        print(f"  {message}")
        if "⚠" in message:
            results["warnings"].append(message)
        else:
            results["info"].append(message)
    
    print()
    print("=" * 60)
    
    if results["errors"]:
        print(f"❌ Validation FAILED: {len(results['errors'])} required variable(s) missing")
        for error in results["errors"]:
            print(f"   {error}")
        return results
    
    if results["warnings"]:
        print(f"⚠️  {len(results['warnings'])} optional variable(s) using defaults")
    
    print("✅ Environment validation passed!")
    print("=" * 60)
    
    return results

def print_setup_instructions():
    """Print setup instructions for missing variables."""
    print()
    print("Setup Instructions:")
    print("-" * 60)
    print("1. Create a .env file in the project root:")
    print("   cp .env.example .env")
    print()
    print("2. Add your API keys:")
    print("   GEMINI_API_KEY=your_gemini_api_key_here")
    print("   YOUTUBE_API_KEY=your_youtube_api_key_here  # Optional")
    print("   JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com  # Optional")
    print("   JUDGE0_API_KEY=your_judge0_api_key_here  # Optional")
    print()
    print("3. Configure database (optional):")
    print("   DATABASE_URL=sqlite:///./agentverse.db")
    print("   CHROMA_DB_PATH=./chroma_db")
    print()
    print("4. Configure JWT secret (recommended for production):")
    print("   JWT_SECRET=your-secret-jwt-key-change-in-production")
    print()
    print("5. Configure CORS (optional):")
    print("   CORS_ORIGINS=http://localhost:3000,http://localhost:5173")
    print("-" * 60)

if __name__ == "__main__":
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file")
        print()
    except ImportError:
        print("python-dotenv not installed, skipping .env file")
        print()
    
    results = validate_environment()
    
    if results["errors"]:
        print()
        print_setup_instructions()
        sys.exit(1)
    
    sys.exit(0)
