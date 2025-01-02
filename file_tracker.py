import argparse
import configparser
import hashlib
import json
import os

config_environ_key = 'FILE_TRACKER_CONFIG'

guess_config_paths = [
    'instance/file_tracker.ini',
]

def calculate_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_folder(directory):
    """
    Walk through all files and hash them
    """
    state = {}
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, directory)
            state[relative_path] = calculate_file_hash(filepath)
    return state

def load_state(state_file):
    """
    Load the saved state from disk
    """
    state = {}
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
    return state

def save_state(state, state_file):
    """
    Save the current state to disk
    """
    with open(state_file, 'w') as f:
        json.dump(state, f)

def compare_states(old_state, new_state):
    added = []
    modified = []
    deleted = []

    # Find added and modified files
    for file, new_hash in new_state.items():
        if file not in old_state:
            added.append(file)
        elif old_state[file] != new_hash:
            modified.append(file)

    # Find deleted files
    for file in old_state:
        if file not in new_state:
            deleted.append(file)

    return (added, modified, deleted)

def track_changes(tracked_dir, state_file):
    """
    Find changes to directory using previously saved file hashes.
    """
    current_state = scan_folder(tracked_dir)
    saved_state = load_state(state_file)

    added, modified, deleted = compare_states(saved_state, current_state)

    if not (added or modified or deleted):
        print("No changes detected.")
    else:
        if added:
            print("Added files:")
            for file in added:
                print(f"  + {file}")
        if modified:
            print("Modified files:")
            for file in modified:
                print(f"  ~ {file}")
        if deleted:
            print("Deleted files:")
            for file in deleted:
                print(f"  - {file}")

    ## Save the new state
    #save_state(current_state, state_file)

def main(argv=None):
    """
    Command line interface.
    """
    parser = argparse.ArgumentParser(
        description = 'Track directory changes by hashing files.',
    )
    parser.add_argument(
        '--config',
        help = 'Configuration file.',
    )
    args = parser.parse_args(argv)

    # Resolve configuration path.
    if args.config:
        config_path = args.config
    else:
        if config_environ_key in os.environ:
            config_path = os.environ[config_environ_key]
        elif guess_config_paths:
            for guess_path in guess_config_paths:
                if os.path.exists(guess_path):
                    config_path = guess_path
                    break

    cp = configparser.ConfigParser()
    cp.read(config_path)

    file_tracker_section = cp['file_tracker']

    tracked_dir = file_tracker_section['tracked_dir']
    state_file = file_tracker_section['state_file']

    track_changes(tracked_dir, state_file)

if __name__ == '__main__':
    main()
