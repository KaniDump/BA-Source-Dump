import subprocess
import os

class Il2CppInspectorDumperCLI:
    def __init__(self,
            executable_path: str,
            library_file: str,
            global_metadata: str):
        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"Il2CppInspectorRedux executable not found at: {executable_path}")
        if not os.path.exists(library_file):
            raise FileNotFoundError(f"Library file not found at: {library_file}")
        if not os.path.exists(global_metadata):
            raise FileNotFoundError(f"Global metadata file not found at: {global_metadata}")
        self.executable_path = executable_path
        self.library_file = library_file
        self.global_metadata = global_metadata

    def dump(self,
            output_base_directory: str,
            use_dissambler: bool = False,
            dissambler_option: str = "IDA"):
        os.makedirs(output_base_directory, exist_ok=True)
        
        command = [
            self.executable_path, 
            "process", self.library_file, self.global_metadata,
            "--output", output_base_directory
        ]

        if use_dissambler:
            command.extend([
                "--disassambler", f'\"{dissambler_option}\"',
                "--output-disassembler-metadata"
            ])
        else:
            command.extend([
                "--output-csharp-stub",
                "--output-dummy-dlls"
            ])

        print("Executing command:", " ".join(command))
        
        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, 
                encoding='utf-8', errors='replace', cwd=output_base_directory)

            print("\nIl2CppInspectorRedux output (stdout):")
            print(result.stdout)
            
            if result.stderr:
                print("\nIl2CppInspectorRedux errors (stderr):")
                print(result.stderr)

            print("\nIl2CppInspectorRedux dumping process completed successfully.")
        except FileNotFoundError:
            print(f"Error: Il2CppInspectorRedux executable or one of the specified input files was not found.")
            print(f"Please double-check paths: {self.executable_path}, {self.library_file}, {self.global_metadata}")
        except subprocess.CalledProcessError as e:
            print(f"\nError executing Il2CppInspectorRedux (returned non-zero exit code {e.returncode}):")
            if e.stdout:
                print(f"STDOUT:\n{e.stdout}")
            if e.stderr:
                print(f"STDERR:\n{e.stderr}")
            print("\nIl2CppInspectorRedux likely encountered an issue. Check the output above for details.")
            print("Common issues: Incorrect Unity version, corrupted binary/metadata, invalid paths.")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")