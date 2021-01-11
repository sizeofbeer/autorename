from flask_restful import reqparse

login_post_parser = reqparse.RequestParser(bundle_errors=True)
login_post_parser.add_argument(
    'Name',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
login_post_parser.add_argument(
    'Password',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)


search_post_parser = reqparse.RequestParser(bundle_errors=True)
search_post_parser.add_argument(
    'Name',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)

add_post_parser = reqparse.RequestParser(bundle_errors=True)
add_post_parser.add_argument(
    'Name',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'Password',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)
add_post_parser.add_argument(
    'Role',
    type=str,
    required=True,
    nullable=False,
    location=('json', 'values')
)