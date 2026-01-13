## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Alembic Dashboard</%def>

<%def name="content_title()"></%def>

<%def name="page_content()">
  <div style="display: flex; gap: 5rem; align-items: start;">

    <div style="width: 40%;">
      <br />

      <b-field label="Script Dir" horizontal>
        <span>{{ script.dir }}</span>
      </b-field>

      <b-field label="Env Location" horizontal>
        <span>{{ script.env_py_location }}</span>
      </b-field>

      <b-field label="Version Locations" horizontal>
        <ul>
          <li v-for="path in script.version_locations">
            {{ path }}
          </li>
        </ul>
      </b-field>

    </div>

    <div>
      <div class="buttons">
        % if request.has_perm("app_tables.list"):
            <wutta-button type="is-primary"
                          tag="a" href="${url('app_tables')}"
                          icon-left="table"
                          label="App Tables"
                          once />
        % endif
        % if request.has_perm("app_tables.create"):
            <wutta-button type="is-primary"
                          tag="a" href="${url('app_tables.create')}"
                          icon-left="plus"
                          label="New Table"
                          once />
        % endif
      </div>
      <div class="buttons">
        % if request.has_perm("alembic.migrations.list"):
            <wutta-button type="is-primary"
                          tag="a" href="${url('alembic.migrations')}"
                          icon-left="forward"
                          label="Alembic Migrations"
                          once />
        % endif
        % if request.has_perm("alembic.migrations.create"):
            <wutta-button type="is-primary"
                          tag="a" href="${url('alembic.migrations.create')}"
                          icon-left="plus"
                          label="New Migration"
                          once />
        % endif
      </div>
      % if request.has_perm("alembic.migrate"):
          <div class="buttons">
            <b-button type="is-warning"
                      icon-pack="fas"
                      icon-left="forward"
                      label="Migrate Database"
                      @click="migrateInit()">
              Migrate Database
            </b-button>
          </div>
      % endif
    </div>
  </div>

  <br />
  <h4 class="block is-size-4">Script Heads</h4>

  <b-table :data="scriptHeads"
           :row-class="getScriptHeadRowClass">
    <b-table-column field="branch_labels" label="Branch" v-slot="props">
      <span>{{ props.row.branch_labels }}</span>
    </b-table-column>
    <b-table-column field="doc" label="Description" v-slot="props">
      <span>{{ props.row.doc }}</span>
    </b-table-column>
    <b-table-column field="is_current" label="Current in DB" v-slot="props">
      <span :class="{'has-text-weight-bold': true, 'has-text-success': props.row.is_current}">{{ props.row.is_current ? "Yes" : "No" }}</span>
    </b-table-column>
    <b-table-column field="revision" label="Revision" v-slot="props">
      <span v-html="props.row.revision"></span>
    </b-table-column>
    <b-table-column field="down_revision" label="Down Revision" v-slot="props">
      <span v-html="props.row.down_revision"></span>
    </b-table-column>
    <b-table-column field="path" label="Path" v-slot="props">
      <span>{{ props.row.path }}</span>
    </b-table-column>
  </b-table>

  <br />
  <h4 class="block is-size-4">Database Heads</h4>

  <b-table :data="dbHeads">
    <b-table-column field="branch_labels" label="Branch" v-slot="props">
      <span>{{ props.row.branch_labels }}</span>
    </b-table-column>
    <b-table-column field="doc" label="Description" v-slot="props">
      <span>{{ props.row.doc }}</span>
    </b-table-column>
    <b-table-column field="revision" label="Revision" v-slot="props">
      <span v-html="props.row.revision"></span>
    </b-table-column>
    <b-table-column field="down_revision" label="Down Revision" v-slot="props">
      <span v-html="props.row.down_revision"></span>
    </b-table-column>
    <b-table-column field="path" label="Path" v-slot="props">
      <span>{{ props.row.path }}</span>
    </b-table-column>
  </b-table>

  % if request.has_perm("alembic.migrate"):
      <${b}-modal has-modal-card
                  :active.sync="migrateShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Migrate Database</p>
          </header>

          <section class="modal-card-body">
            ${h.form(url("alembic.migrate"), method="POST", ref="migrateForm")}
            ${h.csrf_token(request)}

            <p class="block">
              You can provide any revspec target.  Default will
              upgrade to all branch heads.
            </p>

            <div class="block content is-family-monospace">
              <ul>
                <li>alembic upgrade heads</li>
                <li>alembic upgrade poser@head</li>
                <li>alembic downgrade poser@-1</li>
                <li>alembic downgrade poser@base</li>
                <li>alembic downgrade fc3a3bcaa069</li>
              </ul>
            </div>

            <p class="block has-text-weight-bold">
              don&apos;t try that last one ;)
            </p>

            <b-field grouped>

              <b-field label="Direction">
                <b-select name="direction" v-model="migrateDirection">
                  <option value="upgrade">upgrade</option>
                  <option value="downgrade">downgrade</option>
                </b-select>
              </b-field>

              <b-field label="Target Spec"
                       :type="migrateTarget ? null : 'is-danger'">
                <b-input name="revspec" v-model="migrateTarget" />
              </b-field>

            </b-field>

            ${h.end_form()}
          </section>

          <footer class="modal-card-foot">
            <div style="display: flex; gap: 0.5rem;">
            <b-button @click="migrateShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-warning"
                      icon-pack="fas"
                      icon-left="forward"
                      @click="migrateSubmit()"
                      :disabled="migrateSubmitDisabled">
              {{ migrating ? "Working, please wait..." : "Migrate" }}
            </b-button>
            </div>
          </footer>
        </div>
      </${b}-modal>
  % endif

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.script = ${json.dumps(script)|n}
    ThisPageData.scriptHeads = ${json.dumps(script_heads)|n}
    ThisPageData.dbHeads = ${json.dumps(db_heads)|n}

    ThisPage.methods.getScriptHeadRowClass = function(rev) {
        if (!rev.is_current) {
            return 'has-background-warning'
        }
    }

    % if request.has_perm("alembic.migrate"):

        ThisPageData.migrating = false
        ThisPageData.migrateShowDialog = false
        ThisPageData.migrateTarget = "heads"
        ThisPageData.migrateDirection = "upgrade"

        ThisPage.methods.migrateInit = function() {
            this.migrateShowDialog = true
        }

        ThisPage.computed.migrateSubmitDisabled = function() {
            if (this.migrating) {
                return true
            }
            if (!this.migrateTarget) {
                return true
            }
        }

        ThisPage.methods.migrateSubmit = function() {
            this.migrating = true
            this.$refs.migrateForm.submit()
        }

    % endif

  </script>
</%def>
