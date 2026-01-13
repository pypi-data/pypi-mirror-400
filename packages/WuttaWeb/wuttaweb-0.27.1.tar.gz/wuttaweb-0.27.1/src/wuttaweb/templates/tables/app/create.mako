## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>

    ## indent prev/next step buttons at page bottom
    .buttons.steps-control {
        margin: 3rem;
    }

    ## nb. this fixes some field labels within panels.  i guess
    ## the fields are not wide enough due to flexbox?
    .label {
        white-space: nowrap;
    }

  </style>
</%def>

<%def name="page_content()">

  % if not alembic_is_current:
      <b-notification type="is-warning">
        <p class="block">
          Database is not current!  There are
          ${h.link_to("pending migrations", url("alembic.dashboard"))}.
        </p>
        <p class="block">
          (This will be a problem if you wish to auto-generate a migration for a new table.)
        </p>
      </b-notification>
  % endif

  <b-steps v-model="activeStep"
           @input="activeStepChanged"
           :animated="false"
           rounded
           :has-navigation="false"
           vertical
           icon-pack="fas">

    <b-step-item step="1"
                 value="enter-details"
                 label="Enter Details"
                 clickable>

      <h3 class="is-size-3 block">Enter Details</h3>

      <div class="block" style="width: 70%;">

        <b-field label="Table Name" horizontal>
          <b-input v-model="tableName"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Model Class" horizontal>
          <b-input v-model="tableModelName"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Model Title" horizontal>
          <b-input v-model="tableModelTitle"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Model Title Plural" horizontal>
          <b-input v-model="tableModelTitlePlural"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Description" horizontal>
          <b-input v-model="tableDescription"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Versioning" horizontal>
          <b-checkbox v-model="tableVersioned"
                      @input="dirty = true">
            Record version data for this table
          </b-checkbox>
        </b-field>

      </div>


      <div class="level-left">
        <div class="level-item">
          <h4 class="block is-size-4">Columns</h4>
        </div>
        <div class="level-item">
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="plus"
                    @click="tableAddColumn()">
            New
          </b-button>
        </div>
      </div>

      <b-table :data="tableColumns">

        <b-table-column field="name"
                        label="Name"
                        v-slot="props">
          {{ props.row.name }}
        </b-table-column>

        <b-table-column field="data_type"
                        label="Data Type"
                        v-slot="props">
          {{ formatDataType(props.row.data_type) }}
        </b-table-column>

        <b-table-column field="nullable"
                        label="Nullable"
                        v-slot="props">
          {{ props.row.nullable ? "Yes" : "No" }}
        </b-table-column>

        <b-table-column field="versioned"
                        label="Versioned"
                        :visible="tableVersioned"
                        v-slot="props">
          ## nb. versioned may be a string e.g. "n/a"
          {{ typeof(props.row.versioned) == "boolean" ? (props.row.versioned ? "Yes" : "No") : props.row.versioned }}
        </b-table-column>

        <b-table-column field="description"
                        label="Description"
                        v-slot="props">
          {{ props.row.description }}
        </b-table-column>

        <b-table-column field="actions"
                        label="Actions"
                        v-slot="props">
          <a v-if="props.row.name != 'uuid'"
             href="#"
             @click.prevent="tableEditColumn(props.row)">
            <i class="fas fa-edit"></i>
            Edit
          </a>
          &nbsp;

          <a v-if="props.row.name != 'uuid'"
             href="#"
             class="has-text-danger"
             @click.prevent="tableDeleteColumn(props.index)">
            <i class="fas fa-trash"></i>
            Delete
          </a>
          &nbsp;
        </b-table-column>

      </b-table>

      <b-modal has-modal-card
               :active.sync="editingColumnShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">
              {{ (editingColumn && editingColumn.name) ? "Edit" : "New" }} Column
            </p>
          </header>

          <form action="#" @submit="editingColumnOnSubmit">

            <section class="modal-card-body">

              <b-field label="Name">
                <b-input v-model="editingColumnName"
                         ref="editingColumnName" />
              </b-field>

              <b-field grouped>

                <b-field label="Data Type">
                  <b-select v-model="editingColumnDataType">
                    <option value="String">String</option>
                    <option value="Boolean">Boolean</option>
                    <option value="Integer">Integer</option>
                    <option value="Numeric">Numeric</option>
                    <option value="Date">Date</option>
                    <option value="DateTime">DateTime</option>
                    <option value="Text">Text</option>
                    <option value="LargeBinary">LargeBinary</option>
                    <option value="UUID">UUID</option>
                    <option value="_fk_uuid_">UUID+FK</option>
                    <option value="_other_">Other</option>
                  </b-select>
                </b-field>

                <b-field v-if="editingColumnDataType == 'String'"
                         label="Length"
                         :type="{'is-danger': !editingColumnDataTypeLength}"
                         style="max-width: 6rem;">
                  <b-input v-model="editingColumnDataTypeLength" />
                </b-field>

                <b-field v-if="editingColumnDataType == 'Numeric'"
                         label="Precision"
                         :type="{'is-danger': !editingColumnDataTypePrecision}"
                         style="max-width: 6rem;">
                  <b-input v-model="editingColumnDataTypePrecision" />
                </b-field>

                <b-field v-if="editingColumnDataType == 'Numeric'"
                         label="Scale"
                         :type="{'is-danger': !editingColumnDataTypeScale}"
                         style="max-width: 6rem;">
                  <b-input v-model="editingColumnDataTypeScale" />
                </b-field>

                <b-field v-if="editingColumnDataType == '_fk_uuid_'"
                         label="Reference Table"
                         :type="{'is-danger': !editingColumnDataTypeReference}">
                  <b-select v-model="editingColumnDataTypeReference">
                    <option v-for="table in existingTables"
                            :value="table.name">
                      {{ table.name }}
                    </option>
                  </b-select>
                </b-field>

                <b-field v-if="editingColumnDataType == '_other_'"
                         label="Literal (include parens!)"
                         :type="{'is-danger': !editingColumnDataTypeLiteral}"
                         expanded>
                  <b-input v-model="editingColumnDataTypeLiteral" />
                </b-field>

              </b-field>

              <b-field grouped>

                <b-field label="Nullable">
                  <b-checkbox v-model="editingColumnNullable"
                              native-value="true">
                    {{ editingColumnNullable }}
                  </b-checkbox>
                </b-field>

                <b-field label="Versioned"
                         v-if="tableVersioned">
                  <b-checkbox v-model="editingColumnVersioned"
                              native-value="true">
                    {{ editingColumnVersioned }}
                  </b-checkbox>
                </b-field>

                <b-field v-if="editingColumnDataType == '_fk_uuid_'"
                         label="Relationship">
                  <b-input v-model="editingColumnRelationship" />
                </b-field>

              </b-field>

              <b-field label="Description">
                <b-input v-model="editingColumnDescription" />
              </b-field>

            </section>

            <footer class="modal-card-foot">
              <b-button @click="editingColumnShowDialog = false">
                Cancel
              </b-button>
              <b-button type="is-primary"
                        native-type="submit"
                        icon-pack="fas"
                        icon-left="save">
                Save
              </b-button>
            </footer>

          </form>

        </div>
      </b-modal>

      <div class="buttons steps-control">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('write-model')">
          Details are complete
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('write-model')">
          Skip
        </b-button>
      </div>

    </b-step-item>

    <b-step-item step="2"
                 value="write-model"
                 label="Write Model"
                 clickable>

      <h3 class="is-size-3 block">Write Model</h3>

      <p class="block">
        This will create a new Python module with your table/model definition.
      </p>

      <div style="margin-left: 2rem;">

        <b-field grouped>

          <b-field label="Table Name">
            {{ tableName }}
          </b-field>

          <b-field label="Model Class">
            {{ tableModelName }}
          </b-field>

        </b-field>

        <b-field label="Target File">
          <div>
            <b-field>
              <b-input v-model="tableModelFile" />
            </b-field>
            <b-field>
              <b-checkbox v-model="tableModelFileOverwrite">
                Overwrite file if it exists
              </b-checkbox>
            </b-field>
          </div>
        </b-field>

      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('enter-details')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="save"
                  @click="writeModelFile()"
                  :disabled="writingModelFile">
          {{ writingModelFile ? "Working, please wait..." : "Write model class to file" }}
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('confirm-model')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="3"
                 value="confirm-model"
                 label="Confirm Model"
                 clickable>

      <h3 class="is-size-3 block">Confirm Model</h3>

      <div v-if="wroteModelFile"
           class="block">

        <p class="block">
          Code was generated to file: &nbsp; &nbsp;
          <wutta-copyable-text :text="wroteModelFile"
                               class="is-family-code" />
        </p>

        <p class="block">
          Review and modify code to your liking, then include the new
          model/module in your root model/module.
        </p>

        <p class="block">
          Typical root model/module is at: &nbsp; &nbsp;
          <wutta-copyable-text text="${model_dir}/__init__.py"
                               class="is-family-code" />
        </p>

        <p class="block">
          The root model/module should contain something like:
        </p>

        <p class="block is-family-code" style="padding-left: 3rem;">
          from .{{ tableModelFileModuleName }} import {{ tableModelName }}
        </p>

        <p class="block">
          Once you&apos;ve done all that, the web app must be restarted.
          This may happen automatically depending on your setup.
          Test the model import status below.
        </p>

      </div>

      <div v-if="!wroteModelFile"
           class="block">

        <p class="block">
          At this point your new class should be present in the app
          model.  Test below.
        </p>

      </div>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            Model Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span v-if="!modelImporting && !modelImported && !modelImportProblem">
                    check not yet attempted
                  </span>
                  <span v-if="modelImporting" class="is-italic">
                    checking model...
                  </span>
                  <span v-if="!modelImporting && modelImported && !modelImportProblem"
                        class="has-text-success has-text-weight-bold">
                    {{ modelImported }} found in app model
                  </span>
                  <span v-if="!modelImporting && modelImportProblem"
                        class="has-text-danger has-text-weight-bold">
                    {{ modelImported }} not found in app model
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Model Class">
                    <b-input v-model="modelImportName" />
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="modelImportTest()">
                    Check for Model
                  </b-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('write-model')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('write-migration')">
          Model class looks good
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('write-migration')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="4"
                 value="write-migration"
                 label="Write Migration"
                 clickable>

      <h3 class="is-size-3 block">Write Migration</h3>

      <p class="block">
        This will create a new Alembic Migration script, with all
        pending schema changes.
      </p>

      <p class="block">
        Be sure to choose the correct migration branch!
      </p>

      <div style="margin-left: 2rem;">

        <b-field label="Branch">
          <b-select v-model="alembicBranch">
            <option v-for="branch in alembicBranchOptions"
                    :value="branch">
              {{ branch }}
            </option>
          </b-select>
        </b-field>

        <b-field label="Description">
          <b-input v-model="revisionMessage" />
        </b-field>

      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('confirm-model')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="save"
                  @click="writeRevisionScript()"
                  :disabled="!alembicBranch || writingRevisionScript">
          {{ writingRevisionScript ? "Working, please wait..." : "Write migration script" }}
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('confirm-migration')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="5"
                 value="confirm-migration"
                 label="Confirm Migration"
                 clickable>

      <h3 class="is-size-3 block">Confirm Migration</h3>

      <p v-if="revisionScript"
         class="block">
        Script was generated to file: &nbsp; &nbsp;
        <wutta-copyable-text :text="revisionScript"
                             class="is-family-code" />
      </p>

      <p class="block">
        Review and modify the new migration script(s) to your liking, then proceed.
      </p>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('write-migration')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('migrate-db')">
          Migration scripts look good
        </b-button>
          <b-button icon-pack="fas"
                    icon-left="arrow-right"
                    @click="showStep('migrate-db')"
                    >
            Skip
          </b-button>
      </div>
    </b-step-item>

    <b-step-item step="6"
                 value="migrate-db"
                 label="Migrate Database"
                 clickable>

      <h3 class="is-size-3 block">Migrate Database</h3>

      <p class="block">
        If all migration scripts are ready to go, it&apos;s time to run them.
      </p>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('confirm-migration')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="forward"
                  @click="migrateDatabase()"
                  :disabled="migratingDatabase">
          {{ migratingDatabase ? "Working, please wait..." : "Migrate database" }}
        </b-button>
          <b-button icon-pack="fas"
                    icon-left="arrow-right"
                    @click="showStep('confirm-table')"
                    >
            Skip
          </b-button>

      </div>
    </b-step-item>

    <b-step-item step="7"
                 value="confirm-table"
                 label="Confirm Table"
                 clickable>

      <h3 class="is-size-3 block">Confirm Table</h3>

      <p class="block">
        At this point your new table should be present in the
        database.  Test below.
      </p>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            Table Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span v-if="!tableChecking && !tableChecked">
                    check not yet attempted
                  </span>
                  <span v-if="tableChecking" class="is-italic">
                    checking table...
                  </span>
                  <span v-if="!tableChecking && tableChecked && !tableCheckProblem"
                        class="has-text-success has-text-weight-bold">
                    {{ tableChecked }} found in database
                  </span>
                  <span v-if="!tableChecking && tableCheckProblem"
                        class="has-text-danger has-text-weight-bold">
                    {{ tableChecked }} not found in database
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Table Name">
                    <b-input v-model="tableName" />
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="tableCheck()">
                    Check for Table
                  </b-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('migrate-db')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('commit-code')">
          Table looks good
        </b-button>
          <b-button icon-pack="fas"
                    icon-left="arrow-right"
                    @click="showStep('commit-code')">
            Skip
          </b-button>
      </div>
    </b-step-item>

    <b-step-item step="8"
                 value="commit-code"
                 label="Commit Code"
                 clickable>

      <h3 class="is-size-3 block">Commit Code</h3>

      <p class="block">
        Hope you&apos;re having a great day.
      </p>

      <p class="block">
        Don&apos;t forget to commit code changes to your source repo.
      </p>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('confirm-table')">
          Back
        </b-button>
        <wutta-button type="is-primary"
                     tag="a" :href="tableURL"
                     icon-left="arrow-right"
                     :label="`Show my new table: ${'$'}{tableName}`"
                      once
                      :disabled="!tableURL" />
      </div>
    </b-step-item>

  </b-steps>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    // nb. for warning user they may lose changes if leaving page
    ThisPageData.dirty = false

    ThisPageData.wizardActionURL = "${url(f'{route_prefix}.wizard_action')}"

    ThisPageData.activeStep = location.hash ? location.hash.substring(1) : "enter-details"

    ThisPage.methods.activeStepChanged = function(value) {
        location.hash = value
    }

    ThisPage.methods.showStep = function(step) {
        this.activeStep = step
        location.hash = step
    }

    ## TODO: should customize instead of using poser here
    ##ThisPageData.tableName = '${app.get_table_prefix()}_widget'
    ThisPageData.tableName = "poser_widget"
    ##ThisPageData.tableModelName = '${app.get_class_prefix()}Widget'
    ThisPageData.tableModelName = "PoserWidget"
    ThisPageData.tableModelTitle = "Poser Widget"
    ThisPageData.tableModelTitlePlural = "Poser Widgets"

    ThisPageData.tableDescription = "Represents a cool widget for ${app.get_title()}."
    ThisPageData.tableVersioned = true

    ThisPageData.existingTables = ${json.dumps(existing_tables)|n}

    ThisPageData.tableColumns = [{
        name: "uuid",
        data_type: {type: "UUID"},
        nullable: false,
        description: "UUID primary key",
        versioned: "n/a",
    }]

    ThisPageData.editingColumnShowDialog = false
    ThisPageData.editingColumn = null
    ThisPageData.editingColumnName = null
    ThisPageData.editingColumnDataType = null
    ThisPageData.editingColumnDataTypeLength = null
    ThisPageData.editingColumnDataTypePrecision = null
    ThisPageData.editingColumnDataTypeScale = null
    ThisPageData.editingColumnDataTypeReference = null
    ThisPageData.editingColumnDataTypeLiteral = null
    ThisPageData.editingColumnNullable = true
    ThisPageData.editingColumnDescription = null
    ThisPageData.editingColumnVersioned = true
    ThisPageData.editingColumnRelationship = null

    ThisPage.methods.tableAddColumn = function() {
        this.editingColumn = null
        this.editingColumnName = null
        this.editingColumnDataType = null
        this.editingColumnDataTypeLength = null
        this.editingColumnDataTypePrecision = null
        this.editingColumnDataTypeScale = null
        this.editingColumnDataTypeReference = null
        this.editingColumnDataTypeLiteral = null
        this.editingColumnNullable = true
        this.editingColumnDescription = null
        this.editingColumnVersioned = true
        this.editingColumnRelationship = null
        this.editingColumnShowDialog = true
        this.$nextTick(() => {
            this.$refs.editingColumnName.focus()
        })
    }

    ThisPage.methods.tableEditColumn = function(column) {
        this.editingColumn = column
        this.editingColumnName = column.name
        this.editingColumnDataType = column.data_type.type
        this.editingColumnDataTypeLength = column.data_type.length
        this.editingColumnDataTypePrecision = column.data_type.precision
        this.editingColumnDataTypeScale = column.data_type.scale
        this.editingColumnDataTypeReference = column.data_type.reference
        this.editingColumnDataTypeLiteral = column.data_type.literal
        this.editingColumnNullable = column.nullable
        this.editingColumnDescription = column.description
        this.editingColumnVersioned = column.versioned
        this.editingColumnRelationship = column.relationship
        this.editingColumnShowDialog = true
        this.$nextTick(() => {
            this.$refs.editingColumnName.focus()
        })
    }

    ThisPage.methods.formatDataType = function(dataType) {
        if (dataType.type == 'String') {
            return `sa.String(length=${'$'}{dataType.length})`
        } else if (dataType.type == 'Numeric') {
            return `sa.Numeric(precision=${'$'}{dataType.precision}, scale=${'$'}{dataType.scale})`
        } else if (dataType.type == 'UUID') {
            return `UUID()`
        } else if (dataType.type == '_fk_uuid_') {
            return `UUID()`
        } else if (dataType.type == '_other_') {
            return dataType.literal
        } else {
            return `sa.${'$'}{dataType.type}()`
        }
    }

    ThisPage.watch.editingColumnDataTypeReference = function(newval, oldval) {
        this.editingColumnRelationship = newval
        if (newval && !this.editingColumnName) {
            this.editingColumnName = `${'$'}{newval}_uuid`
        }
    }

    ThisPage.methods.editingColumnOnSubmit = function(event) {
        event.preventDefault()
        this.editingColumnSave()
    }

    ThisPage.methods.editingColumnSave = function() {
        let column
        if (this.editingColumn) {
            column = this.editingColumn
        } else {
            column = {}
            this.tableColumns.push(column)
        }

        column.name = this.editingColumnName

        const dataType = {type: this.editingColumnDataType}
        if (dataType.type == 'String') {
            dataType.length = this.editingColumnDataTypeLength
        } else if (dataType.type == 'Numeric') {
            dataType.precision = this.editingColumnDataTypePrecision
            dataType.scale = this.editingColumnDataTypeScale
        } else if (dataType.type == '_fk_uuid_') {
            dataType.reference = this.editingColumnDataTypeReference
        } else if (dataType.type == '_other_') {
            dataType.literal = this.editingColumnDataTypeLiteral
        }
        column.data_type = dataType

        column.nullable = this.editingColumnNullable
        column.description = this.editingColumnDescription
        column.versioned = this.editingColumnVersioned
        column.relationship = this.editingColumnRelationship

        this.dirty = true
        this.editingColumnShowDialog = false
    }

    ThisPage.methods.tableDeleteColumn = function(index) {
        if (confirm("Really delete this column?")) {
            this.tableColumns.splice(index, 1)
            this.dirty = true
        }
    }

    ThisPageData.tableModelFile = "${model_dir}/widget.py"
    ThisPageData.tableModelFileOverwrite = false
    ThisPageData.writingModelFile = false
    ThisPageData.wroteModelFile = null

    ThisPage.methods.writeModelFile = function() {
        this.writingModelFile = true

        this.modelImportName = this.tableModelName
        this.modelImported = null
        this.modelImportProblem = false

        for (let column of this.tableColumns) {
            column.formatted_data_type = this.formatDataType(column.data_type)
        }

        const params = {
            action: "write_model_file",
            table_name: this.tableName,
            model_name: this.tableModelName,
            model_title: this.tableModelTitle,
            model_title_plural: this.tableModelTitlePlural,
            description: this.tableDescription,
            versioned: this.tableVersioned,
            columns: this.tableColumns,
            module_file: this.tableModelFile,
            overwrite: this.tableModelFileOverwrite,
        }

        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.wroteModelFile = this.tableModelFile
            this.writingModelFile = false
            this.showStep("confirm-model")
        }, response => {
            this.writingModelFile = false
        })
    }

    ##ThisPageData.modelImportName = '${app.get_class_prefix()}Widget'
    ThisPageData.modelImportName = "PoserWidget"
    ThisPageData.modelImported = null
    ThisPageData.modelImporting = false
    ThisPageData.modelImportProblem = false

    ThisPage.computed.tableModelFileModuleName = function() {
        let path = this.tableModelFile
        path = path.replace(/^.*\//, "")
        path = path.replace(/\.py$/, "")
        return path
    }

    ThisPage.methods.modelImportTest = function() {
        this.modelImporting = true
        const params = {
            action: "check_model",
            model_name: this.modelImportName,
        }
        this.wuttaPOST(this.wizardActionURL, params, response => {

            // nb. we slow the response down just a bit so the user
            // can "see" that a *new* import was in fact attempted.
            setTimeout(() => {
                this.modelImporting = false
                if (response.data.problem) {
                    this.modelImportProblem = true
                    this.modelImported = this.modelImportName
                } else {
                    this.modelImportProblem = false
                    this.modelImported = this.modelImportName
                    this.revisionMessage = `add ${"$"}{this.tableModelTitlePlural}`
                }
            }, 200)
        })
    }

    ThisPageData.alembicBranchOptions = ${json.dumps(migration_branch_options)|n}
    ThisPageData.alembicBranch = ${json.dumps(migration_branch)|n}

    ThisPageData.writingRevisionScript = false
    ThisPageData.revisionMessage = null
    ThisPageData.revisionScript = null

    ThisPage.methods.writeRevisionScript = function() {
        this.writingRevisionScript = true
        const params = {
            action: "write_revision_script",
            branch: this.alembicBranch,
            message: this.revisionMessage,
        }
        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.writingRevisionScript = false
            this.revisionScript = response.data.script
            this.showStep("confirm-migration")
        }, response => {
            this.writingRevisionScript = false
        })
    }

    ThisPageData.migratingDatabase = false

    ThisPage.methods.migrateDatabase = function() {
        this.migratingDatabase = true
        const params = {action: "migrate_db"}
        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.migratingDatabase = false
            this.showStep('confirm-table')
        }, response => {
            this.migratingDatabase = false
        })
    }

    ThisPageData.tableChecking = false
    ThisPageData.tableChecked = null
    ThisPageData.tableCheckProblem = null
    ThisPageData.tableURL = null

    ThisPage.methods.tableCheck = function() {
        this.tableChecking = true
        const params = {
            action: "check_table",
            name: this.tableName,
        }
        this.wuttaPOST(this.wizardActionURL, params, response => {

            // nb. we slow the response down just a bit so the user
            // can "see" that a *new* import was in fact attempted.
            setTimeout(() => {
                this.tableChecking = false
                this.tableChecked = this.tableName
                if (response.data.problem) {
                    this.tableCheckProblem = true
                } else {
                    this.tableCheckProblem = false
                    this.tableURL = response.data.url
                }
            }, 200)
        })
    }

    // cf. https://stackoverflow.com/a/56551646
    ThisPage.methods.beforeWindowUnload = function(e) {

        // warn user if navigating away would lose changes
        if (this.dirty) {
            e.preventDefault()
            e.returnValue = ''
        }
    }

    ThisPage.created = function() {
        window.addEventListener("beforeunload", this.beforeWindowUnload)
    }

  </script>
</%def>
