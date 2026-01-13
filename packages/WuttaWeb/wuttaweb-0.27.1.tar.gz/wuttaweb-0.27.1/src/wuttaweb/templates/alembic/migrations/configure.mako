## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Basics</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field label="Default Branch for new Migrations">
      <b-select name="${config.appname}.alembic.default_revise_branch"
                v-model="simpleSettings['${config.appname}.alembic.default_revise_branch']"
                @input="settingsNeedSaved = true">
        <option :value="null">(none)</option>
        <option v-for="branch in reviseBranchOptions"
                :value="branch">
          {{ branch }}
        </option>
      </b-select>
    </b-field>

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.reviseBranchOptions = ${json.dumps(revise_branch_options)|n}

  </script>
</%def>
