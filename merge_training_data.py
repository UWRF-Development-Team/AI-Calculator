from pathlib import Path

def change_path(input_file, directory):
    input_file = input_file.split(".")
    counter = 0
    while True:
        path = Path.joinpath(directory, input_file[0] + "." + str(counter) + "." + input_file[2])
        counter += 1
        if not path.exists():
            return path

new = Path('new_training_data')
old = Path('training_data')

for new_file in new.iterdir():   
    print("changed " + new_file.name, end="")
    new_path = change_path(new_file.name, old)
    new_file.replace(new_path)
    print(" to " + new_path.name)
