import subprocess
import os

class FbsDumperCLI:
    def __init__(self,
            executable_path: str,
            dummy_dll_dir: str):
        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"FbsDumper executable not found at: {executable_path}")
        if not os.path.exists(dummy_dll_dir):
            raise FileNotFoundError(f"Dummy DLL directory not found at: {dummy_dll_dir}")
        self.executable_path = executable_path
        self.dummy_dll_dir = dummy_dll_dir

    def dump(self, 
            output_directory,
            output_file_name="BlueArchive.fbs",
            library_file=None,
            custom_namespace=None,
            force_snake_case=False, 
            namespace_to_look_for=None):
        
        full_output_file_path = os.path.join(output_directory, output_file_name)
        os.makedirs(output_directory, exist_ok=True)

        command = [
            self.executable_path,
            "-d", self.dummy_dll_dir
        ]
        if library_file is not None:
            command.extend(["-a", library_file])
        if custom_namespace is not None:
            command.extend(["-n", custom_namespace])
        if force_snake_case:
            command.append("-s")
        if namespace_to_look_for is not None:
            command.extend(["-nl", namespace_to_look_for])
        if full_output_file_path is not None:
            command.extend(["-o", full_output_file_path])
        
        print("Executing command:", " ".join(command))
        
        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True)
            print("FbsDumper output:")
            print(result.stdout)
            if result.stderr:
                print("FbsDumper errors:")
                print(result.stderr)
            print(f"Successfully dumped to: {full_output_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing FbsDumper (exit code {e.returncode}):")
            if e.stdout:
                print(f"FbsDumper stdout: \n{e.stdout}")
            if e.stderr:
                print(f"FbsDumper stderr: \n{e.stderr}")
            print(f"Dump failed. Check the errors above.")
        except FileNotFoundError:
            print(f"Error: The executable '{self.executable_path}' was not found. Check the path.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

