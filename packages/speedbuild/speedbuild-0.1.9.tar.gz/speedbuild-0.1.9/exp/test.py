import json
from exp.prev.main import init_db
from speedbuild.db.relational_db.python_packages import create_python_package, get_all_python_packages, get_python_package


def prepopulate_python_packages(package_file_path):
    init_db()
    with open(package_file_path,"r") as f:
        data = json.loads(f.read())

        for pkg in data:
            if get_python_package(pkg) == None:
                create_python_package(**{"name":pkg,"paths":data[pkg]})
            else:
                print(f"Skipping {pkg} already in db")

def getAllPkgs(saved_path):
    packages = get_all_python_packages()
    data = {}
    try:
        for pkg in packages:
            data[pkg['name']] = json.loads(pkg['paths'])
    except json.JSONDecodeError:
        pass

    with open(saved_path,"w") as f:
        json.dump(data,f, indent=4)

if __name__ == "__main__":
    save_path = "saved_packages.json"
    prepopulate_python_packages(save_path)