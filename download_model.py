import urllib.request
import os

def download_file(url, filename):
    print(f"Trying to download from: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded {filename}!")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

if not os.path.exists('gender_net.caffemodel'):
    urls = [
        "https://github.com/smahesh29/Gender-and-Age-Detection/raw/master/gender_net.caffemodel",
        "https://github.com/eveningglow/age-and-gender-classification/raw/master/model/gender_net.caffemodel",
        "https://github.com/GilLevi/AgeGenderDeepLearning/raw/master/models/gender_net.caffemodel"
    ]
    
    for u in urls:
        if download_file(u, 'gender_net.caffemodel'):
            break

if not os.path.exists('gender_deploy.prototxt'):
    import shutil
    if os.path.exists('gender_deploy.prototxt.txt'):
        shutil.copy('gender_deploy.prototxt.txt', 'gender_deploy.prototxt')
