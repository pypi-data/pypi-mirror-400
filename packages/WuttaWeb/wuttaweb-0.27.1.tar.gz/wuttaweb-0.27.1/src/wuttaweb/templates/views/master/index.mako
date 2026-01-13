## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="page_content()">
  <div class="buttons">

    % if request.has_perm("app_tables.list"):
        <wutta-button type="is-primary"
                      tag="a" href="${url('app_tables')}"
                      icon-left="table"
                      label="App Tables"
                      once />
    % endif

  </div>
  ${parent.page_content()}
</%def>
