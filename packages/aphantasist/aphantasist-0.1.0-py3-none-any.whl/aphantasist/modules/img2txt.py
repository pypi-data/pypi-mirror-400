import os
from PIL import Image as im
from aphantasist.core import config


def img2txt(overwrite=False):
    r = None

    input_dir = config.get_dir("input")
    output_dir = config.get_dir("output")
    print(f"🤔 Thinking about images from `{input_dir}`")
    img_files = os.listdir(input_dir)
    for img_file in img_files:
        source = f"{input_dir}/{img_file}"
        destiny = f"{output_dir}/{img_file}.txt"
        if overwrite:
            is_destiny_available = overwrite
        else:
            is_destiny_available = not os.path.exists(destiny)

        if is_destiny_available and is_image(source):
            print(f"🖼️ Reading and analysing `{img_file}`")
            r = get_reader(r)
            txt = r.readtext(source)

            print(f"✍️ Writing the {len(txt)} found phrases in `{img_file}.txt`")

            final_string = ""
            for phrase in txt:
                if phrase[1][0:1].isupper():
                    final_string = final_string + "\n"
                final_string = final_string + " " + phrase[1]
            with open(destiny, "+w") as f:
                f.write(final_string)
    print("💭 We're done!")


def get_reader(r=None):
    if r is None:
        import warnings

        warnings.filterwarnings("ignore", category=UserWarning)

        import easyocr

        r = easyocr.Reader(["pt", "en"], verbose=False)
    return r


def is_image(file_path):
    try:
        im.open(file_path)
        return True
    except:
        return False
