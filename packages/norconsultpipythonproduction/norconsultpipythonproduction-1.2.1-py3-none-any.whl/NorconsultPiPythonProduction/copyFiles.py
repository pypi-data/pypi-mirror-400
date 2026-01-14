import os 
from serverPaths import getServerPaths
import shutil

def list_all_files(root_path):
    """Returnerer alle filer (absolutte stier) rekursivt under root_path."""
    root_path = os.path.abspath(root_path)
    files = []
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            files.append(os.path.join(dirpath, fname))
    return files

def copyAllFiles(): 
    try: 
        serverPaths = getServerPaths()
    except Exception as e:
        raise e 
    
    destinationFolder = "C:\\Users\\" + os.getlogin() + "\\AppData\\Roaming\\Norconsult\\NorconsultPiPythonProduction\\"

    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)

    try: 
        stubsPath = serverPaths["stubs"]
        femIntegratedServerPath = serverPaths["FemIntegrated"]
    except Exception as e:
        raise e

    # Get all files recursive
    filesToCopyFemIntegrated = list_all_files(femIntegratedServerPath)

    directoryPiPython = os.path.dirname(os.path.abspath(__file__))

    # Get latest .pyi (rekursive in case moved)
    stub_candidates = [f for f in list_all_files(stubsPath) if f.lower().endswith(".pyi")]
    if stub_candidates:
        stubsFileToCopy = max(stub_candidates, key=os.path.getctime)
        stubsFileDestination = os.path.join(directoryPiPython, "init.pyi")
        shutil.copy2(stubsFileToCopy, stubsFileDestination)
    else: 
        print("Unable to find a stub file for copying. This may result in outdated or missing code-help and IntelliSense.")

    # Copy FemIntegrated libraries
    for src in filesToCopyFemIntegrated:
        rel = os.path.relpath(src, femIntegratedServerPath)
        dest = os.path.join(destinationFolder, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            if requiresUpdate(src, dest):
                shutil.copy2(src, dest)
        except Exception as e:
            print(f"Unable to copy -> skipping {rel}. Error: {e}")

def requiresUpdate(serverFilePath, destFilePath):
    if not os.path.isfile(serverFilePath):
        return False
    if not os.path.isfile(destFilePath):
        return True
    return os.path.getmtime(serverFilePath) > os.path.getmtime(destFilePath)