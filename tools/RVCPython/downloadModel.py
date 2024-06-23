import os
import requests


def downloadRVCModels(dir):
    folder = os.path.join(dir, 'base_model')

    if not os.path.exists(folder):
        os.makedirs(folder)

    files = {
        "hubert_base.pt": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/hubert_base.pt",
        "rmvpe.pt": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/rmvpe.pt",
        "rmvpe.onnx": "https://huggingface.co/Daswer123/RVC_Base/resolve/main/rmvpe.onnx"
    }

    for filename, url in files.items():
        filePath = os.path.join(folder, filename)
        if not os.path.exists(filePath):
            print(f"Downloading {filename} to {filePath}...\n"+"-"*len(f"Downloading {filename}..."))
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(filePath, 'wb') as f:
                    f.write(r.content)
                print(f"Successfully downloaded {filename}\n")
