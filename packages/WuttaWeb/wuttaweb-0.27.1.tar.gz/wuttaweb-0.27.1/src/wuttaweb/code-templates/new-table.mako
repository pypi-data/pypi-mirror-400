## -*- coding: utf-8; mode: python; -*-
# -*- coding: utf-8; -*-
"""
Model definition for ${model_title_plural}
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class ${model_name}(model.Base):
    """
    ${description}
    """
    __tablename__ = "${table_name}"
    % if versioned:
    % if all([c["versioned"] for c in columns]):
    __versioned__ = {}
    % else:
    __versioned__ = {
        "exclude": [
            % for column in columns:
            % if not column["versioned"]:
            "${column['name']}",
            % endif
            % endfor
        ],
    }
    % endif
    % endif
    __wutta_hint__ = {
        "model_title": "${model_title}",
        "model_title_plural": "${model_title_plural}",
    }
    % for column in columns:

    % if column["name"] == "uuid":
    uuid = model.uuid_column()
    % elif column["data_type"]["type"] == "_fk_uuid_":
    ${column["name"]} = model.uuid_fk_column("${column['data_type']['reference']}.uuid",
                                nullable=${column["nullable"]})
    % if column["relationship"]:
    ${column["relationship"]["name"]} = orm.relationship(
        "${column['relationship']['reference_model']}",
        doc="""
        ${column["description"] or ""}
        """)
    % endif
    % else:
    ${column["name"]} = sa.Column(
        ${column["formatted_data_type"]},
        nullable=${column["nullable"]},
        doc="""
        ${column["description"] or ""}
        """)
    % endif
    % endfor

    # TODO: you usually should define the __str__() method

    # def __str__(self):
    #     return self.name or ""
