import requests
from pathlib import Path
import os
import time
import zipfile

BASE_URL = "https://meashub.iap.tuwien.ac.at/api"
DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
ACCESS_TOKEN_FILE = DOWNLOAD_DIR / Path("access_token")

def file_exists_and_fresh(path, max_age_seconds=86400):
    """
    Returns True if the file exists and is not older than max_age_seconds.
    """
    if not os.path.isfile(path):
        return False

    age = time.time() - os.path.getmtime(path)
    return age <= max_age_seconds

def get_files_by_meashub(meashub_id):
    if file_exists_and_fresh(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE)as f:
            api_token = f.readline()    
    else:
        os.remove(ACCESS_TOKEN_FILE)
        load_access_token()
    url = f"{BASE_URL}/{meashub_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cd = response.headers.get("content-disposition")
        filename = cd.split("filename=")[-1].strip('"')
        file_path = DOWNLOAD_DIR / Path(filename)
        with open(file_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error {response.status_code}")#: {response.json()}")
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(DOWNLOAD_DIR)


def get_science_email_adress(mounts_path="/proc/mounts",skip_check=False):
    """
    Reads /proc/mounts and returns the user ID from any line
    where the tokens appear in the following order:
        /science -> /home/XXXXX -> ceph

    Returns:
        str or None
    """
    try:
        OS_USER = os.environ.get("JUPYTERHUB_USER") or os.environ.get("USER")
        with open(mounts_path, "r") as f:
            for line in f:
                science = None
                home = None
                ceph = None
                for part in line.split():
                    if science is None and part.endswith("/science"):
                        science = part
                    elif science is not None and home is None and part.startswith("/home/"):
                        home = part
                    elif home is not None and part == "ceph":
                        ceph = part
                        break

                if ceph is not None:
                    user_id = home.split("/home/", 1)[1].replace("_2e", ".").replace("-2e", ".")
                    if user_id == OS_USER or skip_check:
                        return userid_to_generalemail(user_id)
    except OSError:
        pass

    return None

def userid_to_generalemail(user_id="noone"):
    """
    """
    matrikel = user_id[1:] if user_id else user_id
    email = user_id + "@tuwien.ac.at"
    if user_id.startswith("e"):
        url = f"https://tiss.tuwien.ac.at/api/person/v23/mnr/{matrikel}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises HTTPError on non-200 responses

        data = response.json()
        email = data.get("main_email")
    return email
        

def load_access_token():
    email = get_science_email_adress()
    url = f"{BASE_URL}/token/{email}"
    response = requests.post(url)
    data = response.json()
    print(data["access_token"])
    with open(ACCESS_TOKEN_FILE, "w") as f:
        f.write(data['access_token'])    
   
