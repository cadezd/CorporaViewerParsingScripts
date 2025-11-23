import os

import fitz


def create_thumbnails(source, destination):
    print(f"Creating thumbnails for files in directory:", source)

    for file in os.listdir(source):
        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(source, file)

        # get first page of pdf
        pdf_document = fitz.open(path)
        first_page = pdf_document[0]

        # generate thumbnail
        image = first_page.get_pixmap()
        image.save(os.path.join(destination, f"{file[:-4]}.png"))  # Save as PNG, removing .pdf extension

        print(f"✅ Created thumbnail for '{file}'")