import sys
import argparse
from backtick.backtick import Backtick

def main():
    if len(sys.argv) == 1:
        print("Hello from the Backtick programming language!")
        sys.exit(0)

    bt = Backtick()

    parser = argparse.ArgumentParser(description="Command line tool for the Backtick programming language.")
    parser.add_argument("command", choices=["run", "run_without_warning"],help="Command to run.")
    parser.add_argument("filepath", type=str,help="Path to run.")
    args = parser.parse_args()

    if args.command == "run":
        try:
            with open(args.filepath, 'r') as file:
                content = file.read()
        except Exception as e:
            print(f"ERROR: Could not read file: {e}")
            sys.exit(1)

        tokens_obj = bt.tokenize(str(content))

        if tokens_obj[2] == False:
            print(f"ERROR: {tokens_obj[0]}")
            sys.exit(1)
        
        if tokens_obj[1] == True:
            input("This program can access your files and make web requests. If you do not trust this program, do not run it. To exit, type Control-C or close the window. To continue, press return: ")

        try:  
            result = bt.run(tokens_obj[0])
        except Exception as e:
            print(f"ERROR: Runtime error: {e}")
            sys.exit(1)
        
        if result[1] == False:
            print(f"ERROR: {result[0]}")
            sys.exit(1)

    elif args.command == "run_without_warning":
        try:
            with open(args.filepath, 'r') as file:
                content = file.read()
        except Exception as e:
            print(f"ERROR: Could not read file: {e}")
            sys.exit(1)

        tokens_obj = bt.tokenize(str(content))

        if tokens_obj[2] == False:
            print(f"ERROR: {tokens_obj[0]}")
            sys.exit(1)
        
        try:  
            result = bt.run(tokens_obj[0])
        except Exception as e:
            print(f"ERROR: Runtime error: {e}")
            sys.exit(1)
        
        if result[1] == False:
            print(f"ERROR: {result[0]}")
            sys.exit(1)
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"Program running canceled by user.")
        sys.exit(0)