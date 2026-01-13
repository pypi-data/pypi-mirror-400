## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="page_content()">
  <br />
  <div class="buttons">
    % if request.has_perm("alembic.dashboard"):
        <wutta-button type="is-primary"
                      tag="a" href="${url('alembic.dashboard')}"
                      icon-left="forward"
                      label="Alembic Dashboard"
                      once />
    % endif
  </div>

  ${parent.page_content()}
</%def>

<%def name="form_vue_fields()">

  ${form.render_vue_field("description", horizontal=False)}

  ${form.render_vue_field("autogenerate", horizontal=False, label=False, static_text="Auto-generate migration logic based on current app model")}

  <br />

  <b-field label="Branching Options">
    <div style="margin: 1rem;">

      <div class="field">
        <b-radio name="branching_option"
                 v-model="${form.get_field_vmodel('branching_option')}"
                 native-value="revise">
          Revise existing branch
        </b-radio>
      </div>

      <div v-show="${form.get_field_vmodel('branching_option')} == 'revise'"
           style="padding: 1rem 0;">

        ${form.render_vue_field("revise_branch", horizontal=True)}

      </div>

      <div class="field">
        <b-radio name="branching_option"
                 v-model="${form.get_field_vmodel('branching_option')}"
                 native-value="new">
          Start new branch
        </b-radio>
      </div>

      <div v-show="${form.get_field_vmodel('branching_option')} == 'new'"
           style="padding: 1rem 0;">

        ${form.render_vue_field("new_branch", horizontal=True)}
        ${form.render_vue_field("version_location", horizontal=True)}

        <p class="block is-italic">
          NOTE: New version locations must be added to the
          <span class="is-family-monospace">[alembic]</span> section of
          your config file (and app restarted) before they will appear as
          options here.
        </p>

      </div>
    </div>

  </b-field>
</%def>
