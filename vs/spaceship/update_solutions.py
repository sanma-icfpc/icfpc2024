
#!/usr/bin/env python3

import os
import shutil


def main():
    for solution_id in range(1, 25 + 1):
        print(f'solution_id={solution_id}')
        source_file_path = f'data/courses/spaceship/solutions/spaceship{solution_id}.txt.tmp'
        destination_file_path = f'data/courses/spaceship/solutions/spaceship{solution_id}.txt'

        if not os.path.isfile(source_file_path):
            print("The source file does not exist.")
            continue;

        if not os.path.isfile(destination_file_path):
            print("The destination file does not exist.  Copy the source file to the destination file.")
            shutil.copy(source_file_path, destination_file_path)
            continue

        source_file_size = os.path.getsize(source_file_path)
        destination_file_size = os.path.getsize(destination_file_path)
        print(f'source_file_size={source_file_size} destination_file_size={destination_file_size}')

        if source_file_size >= destination_file_size:
            print("The destination file is smaller than the source file. Do nothing.")
            continue

        os.remove(destination_file_path)
        shutil.copy(source_file_path, destination_file_path)
        print("The destination file is bigger than the source file. Copy the source file to the destionation file.")


if __name__ == '__main__':
    main()
