import subprocess
import os

class FbsDumperCLI:
    def __init__(self,
            executable_path: str,
            dummy_dll_dir: str,
            il2cpp_library: str):
        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"FbsDumper executable not found at: {executable_path}")
        if not os.path.exists(dummy_dll_dir):
            raise FileNotFoundError(f"Dummy DLL directory not found at: {dummy_dll_dir}")
        if not os.path.exists(il2cpp_library):
            raise FileNotFoundError(f"Library file not found at: {il2cpp_library}")
        self.executable_path = executable_path
        self.dummy_dll_dir = dummy_dll_dir
        self.il2cpp_library = il2cpp_library

    def dump(self, 
            output_directory,
            fbs_version="V2",
            output_file_name="BlueArchive.fbs",
            custom_namespace=None,
            force_snake_case=False, 
            namespace_to_look_for=None):
        
        full_output_file_path = os.path.join(output_directory, output_file_name)
        os.makedirs(output_directory, exist_ok=True)

        command = [
            self.executable_path,
            "-d", self.dummy_dll_dir,
            "-a", self.il2cpp_library,
            "-o", full_output_file_path,
            "-dv", fbs_version
        ]

        if custom_namespace is not None:
            command.extend(["-n", custom_namespace])
        if force_snake_case:
            command.append("-s")
        if namespace_to_look_for is not None:
            command.extend(["-nl", namespace_to_look_for])
        
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

