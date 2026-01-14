import argparse
import sys
import wpyreg.diff
import os

def save_to_file(file_path: str, dump: wpyreg.diff.RegistryDump | wpyreg.diff.Key):
    print(f"File specified: {file_path}. Saving...")
    if file_path.endswith(".pkl") or file_path.endswith(".pickle"):
        with open(file_path, 'wb') as file:
            file.write(dump.to_pickle())
    else:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(dump.to_json())
    print(f"Dump saved to: {file_path}.")
    return None


def dump_registry() -> wpyreg.diff.RegistryDump:
    print("Dumping registry...")
    dump = wpyreg.diff.dump_registry(True, True)
    print("Dump finished.")

    return dump

def dump_key(key_path: str) -> wpyreg.diff.Key | None:
    print(f"Dumping key: {key_path}...")
    dump = wpyreg.diff.dump_key(key_path, True, True)
    print(f"Dump finished.")

    if dump is None:
        print("Key doesn't exist or not supported. Key won't be dumped.")
        return None

    if isinstance(dump, Exception):
        print(f"Error while key dumping. Key won't be dumped. Message: {dump}")
        return None

    return dump
    
   
def main():
    parser = argparse.ArgumentParser(description="Wojciech's Python Windows Registry Utilities ")
    if False: # For development purposes
        parser.add_argument('-gk', '--generate-key-data-types', action='store_true', help="Generate KeyDataType enumeration from pyreg/key_data_types.json")
    parser.add_argument('-dr', '--dump-registry', action='store_true', help="Dump registry to a file or print if none specified")
    parser.add_argument('-dk', '--dump-key', type=str, help="Dump registry key to file or print if none specified")
    parser.add_argument('--diff',  action='store_true', help="Generate diff between two keys or registries")
    parser.add_argument('-o',  '--output-file', type=str, default=None, help="Dump file path")
    
    args = parser.parse_args(args = None if sys.argv[1:] else ['--help'])
    if len(args) == 0:
        parser.print_help()
        return 0

    file_path = args.output_file
    if file_path is not None:
        file_path = os.path.realpath(file_path)

    if False and args.generate_key_data_types: # For development purposes
        import pyreg._key_data_types_generator
        wpyreg._key_data_types_generator.generate_key_data_types()

    if args.dump_registry and not args.diff:
        reg_dump = dump_registry()
        if file_path is not None:
            save_to_file(file_path, reg_dump)

    if args.dump_key and not args.diff:
        key = dump_key(args.dump_key)
        if key is not None and file_path is not None:
            save_to_file(file_path, key)

    if args.diff:
        before: wpyreg.diff.Key | wpyreg.diff.RegistryDump | None
        after: wpyreg.diff.Key | wpyreg.diff.RegistryDump | None
        if args.dump_key:
            before = dump_key(args.dump_key)
            input("Do action with registry and press enter.")
            after = dump_key(args.dump_key)
        elif args.dump_registry:
            before = dump_registry()
            input("Do action with registry and press enter.")
            after = dump_registry()
        else:
            print("[ERROR] KeyPath or Registry parameter must be specified")
            return
        if before is None:
            print("[ERROR] before dump has error")
            return
        if after is None:
            print("[ERROR] after dump has error")
            return

        def _traverse_key(key_data: wpyreg.diff.Key, output: dict[str, str]):
            for value in key_data.values:
                output[f'{key_data.full_path()}'] = value.to_string()
            for _, key in key_data.children.items():
                _traverse_key(key, output)

        def _generate_paths_set(diff_data: dict[str, wpyreg.diff.Key]):
            output: dict[str, str] = {}
            for _, value in diff_data.items():
                _traverse_key(value, output)
            return output
        
        before_diff_data: dict[str, wpyreg.diff.Key] = {}
        if isinstance(before, wpyreg.diff.RegistryDump):
            before_diff_data = before.get_filtered_tree()
        else:
            before_diff_data = { before.name: before }

        after_diff_data: dict[str, wpyreg.diff.Key] = {}
        if isinstance(after, wpyreg.diff.RegistryDump):
            after_diff_data = after.get_filtered_tree()
        else:
            after_diff_data = { after.name: after }
        
        print("[INFO] Preparing 'before' data")
        before_dict = _generate_paths_set(before_diff_data)
        print("[INFO] Preparing 'after' data")
        after_dict = _generate_paths_set(after_diff_data)

        print("[INFO] Calculating diff")
        output_lines = []
        with open(file_path, "w", encoding="UTF-8") as file:
            for before_key, before_value in before_dict.items():
                after_val = after_dict.get(before_key)
                if after_val != before_value:
                    output_lines.append(f"BA_DIFF: {before_key}\n    {before_value}\n    {after_val}")

            for before_key, before_value in before_dict.items():
                after_val = after_dict.get(before_key)
                if after_val is None:
                    output_lines.append(f"PB_NPA: {before_key}\n    {before_value}")

            for after_key, after_value in after_dict.items():
                before_value = before_dict.get(after_key)
                if before_value is None:
                    output_lines.append(f"PA_NPB: {after_key}\n    {after_value}")
        
        print("[INFO] Diff calculated")
        output_text = '\n'.join(output_lines)
        if file_path is None:
            print(output_text) 
            return
        
        print(f"[Info] Saving diff to {file_path}")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(output_text)
        print(f"[Info] Diff saved to {file_path}")

if __name__ == "__main__":
    exit(main())