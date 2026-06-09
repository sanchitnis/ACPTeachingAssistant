#!/usr/bin/env python3
"""
Usage: compile_check.py <file.c>
Outputs YAML-style compile_status block for inclusion in the context block.
Requires: gcc
"""

import sys
import os
import subprocess
import tempfile

def compile_check(filepath):
    """Compile C file and return YAML-formatted compile status."""
    if not filepath:
        print("ERROR: Usage: compile_check.py <file.c>")
        sys.exit(1)
    
    if not os.path.isfile(filepath):
        print(f"ERROR: File '{filepath}' not found.")
        sys.exit(1)
    
    # Create temporary binary path
    temp_fd, temp_bin = tempfile.mkstemp(prefix='reva_tutor_bin_')
    os.close(temp_fd)
    
    try:
        # Attempt to compile
        result = subprocess.run(
            ['gcc', '-Wall', '-Wextra', '-Wpedantic', '-std=c99', '-o', temp_bin, filepath],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Compilation successful
            output = ["compile_status: OK"]
            
            # Check for warnings
            warn_result = subprocess.run(
                ['gcc', '-Wall', '-Wextra', '-std=c99', '-fsyntax-only', filepath],
                capture_output=True,
                text=True
            )
            
            if warn_result.stderr:
                output.append("compile_warnings: |")
                for line in warn_result.stderr.strip().split('\n'):
                    output.append(f"  {line}")
            
            # Copy to stable path for grade.sh compatibility
            stable_bin = os.path.join(tempfile.gettempdir(), 'reva_tutor_bin')
            try:
                with open(temp_bin, 'rb') as src, open(stable_bin, 'wb') as dst:
                    dst.write(src.read())
            except:
                pass
            
            return '\n'.join(output)
        else:
            # Compilation failed
            output = ["compile_status: ERROR", "compile_output: |"]
            for line in result.stderr.strip().split('\n'):
                output.append(f"  {line}")
            return '\n'.join(output)
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_bin):
            try:
                os.remove(temp_bin)
            except:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Usage: compile_check.py <file.c>")
        sys.exit(1)
    
    result = compile_check(sys.argv[1])
    print(result)
