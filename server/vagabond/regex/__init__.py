'''
    Collection of regular expressions in string format used for Cerberus input validation.
'''

USERNAME = '^[a-zA-Z0-9_-]{1,32}$'

ACTOR_NAME = '^[a-zA-Z0-9_-]{1,32}$'

PASSWORD = '^.{12,255}'

ACTOR_HANDLE = '@[\\w]{1,}@([\\w]{1,}\\.){0,}[\\w]{1,}\\.[\\w]{1,}'

XSD_DATE = '[1-9][0-9]{3}-.+T[^.]+(Z|[+-].+)'

MIME_TYPE = '.{1,}/.{1,}'

XSD_DURATION = '^(-?)P(?=.)((\d+)Y)?((\d+)M)?((\d+)D)?(T(?=.)((\d+)H)?((\d+)M)?(\d*(\.\d+)?S)?)?$'
