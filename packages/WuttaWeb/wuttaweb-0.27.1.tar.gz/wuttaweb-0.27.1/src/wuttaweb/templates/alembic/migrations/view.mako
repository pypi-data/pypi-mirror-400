## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

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
