## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="page_content()">
  <div class="buttons">

    % if request.has_perm("alembic.dashboard"):
        <wutta-button type="is-primary"
                      tag="a" href="${url('alembic.dashboard')}"
                      icon-left="forward"
                      label="Alembic Dashboard"
                      once />
    % endif

    % if request.has_perm("alembic.migrations.list"):
        <wutta-button type="is-primary"
                      tag="a" href="${url('alembic.migrations')}"
                      icon-left="forward"
                      label="Alembic Migrations"
                      once />
    % endif

    % if request.has_perm("master_views.list"):
        <wutta-button type="is-primary"
                      tag="a" href="${url('master_views')}"
                      icon-left="eye"
                      label="Master Views"
                      once />
    % endif

  </div>
  ${parent.page_content()}
</%def>
