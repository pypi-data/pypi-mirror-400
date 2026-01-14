import os
import json
from typing import Dict

from vector_database import saveToVectorDB
from features import create_feature, feature_exist, get_feature

def saveFeatureToDB(feature : Dict, framework : str, skip_vector_db=False) -> None:
    name = feature['name']
    code = feature['code']
    imports = feature.get('imports',[])
    dependencies = feature.get('deps',[])
    filename = feature['feature_filename']
    is_root = feature.get('is_root',False)
    documentation = feature.get('documentation',"")

    if not feature_exist(name,filename,code):
        dependencies = ",".join([i['imports'] for i in dependencies if isinstance(i,dict)])
        
        feature_id = create_feature(**{
            "doc": documentation,
            "name": name,
            "code":code,
            "code_import": imports,
            "dependencies": dependencies,
            "root_feature": is_root,
            "feature_filename": filename,
            "framework":framework
        })

        imports = ",".join(imports)

        if not skip_vector_db:
            meta_data = {
                "doc": documentation if documentation else "",
                "name": name,
                "code_imports": imports,
                "dependencies": dependencies,
                "root_feature": is_root,
                "feature_filename": filename,
                "id": feature_id,
                "framework":framework
            }

            saveToVectorDB(doc=f"{documentation}\n\n{code}",meta_data=meta_data)

def processFeatureDjangoSettings(settings_data : Dict ) -> str:
    name = f"{settings_data['feature']}_django_settings"
    settings = settings_data.get('settings',{})
    data = {
        "INSTALLED_APPS":settings.get('installed_apps',[]),
        "MIDDLEWARES":settings.get('middlewares',[[]])[0],
        "ImportStatements":settings.get('imports',[]),
        "Configurations":settings_data.get('configurations',[]),
        "PackageDependencies":settings_data.get("dependencies",[])
    }

    saveFeatureToDB({
        "name":name,
        "code":json.dumps(data),
        "feature_filename":"settings.py"
    },"django",True)

    return name

def saveFeatureFileToDB(file : str, framework : str) -> None:
    if not os.path.exists(file):
        raise FileNotFoundError(f"Could not find file : {file}")
    
    with open(file,"r") as f:
        try:
            file_data = json.loads(f.read())
            settings_conf = file_data['settings.py']
            del file_data['settings.py']

            settings_name = processFeatureDjangoSettings(settings_conf['feature_settings']['code'])

            for filename in file_data:
                for chunk in file_data[filename]:
                   feature_data = file_data[filename][chunk]

                   feature_data['deps'].append(settings_name) # add feature settings as part of dependencies
                   feature_data['feature_filename'] = filename
                   feature_data['name'] = chunk

                   saveFeatureToDB(feature_data,framework)

        except json.JSONDecodeError as error:
            raise ValueError(f"Feature file `{file}` is not valid json")
        
    print("Feature Saved to DB")
        
if __name__ == "__main__":
    # saveFeatureFileToDB("/home/attah/.sb_zip/ManageSupplements.json","django")
    print(get_feature(2))