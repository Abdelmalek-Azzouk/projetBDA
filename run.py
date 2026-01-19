import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Plateforme Optimisation EDT Examens")
    print("=" * 60)
    print("\nURL: http://localhost:8080")
    print("Arrêt: Ctrl+C\n")
    print("=" * 60 + "\n")
    
    if not os.path.exists('data/university.db'):
        print("Base de données manquante. Initialisation...\n")
        subprocess.run([sys.executable, 'scripts/generate_data.py'])
    
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 
        'app.py',
        '--server.port=8080',
        '--server.headless=true',
        '--browser.gatherUsageStats=false'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nApplication arrêtée.")

if __name__ == '__main__':
    main()