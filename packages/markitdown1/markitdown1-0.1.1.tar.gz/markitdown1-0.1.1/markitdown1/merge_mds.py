import os
import argparse

def merge_mds(input_dir, output_dir):
    """
    Merge markdown files in each subdirectory of input_dir into a single file.
    """
    if not os.path.exists(input_dir):
        print(f"Error: Target directory '{input_dir}' does not exist.")
        return

    # Ensure summary directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over immediate subdirectories
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        
        if os.path.isdir(item_path):
            folder_name = item
            summary_file_name = f"{folder_name}_summary.md"
            summary_file_path = os.path.join(output_dir, summary_file_name)
            
            print(f"Processing folder: {folder_name}")
            
            summary_content = f"# Summary of {folder_name}\n\n"
            
            # Walk through the subdirectory recursively
            file_count = 0
            for root, dirs, files in os.walk(item_path):
                for file in files:
                    if file.lower().endswith('.md'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, input_dir)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            summary_content += f"## File: {relative_path}\n\n"
                            summary_content += content
                            summary_content += "\n\n---\n\n"
                            file_count += 1
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
            
            if file_count > 0:
                try:
                    with open(summary_file_path, 'w', encoding='utf-8') as f:
                        f.write(summary_content)
                    print(f"Created summary: {summary_file_path} (Merged {file_count} files)")
                except Exception as e:
                    print(f"Error writing summary {summary_file_path}: {e}")
            else:
                print(f"No markdown files found in {folder_name}")

def main():
    parser = argparse.ArgumentParser(description="Merge markdown files in subdirectories.")
    parser.add_argument("input_dir", help="Target directory containing subfolders to merge")
    parser.add_argument("output_dir", help="Directory to save summary files")
    args = parser.parse_args()
    merge_mds(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
