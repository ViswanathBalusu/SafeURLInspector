import requests
import zipfile
import io
import os
import platform
import glob

URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"


def download_url(version, platform, binary):
    return f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/{platform}/{binary}-{platform}.zip"


def fetch_latest_version():
    return requests.get(URL).json()["channels"]["Stable"]["version"]


def download_binaries(version):
    machine = platform.machine().lower()
    sys = platform.system().lower()

    if sys == "windows":
        raise NotImplemented

    if sys == "darwin":
        if "arm" in machine:
            _platform = "mac-arm64"
        else:
            _platform = "mac-x64"

    # linux
    elif sys == "linux":
        if "arm" in machine:
            raise Exception("Google doesn't compile chromedriver versions for Linux ARM. Sorry!")
        if machine.endswith("32"):
            raise Exception("Google doesn't compile 32bit chromedriver versions for Linux. Sorry!")
        _platform = "linux64"

    print(f"platform: {_platform}")

    print("downloading zip file")
    driver_url = download_url(version, _platform, "chromedriver")
    print(driver_url)
    chrome_url = download_url(version, _platform, "chrome")
    driver = requests.get(driver_url)
    chrome = requests.get(chrome_url)
    d_z = zipfile.ZipFile(io.BytesIO(driver.content))
    c_z = zipfile.ZipFile(io.BytesIO(chrome.content))

    d_path = f"chromedriver-{_platform}"
    d_origin = os.path.join(d_path, "chromedriver")
    d_dest = os.path.join(os.getcwd(), "binaries", "chromedriver")

    if not os.path.exists(os.path.join(os.getcwd(), "binaries")):
        os.mkdir(os.path.join(os.getcwd(), "binaries"))

    print("extracting zip file")
    d_z.extract(d_origin)
    print("moving file to correct folder")
    os.rename(d_origin, d_dest)

    # give execute permission
    print("setting permissions")
    os.chmod(d_dest, 0o755)

    # delete zip folder
    print("removing file: " + d_path)
    os.removedirs(d_path)

    c_path = f"chrome-{_platform}"
    c_dest = os.path.join(os.getcwd(), "binaries")

    c_z.extractall(c_dest)
    c_dest_ext = os.path.join(c_dest, c_path)
    c_dest_final = os.path.join(c_dest, f"chrome")
    if os.path.exists(c_dest_ext):
        # Rename the directory
        os.rename(c_dest_ext, c_dest_final)
    print("setting permissions")
    perm_files = glob.glob(os.path.join(c_dest_final, "*"))

    for file in perm_files:
        os.chmod(file, 0o755)


if __name__ == "__main__":
    version = fetch_latest_version()
    print(f"using version: {version}")
    download_binaries(version)
