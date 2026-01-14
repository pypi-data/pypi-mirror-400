from speedbuild.sb import extractFeature

project_path = "/home/attah/Documents/work/speedbuildjs/express.js_contact_app"
file_name = "routes/contact_routes.js"
target = "/"

extracted_file = extractFeature(project_path,[
    "speedbuild",
    "extract",
    target,
    file_name,
    "--express"
],True)

print(extracted_file)