
import json
import sys
from pathlib import Path

def main():
    """
    Duplicates a JSON file, adding a postfix to the filename and updating
    an internal value.
    """
    if len(sys.argv) != 3:
        print("Usage: make_waiwera_copy <input.json> <postfix>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    postfix = sys.argv[2]

    if not input_path.exists() or input_path.suffix != '.json':
        print(f"Error: Input file '{input_path}' does not exist or is not a .json file.")
        sys.exit(1)

    # Construct output path
    output_path = input_path.with_name(f"{input_path.stem}{postfix}{input_path.suffix}")

    # Read and modify JSON content
    with open(input_path, 'r') as f:
        data = json.load(f)

    if "output" in data and "filename" in data["output"]:
        h5_path = Path(data["output"]["filename"])
        new_h5_filename = f"{h5_path.stem}{postfix}{h5_path.suffix}"
        data["output"]["filename"] = new_h5_filename
    else:
        print("Warning: ['output']['filename'] key not found in the JSON file. No change made to content.")

    # Write new JSON file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully created '{output_path}'")

if __name__ == "__main__":
    main()
