import os
import zipfile
import cloudscraper

class FileDownloader:
    def __init__(self, url, download_dir, filename):
        self.url = url
        self.download_dir = download_dir
        self.filename = filename
        self.local_filepath = os.path.join(self.download_dir, self.filename)
        os.makedirs(self.download_dir, exist_ok=True)
        self.scraper = cloudscraper.create_scraper()

    def download(self):
        try:
            response = self.scraper.get(self.url, stream=True)
            response.raise_for_status()

            # total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192

            with open(self.local_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        # self.print_progress(downloaded, total_size)
            print(f"\nDownloaded {self.local_filepath}")
        except Exception as e:
            print(f"Error during download: {e}")

    def print_progress(self, downloaded, total_size):
        if total_size > 0:
            percent = downloaded / total_size * 100
            print(
                f"\rDownloading: {percent:.2f}% complete ({downloaded/1024:.2f} KB / {total_size/1024:.2f} KB)",
                end=''
            )

class FileExtractor:
    def __init__(self, file_path, extract_dir, version="jp"):
        self.file_path = file_path
        self.extract_dir = extract_dir
        self.apk_files = {
            'config.arm64_v8a.apk': os.path.join(self.extract_dir, 'config_arm64_v8a'),
        }
        if version == "global":
            pkg_filename = "com.nexon.bluearchive.apk"
        else:
            self.apk_files['UnityDataAssetPack.apk'] = os.path.join(self.extract_dir, 'UnityDataAssetPack')
            pkg_filename = "com.YostarJP.BlueArchive.apk"
        self.apk_files[pkg_filename] = os.path.join(self.extract_dir, 'BlueArchive_apk')
        os.makedirs(self.extract_dir, exist_ok=True)

    def extract_xapk(self):
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            print(f"Extracted {self.file_path} to {self.extract_dir}")
        except Exception as e:
            print(f"Error extracting {self.file_path}: {e}")
            return
        
        for apk_name, dest_dir in self.apk_files.items():
            print(apk_name, dest_dir)
            self.extract_apk(apk_name, dest_dir)
    
    def extract_il2cppData(self):
        destination_dir = os.path.join(self.extract_dir, 'Il2CppInspector')
        os.makedirs(destination_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_dir)
            print(f"Extracted {self.file_path} to {destination_dir}")
        except Exception as e:
            print(f"Error extracting {self.file_path}: {e}")

    def extract_il2cppPlugin(self):
        destination_dir = os.path.join(self.extract_dir, 'Il2CppInspector')
        os.makedirs(destination_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_dir)
            print(f"Extracted {self.file_path} to {destination_dir}")
        except Exception as e:
            print(f"Error extracting {self.file_path}: {e}") 

    def extract_fbsdumper(self):
        destination_dir = os.path.join(self.extract_dir, 'FbsDumper')
        os.makedirs(destination_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(destination_dir)
            print(f"Extracted {self.file_path} to {destination_dir}")
        except Exception as e:
            print(f"Error extracting {self.file_path}: {e}") 

    def extract_apk(self, apk_filename, destination_dir):
        apk_path = os.path.join(self.extract_dir, apk_filename)
        if os.path.exists(apk_path):
            os.makedirs(destination_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(apk_path, 'r') as apk_zip:
                    apk_zip.extractall(destination_dir)
                print(f"Extracted {apk_filename} to {destination_dir}")
            except Exception as e:
                print(f"Error extracting {apk_filename}: {e}")
        else:
            print(f"{apk_filename} not found in {self.extract_dir}")
