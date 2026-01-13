## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Basics</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field label="Default location for new Master Views">
      <b-select name="wuttaweb.master_views.default_module_dir"
                v-model="simpleSettings['wuttaweb.master_views.default_module_dir']"
                @input="settingsNeedSaved = true">
        <option :value="null">(none)</option>
        <option v-for="modpath in viewModuleLocations"
                :value="modpath">
          {{ modpath }}
        </option>
      </b-select>
    </b-field>

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.viewModuleLocations = ${json.dumps(view_module_locations)|n}

  </script>
</%def>
