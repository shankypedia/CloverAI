import os

def count_lines_characters_and_words_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        lines = content.splitlines()
        words = content.split()
        return len(lines), len(content), len(words)

def count_stats_in_directory(directory, file_extensions=None):
    if file_extensions is None:
        file_extensions = ['.py', '.txt', '.Dockerfile', '.md', '.yaml', '.yml', '.csv', 'Dockerfile', '.sh']

    total_lines = 0
    total_characters = 0
    total_words = 0
    total_files = 0
    total_dirs = 0
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories and __pycache__ directories, but include .github
        dirs[:] = [d for d in dirs if (not d.startswith('.') or d == '.github') and d != '__pycache__']
        if any(file.endswith(tuple(file_extensions)) for file in files):
            total_dirs += 1
        for file in files:
            if not file.startswith('.') and any(file.endswith(ext) or file == 'Dockerfile' for ext in file_extensions):
                file_path = os.path.join(root, file)
                lines, characters, words = count_lines_characters_and_words_in_file(file_path)
                total_lines += lines
                total_characters += characters
                total_words += words
                total_files += 1
            else:
                print(f"Skipping file: {file}")  # Debugging line for skipped files

    avg_lines_per_file = total_lines / total_files if total_files else 0
    avg_characters_per_file = total_characters / total_files if total_files else 0
    avg_words_per_file = total_words / total_files if total_files else 0

    return total_lines, total_characters, total_words, total_files, total_dirs, avg_lines_per_file, avg_characters_per_file, avg_words_per_file

if __name__ == "__main__":
    directory = '.'  # Current directory
    file_extensions = ['.py', '.txt', '.Dockerfile', '.md', '.yaml', '.yml', '.csv', 'Dockerfile', '.sh']  # Specify relevant file types
    stats = count_stats_in_directory(directory, file_extensions)
    total_lines, total_characters, total_words, total_files, total_dirs, avg_lines_per_file, avg_characters_per_file, avg_words_per_file = stats
    print(f"Total number of lines in the codebase: {total_lines}")
    print(f"Total number of characters in the codebase: {total_characters}")
    print(f"Total number of words in the codebase: {total_words}")
    print(f"Total number of files processed: {total_files}")
    print(f"Total number of directories processed: {total_dirs}")
    print(f"Average number of lines per file: {avg_lines_per_file:.2f}")
    print(f"Average number of characters per file: {avg_characters_per_file:.2f}")
    print(f"Average number of words per file: {avg_words_per_file:.2f}")
    