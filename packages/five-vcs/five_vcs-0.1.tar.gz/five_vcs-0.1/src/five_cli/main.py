import pathlib
import sys, os
from typing import Type
from five_source.version_system import compile, decompile, RAWFILE_VER
from five_source import __version__
from .interface import *
Version = '1.1.19'





VCS_FORMAT = '.vcs'
FIVE_FILE_FORMAT = '.five'





class Parser:
    def __init__(self) -> None:
        self.commands = {} # command:[handler, description, require_args, optional_args]
        self.add_command('help', self.help, 'Show this help message', [], [])
        self.logo = color.set(''' _______ ___            _______ 
|   _   |__/--.--.-----|   _   |
|.  ⎣___|  |  |  |  -__|   ⎣___|
|.  __) |__|\\___/|_____|____   |
|:  |                  |:  ╵   |
|::.|       five       |::.. . |
`---'                  `-------\'''', color.RED)
        self.debug = False
    
    def about(self):
        print(self.logo)
        print(color.set('FIVE - File Versioning Engine', color.BLUE))
        print('FIVE is a simple and predictable VCS for text files.\n')
        print(f'Only {color.set('humanmade', color.YELLOW)}, by Pt')
        print('Licence', color.set('MIT', color.YELLOW))
        print(f'CLI {color.set('v'+Version, color.BRIGHT_GREEN)}, Project {color.set('v'+__version__, color.BRIGHT_GREEN)}')
        print()
    
    def help(self, *args):
        self.about()
        for cmd in self.commands.keys():
            print(f'{color.set('╭─────── Command ', color.GREEN)}[{color.set(cmd, color.YELLOW)}]')
            args = ''
            require_args = self.commands[cmd][2]
            for arg in require_args:
                args += '<'+arg+'>'
                if require_args.index(arg) != (len(require_args) - 1):
                    args += ' '
            print(color.set('⎬─ Args: ', color.GREEN) + color.set(args, color.BLUE))
            docs = self.commands[cmd][1].split('\n')
            print(color.set('⎬─ Desc:', color.GREEN))
            for line in docs:
                print(color.set('│   ', color.GREEN) + line)
            print(color.set('╰───────', color.GREEN))
            print()
    
    def unknown(self, command):
        print(color.set('Unknown command: ', color.RED), end = '')
        print(color.set(f'[{command}]', color.BLUE))
        print(color.set('Type [help] for help', color.YELLOW))
    
    def main(self):
        argv = sys.argv[1:]
        if len(argv) == 0:
            self.about()
            print(color.set('Type [help] for help', color.YELLOW))
            return
        if argv[0] == '--debug':
            argv = argv[1:]
            self.debug = True
        command = argv[0]
        args = argv[1:]
        if command not in self.commands.keys():
            self.unknown(command)
            return
        require = self.commands[command][2]
        optional = self.commands[command][3]
        if optional == []:
            if not (len(args) == len(require)):
                print(color.set('Invalid argument length: ', color.RED)+str(len(args)))
                print(f'(Reguire: {color.set(str(require), color.YELLOW)}[{len(require)}], now: {len(args)})')
                return
        else:
            if not (len(args) >= (len(require) + len(optional))):
                print(color.set('Invalid argument length: ', color.RED)+str(len(args)))
                print(f'(Reguire: {color.set(str(require), color.YELLOW)}[{len(require)}], {color.set(str(optional), color.YELLOW)}[{len(optional)}], now: {len(args)})')
                return
        try: self.commands[command][0](*args) # call handler
        except Exception as e:
            print(color.set(f'Error: [{e}]', color.RED))
            if self.debug:
                e.with_traceback()
            return

    def add_command(self, cmd, handler, description, require_args: list[str], optional_args: list[str] = []):
        self.commands[cmd] = [handler, description, require_args, optional_args]






def compile_handler(file_in: str, file_out: str):
    with open(file_in, 'r') as file:
        content = file.read()
    with open(file_out, 'w') as file:
        file.write(compile({RAWFILE_VER:content}))

def decompile_handler(filename_in: str, filename_out: str, version: str):
    with open(filename_in, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    try: version = decompiled[version]
    except KeyError: 
        print(f'Error: Version [{(version)}] is not found. Available versions: {list(decompiled.keys())}')
        return
    with open(filename_out, 'w') as file:
        content = file.write(version)

def push_handler(five_file: str, push_file: str, push_version: str):
    with open(five_file, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    with open(push_file, 'r') as file:
        content = file.read()
    decompiled[push_version] = content
    compiled = compile(decompiled)
    with open(five_file, 'w') as file:
        content = file.write(compiled)

def log_handler(five_file: str):
    with open(five_file, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    print(color.set('╭─────── Versions:', color.GREEN))
    [
        print(color.set('│   ', color.GREEN) + color.set(str(list(decompiled.keys()).index(version
            )) + ': ', color.YELLOW) + str(version)) 
        for version in decompiled.keys()
    ]
    print(color.set('╰───────', color.GREEN))

def delete_handler(five_file: str, version: str):
    with open(five_file, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    new = {}
    for key in decompiled.keys():
        if key != version: new[key] = decompiled[key]
    compiled = compile(new)
    with open(five_file, 'w') as file:
        content = file.write(compiled)

def print_handler(five_file: str, version: str):
    with open(five_file, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    if version not in decompiled.keys():
        print(f'Error: Version [{(version)}] is not found. Available versions: {list(decompiled.keys())}')
        return
    print(f'{color.set(f'╭─────── Version [{version}] of ', color.GREEN)}[{color.set(five_file, color.YELLOW)}]')
    code = decompiled[version].split('\n')
    [
        print(color.set('│   ', color.GREEN) + line) 
        for line in code
    ]
    print(color.set('╰───────', color.GREEN))

def stats_handler(five_file: str):
    with open(five_file, 'r') as file:
        content = file.read()
    decompiled = decompile(content)
    versions = decompiled.keys()
    chars_len = len(content)
    lines_len = len(content.split('\n'))
    last_version = list(decompiled.keys())[-1]
    print(f'{color.set('╭─────── Stats of ', color.GREEN)}[{color.set(five_file, color.YELLOW)}]')
    print(color.set('⎬─ Versions:', color.GREEN))
    [
        print(color.set('│   ', color.GREEN) + color.set(str(list(decompiled.keys()).index(version
            )) + ': ', color.YELLOW) + str(version)) 
        for version in versions
    ]
    print(color.set('⎬─ Last version: ', color.GREEN))
    print(color.set('│   ', color.GREEN), end = '')
    print(color.set(f"{list(versions).index(last_version)}: ", color.YELLOW), end = '')
    print(str(last_version))
    print(color.set('⎬─ Size: ', color.GREEN))
    print(color.set('│   ', color.GREEN) + color.set('Chars: ', color.YELLOW) + str(chars_len))
    print(color.set('│   ', color.GREEN) + color.set('Lines: ', color.YELLOW) + str(lines_len))
    print(color.set('╰───────', color.GREEN))
    print()






def vcs_init_handler(dir_name: str, *files: str):
    dir_name = dir_name+VCS_FORMAT
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    for file_path in files: 
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} does not exist, skipping")
            continue
        relative_dir = os.path.dirname(file_path)
        if relative_dir:
            target_dir = os.path.join(dir_name, relative_dir)
            os.makedirs(target_dir, exist_ok=True)
        with open(file_path, 'r') as src_file:
            content = src_file.read()
        target_path = os.path.join(dir_name, file_path + FIVE_FILE_FORMAT)
        five_content = compile({RAWFILE_VER: content})
        with open(target_path, 'w') as dst_file:
            dst_file.write(five_content)
        print(f"Created backup: {target_path}")



def vcs_get_handler(vcs_folder, file: str, output: str, version: str):
    vcs_folder = vcs_folder+VCS_FORMAT
    if not os.path.exists(vcs_folder):
        raise SystemError('VCS folder is not exist.')
        return
    with open(f'{vcs_folder}/{file}.five', 'r') as fivefile:
        content = decompile(fivefile.read())
    with open(output, 'w') as outfile:
        outfile.write(content[version])

def vcs_add_handler(vcs_folder, *files: str):
    vcs_folder = vcs_folder+VCS_FORMAT
    if not os.path.exists(vcs_folder):
        raise SystemError('VCS folder is not exist.')
        return
    for file_path in files: 
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} does not exist, skipping")
            continue
        relative_dir = os.path.dirname(file_path)
        if relative_dir:
            target_dir = os.path.join(vcs_folder, relative_dir)
            os.makedirs(target_dir, exist_ok=True)
        with open(file_path, 'r') as src_file:
            content = src_file.read()
        target_path = os.path.join(vcs_folder, file_path + FIVE_FILE_FORMAT)
        five_content = compile({RAWFILE_VER: content})
        with open(target_path, 'w') as dst_file:
            dst_file.write(five_content)
        print(f"Created backup: {target_path}")





def vcs_handler(command, *args):
    try:
        if command == 'init':
            vcs_init_handler(*args)
        elif command == 'get':
            vcs_get_handler(*args)
        elif command == 'add':
            vcs_add_handler(*args)
        else:
            print(Parser().unknown(command))
    except TypeError as e:
        print(color.set(f'Arguments error: {e}'))










def main():
    compile_docs = f'''Compile text file to .five format
Converts a regular text file into a .five file 
with version control.

Initial version [{RAWFILE_VER}] will be created with the 
raw file content.

Usage:
    five compile <input_file> <output.five>

Example:
    five compile document.txt versions.five'''

    decompile_docs = '''Extract specific version from .five file
Decompiles a particular version from a .five 
file and saves it as a regular file.

Usage:
    five decompile <file.five> <out> <version>

Example:
    five decompile project.five current.txt v2.5'''

    push_docs = '''Add new version to existing .five file
Pushes content from a text file as a new 
version into an existing .five file.

Usage:
    five push <file.five> <add_file> <version>

Example:
    five push project.five changes.txt v3.0'''

    delete_docs = '''Remove version from .five file
Deletes a specific version from a .five 
file while keeping other versions.

Usage:
    five delete <file.five> <version>

Example:
    five delete project.five v1.0'''

    log_docs = '''List all versions in .five file
Shows all available versions with their 
indices in chronological order.

Usage:
    five log <file.five>

Example:
    five log project.five

Output format:
    0: RAW
    1: v1.0
    2: v2.0'''

    print_docs = '''Display version content in console
Prints the content of a specific version 
directly to the terminal.

Usage:
    five print <file.five> <version>

Example:
    five print project.five v2.5'''

    stats_docs = '''Show .five file statistics
Displays comprehensive statistics about the 
.five file.

Usage:
    five stats <file.five>

Example:
    five stats project.five

Shows:
    - All version names
    - File size (characters and lines)
    - Last version name'''

    vcs_docs = '''VCS - Version Control System for multiple 
files Manage version control for entire 
directories and multiple files.

Available VCS commands:
    five vcs init <dir> <files...>   
        - Initialize new VCS repository
    five vcs add <dir> <files...>    
        - Add files to existing VCS
    five vcs get <dir> <file> <out> <ver> 
        - Extract file version
    five vcs help                    
        - Show this help message
    
VCS Structure:
    Creates <dir>.vcs/ folder containing 
    .five files for each tracked file.
    Each .five file contains all versions 
    of the original file.
    
Example workflow:
    five vcs init project main.py config.yaml
    (make changes to main.py)
    five push project.vcs/main.py.five main.py v1.1
    five vcs get project main.py old_main.py v1.0'''

    p = Parser()
    commands = [
        ('compile', compile_handler, compile_docs, ['filename', 'five_filename']),
        ('decompile', decompile_handler, decompile_docs, ['filename_in', 'filename_out', 'version']),
        ('push', push_handler, push_docs, ['five_file', 'push_text_file', 'push_version']),
        ('delete', delete_handler, delete_docs, ['five_file', 'version']),
        ('log', log_handler, log_docs, ['five_file']),
        ('print', print_handler, print_docs, ['five_file', 'version']),
        ('stats', stats_handler, stats_docs, ['five_file']),
        ('vcs', vcs_handler, vcs_docs, ['command'], ['args...']),
    ]
    for cmd in commands:
        p.add_command(*cmd)
    p.main()

if __name__ == '__main__':
    main()