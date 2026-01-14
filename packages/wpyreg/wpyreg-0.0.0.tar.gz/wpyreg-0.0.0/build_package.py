import argparse
import os
import subprocess
import shutil

SCRIPT_DIR = os.path.normpath(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/')
BUILD_DIR = f'{SCRIPT_DIR}/.build'

def main():
    parser = argparse.ArgumentParser(description="build_tools release utils")
    parser.add_argument('-c', '--create', default=True, action='store_true', help="Create release package")
    parser.add_argument('-r', '--release', default=True, action='store_true', help="Release package")
    args = parser.parse_args()


    if args.create or args.release:
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)        
        os.makedirs(BUILD_DIR)

        proc = subprocess.run(args=' && '.join([
            "python3 -m build --sdist --wheel --no-isolation --outdir . .."
        ]), shell=True, cwd=BUILD_DIR)

        if proc.returncode != 0:
            print(f"[ERROR] Building package failed. Process code: {proc.returncode}")
            return 1

        shutil.move(f'{SCRIPT_DIR}/wpyreg.egg-info', f'{BUILD_DIR}/wpyreg.egg-info')
        shutil.move(f'{SCRIPT_DIR}/build', f'{BUILD_DIR}/build')

    if args.release:
        proc = subprocess.run(args=' && '.join([
            "twine upload wpyreg-0.0.0.tar.gz wpyreg-0.0.0.tar.gz  --verbose"
        ]), shell=True, cwd=BUILD_DIR)

        if proc.returncode != 0:
            print(f"[ERROR] Building releasing failed. Process code: {proc.returncode}")
            return 1



if __name__ == "__main__":
    exit(main())