#!/usr/bin/env python3
"""
Standalone Smart Log Analyzer
Wraps any command, captures output, detects errors, and provides AI-powered solutions.
"""
import sys
import subprocess
import argparse
from collections import deque

# Error detection patterns
ERROR_KEYWORDS = [
    "ERROR", "CRITICAL", "EXCEPTION", "TRACEBACK", 
    "FAILED", "FATAL", "PANIC", "CRASH"
]

class TriageWrapper:
    def __init__(self, buffer_size=100):
        self.buffer = deque(maxlen=buffer_size)
        self.error_detected = False
        self.error_lines = []
        
    def detect_error(self, line):
        """Check if line contains error indicators"""
        line_upper = line.upper()
        return any(keyword in line_upper for keyword in ERROR_KEYWORDS)
    
    def run_command(self, command):
        """Execute command and capture output in real-time"""
        print(f"\n[TRIAGE] Executing: {command}")
        print("=" * 60)
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                    
                line = line.rstrip()
                self.buffer.append(line)
                
                if self.detect_error(line):
                    self.error_detected = True
                    self.error_lines.append(line)
                    print(f"[ERROR]  {line}")
                else:
                    print(f"[OUTPUT] {line}")
            
            process.wait()
            return_code = process.returncode
            
            print("=" * 60)
            
            if self.error_detected:
                self.analyze_errors()
            else:
                print(f"\n[TRIAGE] ✅ Command completed successfully (exit code: {return_code})")
            
            return return_code
            
        except Exception as e:
            print(f"\n[TRIAGE] ❌ Failed to execute command: {e}")
            return 1
    
    def analyze_errors(self):
        """Analyze detected errors and provide solutions"""
        print(f"\n[TRIAGE] ⚠️  Error detected! Analyzing...")
        print()
        
        context = list(self.buffer)[-20:]
        context_str = "\n".join(context)
        
        try:
            # Use new class-based API
            from ai_logmaster.core.analyzer import ErrorAnalyzer
            analyzer = ErrorAnalyzer()
            result = analyzer.analyze(context_str)
            self.display_analysis(result)
        except ImportError:
            # Fallback to old function-based API
            try:
                from ai_logmaster.analyzer import analyze_error
                result = analyze_error(context_str)
                self.display_analysis(result)
            except ImportError:
                self.display_basic_analysis(context_str)
    
    def display_analysis(self, result):
        """Display AI-powered analysis results"""
        method = result.get('method', 'Unknown')
        
        print("╔" + "═" * 58 + "╗")
        print("║ 🔍 DIAGNOSIS" + " " * 45 + "║")
        print("╠" + "═" * 58 + "╣")
        print(f"║ Type: {result.get('type', 'Unknown'):<50} ║")
        print(f"║ Confidence: {result.get('confidence', 0):.0%}" + " " * 44 + "║")
        print(f"║ Method: {method:<49} ║")
        print("╠" + "═" * 58 + "╣")
        
        cause = result.get('cause')
        if cause:
            print("║ 📋 ROOT CAUSE" + " " * 44 + "║")
            print("╠" + "═" * 58 + "╣")
            words = cause.split()
            line = "║ "
            for word in words:
                if len(line) + len(word) + 1 > 57:
                    print(line + " " * (59 - len(line)) + "║")
                    line = "║ " + word
                else:
                    line += (" " if len(line) > 2 else "") + word
            if len(line) > 2:
                print(line + " " * (59 - len(line)) + "║")
            print("╠" + "═" * 58 + "╣")
        
        print("║ 💡 RECOMMENDED FIXES" + " " * 37 + "║")
        print("╠" + "═" * 58 + "╣")
        
        for i, fix in enumerate(result.get('fixes', []), 1):
            if len(fix) > 52:
                words = fix.split()
                line = f"║ {i}. "
                for word in words:
                    if len(line) + len(word) + 1 > 57:
                        print(line + " " * (59 - len(line)) + "║")
                        line = "║    " + word
                    else:
                        line += (" " if len(line) > 5 else "") + word
                if len(line) > 5:
                    print(line + " " * (59 - len(line)) + "║")
            else:
                print(f"║ {i}. {fix:<54} ║")
        
        sources = result.get('sources', [])
        if sources:
            print("╠" + "═" * 58 + "╣")
            print("║ 📚 DOCUMENTATION SOURCES" + " " * 33 + "║")
            print("╠" + "═" * 58 + "╣")
            for source in sources[:3]:
                if len(source) > 54:
                    source = source[:51] + "..."
                print(f"║ • {source:<55} ║")
        
        print("╚" + "═" * 58 + "╝")
    
    def display_basic_analysis(self, context):
        """Display basic analysis without AI"""
        print("╔" + "═" * 58 + "╗")
        print("║ 🔍 BASIC ANALYSIS" + " " * 40 + "║")
        print("╠" + "═" * 58 + "╣")
        
        error_type = "Unknown Error"
        for line in context.split('\n'):
            if 'Error:' in line or 'Exception:' in line:
                error_type = line.split(':')[0].strip()
                break
        
        print(f"║ Type: {error_type:<50} ║")
        print("╠" + "═" * 58 + "╣")
        print("║ 💡 GENERAL RECOMMENDATIONS" + " " * 31 + "║")
        print("╠" + "═" * 58 + "╣")
        print("║ 1. Check the error message above" + " " * 25 + "║")
        print("║ 2. Review recent code changes" + " " * 28 + "║")
        print("║ 3. Search for the error online" + " " * 27 + "║")
        print("║ 4. Check logs for more details" + " " * 27 + "║")
        print("╚" + "═" * 58 + "╝")
        
        print("\n[TRIAGE] 💡 Tip: Install AI analyzer for smarter suggestions!")
        print("[TRIAGE]     pip install langchain langchain-openai")

def init_config():
    """Initialize configuration"""
    from ai_logmaster.config import init_config as do_init
    
    if do_init():
        print("✅ Configuration already exists")
    else:
        print("✅ Configuration initialized")
    
    print("\nNext steps:")
    print("1. Edit ~/.ai-logmaster/config.yaml")
    print("2. Set your API key")
    print("3. Run: logmaster run \"your command\"")

def main():
    parser = argparse.ArgumentParser(
        description="Smart Log Analyzer - Wrap commands and get AI-powered error analysis"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a command with analysis")
    run_parser.add_argument("cmd", help="Command to execute (use quotes)")
    run_parser.add_argument("--buffer", type=int, default=100, 
                           help="Number of lines to buffer (default: 100)")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_config()
    elif args.command == "run":
        wrapper = TriageWrapper(buffer_size=args.buffer)
        exit_code = wrapper.run_command(args.cmd)
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
