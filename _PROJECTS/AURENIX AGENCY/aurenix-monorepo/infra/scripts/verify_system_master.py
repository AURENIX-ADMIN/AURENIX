import requests
import subprocess
import time
import sys
import os

def check_url(name, url, expected_status=200):
    print(f"🔍 Checking {name} at {url}...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ PASS: {name} is UP ({response.status_code})")
            return True
        else:
            print(f"❌ FAIL: {name} returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {name} unreachable. Error: {e}")
        return False

def check_docker_container(container_name_part):
    print(f"🔍 Checking Docker container matching '{container_name_part}'...")
    try:
        # Get ID
        result = subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name_part}"], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ PASS: Container {container_name_part} is RUNNING.")
            return result.stdout.strip()
        else:
            print(f"❌ FAIL: Container {container_name_part} is NOT running.")
            return None
    except Exception as e:
        print(f"❌ FAIL: Docker check failed: {e}")
        return None

def run_internal_verification(container_id, script_path):
    print(f"🔍 Running internal verification inside {container_id}...")
    # First copy the script
    try:
        # Copy
        copy_cmd = ["docker", "cp", script_path, f"{container_id}:/app/verify_internal.py"]
        subprocess.run(copy_cmd, check=True)
        
        # Exec
        exec_cmd = ["docker", "exec", container_id, "python", "/app/verify_internal.py"]
        result = subprocess.run(exec_cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        if result.returncode == 0:
            print("✅ PASS: Internal Verification PASSED.")
            return True
        else:
            print("❌ FAIL: Internal Verification FAILED.")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Execution failed: {e}")
        return False

def main():
    print("🚀 AURENIX AGENCY SYSTEM VERIFICATION")
    print("="*40)
    
    # 1. API Gateway
    gateway_ok = check_url("API Gateway", "http://localhost:8000/health")
    
    # 2. Web Portal
    web_ok = check_url("Web Portal", "http://localhost:3000") # Might return 200 or redirect
    
    # 3. Temporal Worker Logic (LLM)
    worker_id = check_docker_container("temporal-worker")
    worker_ok = False
    if worker_id:
        # Path to the script we created earlier
        script_path = os.path.join(os.getcwd(), "infra", "scripts", "verify_lead_hunter_llm.py")
        if os.path.exists(script_path):
            worker_ok = run_internal_verification(worker_id, script_path)
        else:
            print(f"⚠️ WARN: Verification script not found at {script_path}")
            
    # Summary
    print("\n📊 VERIFICATION SUMMARY")
    print("="*40)
    print(f"API Gateway:   {'✅' if gateway_ok else '❌'}")
    print(f"Web Portal:    {'✅' if web_ok else '❌'}")
    print(f"Temporal Worker: {'✅' if worker_ok else '❌'}")
    
    if gateway_ok and web_ok and worker_ok:
        print("\n🏆 SYSTEM READY FOR MARKET")
    else:
        print("\n⚠️ SYSTEM HAS ISSUES")

if __name__ == "__main__":
    main()
