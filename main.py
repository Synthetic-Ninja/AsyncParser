import argparse
from async_parser import get_parsed_pages
from cvs_dump import dump_cvs


def main(link: str,
         name_output_file: str = None,
         count_pages: int = None) -> None:
    pages_content = get_parsed_pages(link, page_count=count_pages)
    dump_cvs(pages=pages_content, file_name=name_output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--link',
                        '-l',
                        type=str,
                        help='link for parsing-site',
                        required=True)
    parser.add_argument('--output',
                        '-o',
                        type=str,
                        help='link for parsing-site',
                        required=False)

    parser.add_argument('--count',
                        '-c',
                        type=int,
                        help='link for parsing-site',
                        required=False)

    args = parser.parse_args()
    main(link=args.link,
         name_output_file=args.output,
         count_pages=args.count)
