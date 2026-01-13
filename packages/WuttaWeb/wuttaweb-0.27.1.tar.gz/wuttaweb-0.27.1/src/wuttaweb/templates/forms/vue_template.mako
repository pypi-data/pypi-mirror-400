## -*- coding: utf-8; -*-

<script type="text/x-template" id="${form.vue_tagname}-template">
  ${h.form(form.action_url, **form_attrs)}
    % if form.action_method == 'post':
        ${h.csrf_token(request)}
    % endif

    % if form.has_global_errors():
        % for msg in form.get_global_errors():
            <b-notification type="is-warning" :closable="false">
              ${msg}
            </b-notification>
        % endfor
    % endif

    ${form.render_vue_fields(form_context)}

    ${form.render_vue_buttons(form_context)}

  ${h.end_form()}
</script>

<script>

  const ${form.vue_component} = {
      template: '#${form.vue_tagname}-template',
      methods: {},
  }

  const ${form.vue_component}Data = {

      % if not form.readonly:

          modelData: ${json.dumps(model_data)|n},

          % if form.auto_disable_submit:
              formSubmitting: false,
          % endif

      % endif

      % if form.grid_vue_context:
          gridContext: {
              % for key, data in form.grid_vue_context.items():
                  '${key}': ${json.dumps(data)|n},
              % endfor
          },
      % endif
  }

</script>

<% request.register_component(form.vue_tagname, form.vue_component) %>
