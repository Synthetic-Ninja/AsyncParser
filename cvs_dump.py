import pandas as pd
from csv import writer


def dump_cvs(pages: list,
             file_name: str | None) -> None:

    if file_name is not None and '.csv' not in file_name:
        file_name += '.csv'

    if file_name is None:
        file_name = 'output.csv'

    with open(file_name, 'w', encoding='UTF-8', newline='') as f:
        thewriter = writer(f)
        header = ['Title', 'Location', 'Price', 'Area']
        thewriter.writerow(header)

        for list in pages:
            info = [list.TITLE, list.LOCATION, list.PRICE, list.AREA]
            thewriter.writerow(info)
