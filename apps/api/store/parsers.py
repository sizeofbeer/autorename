from flask_restful import reqparse

author_post_parser = reqparse.RequestParser(bundle_errors=True)
author_post_parser.add_argument(
    'ID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
author_post_parser.add_argument(
    'MAC',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)


search_post_parser = reqparse.RequestParser(bundle_errors=True)
search_post_parser.add_argument(
    'ID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)


add_post_parser = reqparse.RequestParser(bundle_errors=True)
add_post_parser.add_argument(
    'ID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'MAC',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'ModelPaper',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'Path',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'PathTag',
    type=bool,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'BatchID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'BatchTime',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'Wordless',
    type=bool,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'ProcessState',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'YearMonth',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'Warehouse',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'deltag',
    type=bool,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'SeletcDel',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'picname',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)