import os
import sys
import argparse
from pathlib import Path
import fnmatch


def read_list_file(file_path):
    """
    Read a list file (.il or .wl) and return the list of patterns.
    """
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"List file not found: {file_path}")
        return []

def match_pattern(path, patterns):
    """
    Match a path against a list of glob-style patterns.
    Supports wildcards, folders, and root-relative ignores.
    """
    normalized = path.replace("\\", "/")
    for pattern in patterns or []:
        pattern = pattern.strip()
        if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(normalized + '/', pattern):
            return True
    return False

def save_project_structure_and_files(root_path, output_file, ignore_list=None, whitelist=None):
    """
    Save the project structure and contents of all files in the project to a text file,
    considering ignore and whitelist.
    """
    project_structure = []
    file_contents = []

    for root, dirs, files in os.walk(root_path):
        rel_root = os.path.relpath(root, root_path).replace("\\", "/")

        # Normalize relative paths for filtering
        dirs[:] = [
            d for d in dirs
            if not match_pattern(f"{rel_root}/{d}" if rel_root != '.' else d, ignore_list)
        ]

        files = [
            f for f in files
            if not match_pattern(f"{rel_root}/{f}" if rel_root != '.' else f, ignore_list)
            and (not whitelist or match_pattern(f"{rel_root}/{f}" if rel_root != '.' else f, whitelist))
        ]

        for file in files:
            rel_file = os.path.join(rel_root, file).replace("\\", "/")
            project_structure.append(rel_file)

            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                file_contents.append(f"{rel_file}:\n```\n{content}\n```\n")
            except Exception as e:
                file_contents.append(f"{rel_file}:\n```\nError reading file: {e}\n```\n")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Project Structure:\n")
        f.write("\n".join(project_structure) + "\n\n")
        f.write("File Contents:\n")
        f.write("\n".join(file_contents))

def main():

    project_dir = Path.cwd()
    script_dir = Path(__file__).parent

    il_file = (project_dir / '.il') if (project_dir / '.il').exists() else (script_dir / '.il')
    wl_file = (project_dir / '.wl') if (project_dir / '.wl').exists() else (script_dir / '.wl')

    parser = argparse.ArgumentParser(description="Save project structure and file contents.")
    parser.add_argument("--il", help="Use ignore list (.il file)", action="store_true")
    parser.add_argument("--wl", help="Use whitelist (.wl file)", action="store_true")
    parser.add_argument("--show-locations", help="Show the location of the .il and .wl files", action="store_true")

    args = parser.parse_args()

    if args.show_locations:
        print(f"IL file in use: {il_file} ({'local' if il_file.is_relative_to(project_dir) else 'default'})")
        print(f"WL file in use: {wl_file} ({'local' if wl_file.is_relative_to(project_dir) else 'default'})")
        sys.exit(0)

    ignore_list = read_list_file(il_file) if args.il else None
    whitelist = read_list_file(wl_file) if args.wl else None

    save_project_structure_and_files('.', 'project_contents.txt', ignore_list, whitelist)
