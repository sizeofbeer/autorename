from flask_restful import reqparse


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
    'ModelPaperCode',
    type=str,
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
    'YearMonth',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'WarehouseCode',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)

select_post_parser = reqparse.RequestParser(bundle_errors=True)
select_post_parser.add_argument(
    'ID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
select_post_parser.add_argument(
    'ModelPaperCode',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)

combin_post_parser = reqparse.RequestParser(bundle_errors=True)
combin_post_parser.add_argument(
    'ID',
    type=int,
    required=True,
    nullable=False,
    location=('json', 'values')
)
combin_post_parser.add_argument(
    'ModelPaperCode',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
combin_post_parser.add_argument(
    'data',
    type=list,
    required=True,
    nullable=False,
    location=('json', 'values')
)
