## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="index_title_controls()">
  ${parent.index_title_controls()}

  % if request.has_perm("alembic.dashboard"):
      <wutta-button type="is-primary"
                    tag="a" href="${url('alembic.dashboard')}"
                    icon-left="forward"
                    label="Alembic Dashboard"
                    once />
  % endif
</%def>
