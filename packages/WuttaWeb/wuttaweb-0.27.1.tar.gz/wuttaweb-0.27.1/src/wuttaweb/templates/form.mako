## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="page_layout()">
  <div style="display: flex; justify-content: space-between;">

    ## main form
    <div style="flex-grow: 1;">
      ${self.page_content()}
    </div>

    ## tool panels
    ${self.tool_panels_wrapper()}
  </div>
</%def>

<%def name="page_content()">
  % if form is not Undefined:
      <div class="wutta-form-wrapper">
        ${self.render_form_tag()}
      </div>
  % endif
</%def>

<%def name="render_form_tag()">
  ${form.render_vue_tag()}
</%def>

<%def name="tool_panels_wrapper()">
  <div class="tool-panels-wrapper">
    ${self.tool_panels()}
  </div>
</%def>

<%def name="tool_panels()"></%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${self.render_vue_template_form()}
</%def>

<%def name="render_vue_template_form()">
  % if form is not Undefined:
      ## nb. must provide main template to form, so it can
      ## do 'def' lookup as needed for fields template etc.
      ${form.render_vue_template(main_template=self.template)}
  % endif
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  ${self.make_vue_components_form()}
</%def>

<%def name="make_vue_components_form()">
  % if form is not Undefined:
      ${form.render_vue_finalize()}
  % endif
</%def>
