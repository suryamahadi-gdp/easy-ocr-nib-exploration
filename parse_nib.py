from argparse import ArgumentParser
import re
import json

import easyocr
from rapidfuzz import fuzz

from utils import find_value_from_key, combine_values

def parse_nib(result: list, threshold: float = 90):
    """
    NIB usually after string "NOMOR INDUK BERUSAHA (NIB), so find any integer after
    this string
    """
    is_nib_title = False
    for row in result:
        score = fuzz.ratio(row[1], "NOMOR INDUK BERUSAHA (NIB)")
        if score > threshold:
            is_nib_title = True
        m = re.search("^[0-9]*$", row[1])
        if m is not None and is_nib_title:
            return m.string
    return ''

def main(image, threshold):
    reader = easyocr.Reader(['en', 'id'], gpu=False)
    result = reader.readtext(image)
    nib = parse_nib(result, threshold)

    keys = {
        'Nama Usaha': '',
        'Alamat Usaha': '',
        'Nomor Telepon': '',
        'Nomor Fax': '',
        'Email': '',
        'Nama KBLI': '',
        'Kode KBLI': '',
        'Status Penanaman Modal': '',
        'Ditetapkan tanggal': ''
    }

    for key in keys.keys():
        values = find_value_from_key(result, key, thresh=threshold)
        keys[key] = combine_values(values)

    keys['NIB'] = nib
    
    result = json.dumps(keys, indent=4)
    print(result)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--image', type=str, required=True)
    parser.add_argument('--threshold', type=float, default=90)
    args = parser.parse_args()

    main(args.image, args.threshold)