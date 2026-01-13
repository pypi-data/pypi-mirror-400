## -*- coding: utf-8; mode: python; -*-
# -*- coding: utf-8; -*-
"""
Master view for ${model_title_plural}
"""

% if model_option == "model_class":
from ${model_module} import ${model_name}
% endif

from wuttaweb.views import MasterView


class ${class_name}(MasterView):
    """
    Master view for ${model_title_plural}
    """
    % if model_option == "model_class":
    model_class = ${model_name}
    % else:
    model_name = "${model_name}"
    % endif
    model_title = "${model_title}"
    model_title_plural = "${model_title_plural}"

    route_prefix = "${route_prefix}"
    % if permission_prefix != route_prefix:
    permission_prefix = "${permission_prefix}"
    % endif
    url_prefix = "${url_prefix}"
    % if template_prefix != url_prefix:
    template_prefix = "${template_prefix}"
    % endif

    % if not listable:
    listable = False
    % endif
    creatable = ${creatable}
    % if not viewable:
    viewable = ${viewable}
    % endif
    editable = ${editable}
    deletable = ${deletable}

    % if listable and model_option == "model_name":
    filterable = False
    sort_on_backend = False
    paginate_on_backend = False
    % endif

    % if grid_columns:
    grid_columns = [
        % for field in grid_columns:
        "${field}",
        % endfor
    ]
    % elif model_option == "model_name":
    # TODO: must specify grid columns before the list view will work:
    # grid_columns = [
    #     "foo",
    #     "bar",
    # ]
    % endif

    % if form_fields:
    form_fields = [
        % for field in form_fields:
        "${field}",
        % endfor
    ]
    % elif model_option == "model_name":
    # TODO: must specify form fields before create/view/edit/delete will work:
    # form_fields = [
    #     "foo",
    #     "bar",
    # ]
    % endif

    % if listable and model_option == "model_name":
    def get_grid_data(self, columns=None, session=None):
        data = []

        # TODO: you should return whatever data is needed for the grid.
        # it is expected to be a list of dicts, with keys corresponding
        # to grid columns.
        # 
        #     data = [
        #         {"foo": 1, "bar": "abc"},
        #         {"foo": 2, "bar": "def"},
        #     ]

        return data
    % endif

    % if listable:
    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # TODO: tweak grid however you need here
        #
        #     g.set_label("foo", "FOO")
        #     g.set_link("foo")
        #     g.set_renderer("foo", self.render_special_field)
    % endif


def defaults(config, **kwargs):
    base = globals()

    ${class_name} = kwargs.get('${class_name}', base['${class_name}'])
    ${class_name}.defaults(config)


def includeme(config):
    defaults(config)
