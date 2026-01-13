#!/usr/bin/env python3
"""
tee-safe - A no-clobber wrapper around tee functionality
Prevents overwriting existing files unless -f (force) is used
"""
import sys
import os
import argparse
import signal

def main():
    parser = argparse.ArgumentParser(
        description='Copy standard input to each FILE, and also to standard output. '
                    'Fails if any FILE already exists (unless -f is used).',
        epilog='All standard tee functionality with added no-clobber protection.',
        add_help=False
    )
    
    # tee-safe specific options
    parser.add_argument('-f', '--force', action='store_true',
                       help='Allow overwriting existing files')
    
    # Standard tee options
    parser.add_argument('-a', '--append', action='store_true',
                       help='Append to the given FILEs, do not overwrite')
    parser.add_argument('-i', '--ignore-interrupts', action='store_true',
                       help='Ignore interrupt signals')
    parser.add_argument('--help', action='store_true',
                       help='Display this help and exit')
    parser.add_argument('--version', action='store_true',
                       help='Output version information and exit')
    
    # Files
    parser.add_argument('files', nargs='*', metavar='FILE',
                       help='Output file(s)')
    
    args = parser.parse_args()
    
    # Handle --help
    if args.help:
        print("""Usage: tee-safe [OPTION]... [FILE]...

Copy standard input to each FILE, and also to standard output.
Fails if any FILE already exists (unless -f is used).

Options:
  -f, --force              Allow overwriting existing files
  -a, --append             Append to files instead of overwriting
  -i, --ignore-interrupts  Ignore interrupt signals
      --help               Display this help and exit
      --version            Output version information and exit

Examples:
  echo "test" | tee-safe file.txt
  ls | tee-safe output.txt | grep foo
  echo "data" | tee-safe -a existing.txt  # Append is always safe
  echo "test" | tee-safe -f file.txt      # Force overwrite

Exit status:
  0   Success
  1   File exists (no-clobber violation)
  2+  Other errors

Report bugs to: <your-email>
""")
        return 0
    
    # Handle --version
    if args.version:
        print("tee-safe 1.0 (Python)")
        print("A no-clobber wrapper for tee functionality")
        return 0
    
    # Set up signal handling
    if args.ignore_interrupts:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    # Check for file existence (unless forcing or appending)
    if not args.force and not args.append:
        for filepath in args.files:
            if os.path.exists(filepath):
                print(f"tee-safe: {filepath}: File exists (use -f to overwrite)", 
                      file=sys.stderr)
                return 1
    
    # Open output files
    mode = 'a' if args.append else 'w'
    file_handles = []
    
    try:
        for filepath in args.files:
            try:
                fh = open(filepath, mode)
                file_handles.append(fh)
            except IOError as e:
                print(f"tee-safe: {filepath}: {e.strerror}", file=sys.stderr)
                # Close already opened files
                for fh in file_handles:
                    fh.close()
                return 1
        
        # Read from stdin and write to stdout and files
        try:
            for line in sys.stdin:
                # Write to stdout
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # Write to all files
                for fh in file_handles:
                    try:
                        fh.write(line)
                        fh.flush()
                    except IOError as e:
                        print(f"tee-safe: write error: {e.strerror}", 
                              file=sys.stderr)
                        # Continue writing to other files
        
        except KeyboardInterrupt:
            if not args.ignore_interrupts:
                raise
        
        finally:
            # Close all files
            for fh in file_handles:
                try:
                    fh.close()
                except:
                    pass
        
        return 0
    
    except Exception as e:
        print(f"tee-safe: error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())