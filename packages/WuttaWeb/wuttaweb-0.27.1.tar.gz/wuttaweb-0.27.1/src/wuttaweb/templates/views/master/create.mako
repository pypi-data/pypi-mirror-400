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

## nb. no need for standard form here
<%def name="render_vue_template_form()"></%def>
<%def name="make_vue_components_form()"></%def>

<%def name="page_content()">

  <b-steps v-model="activeStep"
           @input="activeStepChanged"
           :animated="false"
           rounded
           :has-navigation="false"
           vertical
           icon-pack="fas">

    <b-step-item step="1"
                 value="choose-model"
                 label="Choose Model"
                 clickable>

      <h3 class="is-size-3 block">Choose Model</h3>

      <p class="block">
        You can choose a particular model, or just enter a name if the
        view needs to work with something outside the app database.
      </p>

      <div style="margin-left: 2rem; width: 70%;">

        <div class="field">
          <b-radio v-model="modelOption"
                   native-value="model_class">
            Choose model from app database
          </b-radio>
        </div>

        <div v-show="modelOption == 'model_class'"
             style="padding: 1rem 0;">

          <b-field label="Model" horizontal>
            <b-select v-model="modelClass">
              <option v-for="name in modelClasses"
                      :value="name">
                {{ name }}
              </option>
            </b-select>
          </b-field>
        </div>

        <div class="field">
          <b-radio v-model="modelOption"
                   native-value="model_name">
            Provide just a model name
          </b-radio>
        </div>

        <div v-show="modelOption == 'model_name'"
             style="padding: 1rem 0;">

          <b-field label="Model Name" horizontal>
            <b-input v-model="modelName" />
          </b-field>

          <div style="margin: 2rem;">

            <p class="block">
              This name will be used to suggest defaults for other class attributes.
            </p>

            <p class="block">
              It is best to use a "singular Python variable name" style;
              for instance these are real examples:
            </p>

            <ul class="block is-family-code">
              <li>app_table</li>
              <li>email_setting</li>
              <li>master_view</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="buttons steps-control">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="modelLooksGood()"
                  :disabled="modelLooksBad">
          Model looks good
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('enter-details')">
          Skip
        </b-button>
      </div>

    </b-step-item>

    <b-step-item step="2"
                 value="enter-details"
                 label="Enter Details"
                 clickable>

      <b-loading v-model="fetchingSuggestions" />

      <h3 class="is-size-3 block">Enter Details</h3>

      <div class="block" style="width: 70%;">

        <b-field :label="modelLabel" horizontal>
          <span>{{ modelName }}</span>
        </b-field>

        <b-field label="Model Title" horizontal>
          <b-input v-model="modelTitle"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Model Title Plural" horizontal>
          <b-input v-model="modelTitlePlural"
                   @input="dirty = true" />
        </b-field>

        <b-field label="View Class Name" horizontal>
          <b-input v-model="className"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Route Prefix" horizontal>
          <b-input v-model="routePrefix"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Permission Prefix" horizontal>
          <b-input v-model="permissionPrefix"
                   @input="dirty = true" />
        </b-field>

        <b-field label="URL Prefix" horizontal>
          <b-input v-model="urlPrefix"
                   @input="dirty = true" />
        </b-field>

        <b-field label="Template Prefix" horizontal>
          <b-input v-model="templatePrefix"
                   @input="dirty = true" />
        </b-field>

        <b-field label="CRUD Routes" horizontal>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-model="listable">List</b-checkbox>
            <b-checkbox v-model="creatable">Create</b-checkbox>
            <b-checkbox v-model="viewable">View</b-checkbox>
            <b-checkbox v-model="editable">Edit</b-checkbox>
            <b-checkbox v-model="deletable">Delete</b-checkbox>
          </div>
        </b-field>

        <b-field v-if="listable"
                 label="Grid Columns"
                 horizontal>
          <b-input type="textarea" v-model="gridColumns" />
        </b-field>

        <b-field v-if="creatable || viewable || editable || deletable"
                 label="Form Fields"
                 horizontal>
          <b-input type="textarea" v-model="formFields" />
        </b-field>

      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('choose-model')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('write-view')">
          Details look good
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('write-view')">
          Skip
        </b-button>
      </div>

    </b-step-item>

    <b-step-item step="3"
                 value="write-view"
                 label="Write View"
                 clickable>

      <h3 class="is-size-3 block">Write View</h3>

      <p class="block">
        This will create a new Python module with your view class definition.
      </p>

      <div style="margin-left: 2rem;">

        <b-field grouped>

          <b-field label="View Class Name">
            {{ className }}
          </b-field>

          <b-field label="Model Name">
            {{ modelClass || modelName }}
          </b-field>

        </b-field>

        <b-field label="View Location">
          <b-select v-model="viewModuleDir">
            <option :value="null">(other)</option>
            <option v-for="path in viewModuleDirs"
                    :value="path">
              {{ path }}
            </option>
          </b-select>
        </b-field>

        <b-field label="Target File">
          <div>
            <b-field>
              <b-input v-if="!viewModuleDir"
                       v-model="classFilePath" />
              <div v-if="viewModuleDir"
                   style="display: flex; gap: 0.5rem; align-items: center;">
                <span>{{ viewModuleDir }}</span>
                <span>/</span>
                <b-input style="display: inline-block;" v-model="classFileName" />
              </div>
            </b-field>
            <b-field>
              <b-checkbox v-model="classFileOverwrite">
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
                  @click="writeViewFile()"
                  :disabled="writingViewFile">
          {{ writingViewFile ? "Working, please wait..." : "Write view class to file" }}
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('confirm-route')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="4"
                 value="confirm-route"
                 label="Confirm Route"
                 clickable>

      <h3 class="is-size-3 block">Confirm Route</h3>

      <div v-if="wroteViewFile"
           class="block">

        <p class="block">
          Code was generated to file: &nbsp; &nbsp;
          <wutta-copyable-text :text="wroteViewFile"
                               class="is-family-code" />
        </p>

        <p class="block">
          Review and modify code to your liking, then include the new
          view/module in your view config.
        </p>

        <p class="block">
          Typical view config might be at: &nbsp; &nbsp;
          <wutta-copyable-text :text="viewConfigPath"
                               class="is-family-code" />
        </p>

        <p class="block">
          The view config should contain something like:
        </p>

        <pre class="block is-family-code" style="padding-left: 3rem;">def includeme(config):

    # ..various things..

    config.include("{{ viewModulePath }}")</pre>

        <p class="block">
          Once you&apos;ve done all that, the web app must be
          restarted.  This may happen automatically depending on your
          setup.  Test the route status below.
        </p>

      </div>

      <div v-if="!wroteViewFile"
           class="block">

        <p class="block">
          At this point your new view/route should be present in the app.  Test below.
        </p>

      </div>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            Route Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span v-if="!routeChecking && !routeChecked && !routeCheckProblem">
                    check not yet attempted
                  </span>
                  <span v-if="routeChecking" class="is-italic">
                    checking route...
                  </span>
                  <span v-if="!routeChecking && routeChecked && !routeCheckProblem"
                        class="has-text-success has-text-weight-bold">
                    {{ routeChecked }} found in app routes
                  </span>
                  <span v-if="!routeChecking && routeCheckProblem"
                        class="has-text-danger has-text-weight-bold">
                    {{ routeChecked }} not found in app routes
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Route">
                    <b-input v-model="routeCheckRoute" />
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="routeCheck()">
                    Check for Route
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
                  @click="showStep('write-view')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('add-to-menu')"
                  :disabled="routeChecking || !routeChecked || routeCheckProblem">
          Route looks good
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('add-to-menu')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="5"
                 value="add-to-menu"
                 label="Add to Menu"
                 clickable>

      <h3 class="is-size-3 block">Add to Menu</h3>

      <p class="block">
        You probably want to add a menu entry for the view, but it&apos;s optional.
      </p>

      <p class="block">
        Edit the menu file: &nbsp; &nbsp;
        <wutta-copyable-text :text="menuFilePath"
                             class="is-family-code" />
      </p>

      <p class="block">
        Add this entry wherever you like:
      </p>

      <pre class="block is-family-code" style="padding-left: 3rem;">{
    "title": "{{ modelTitlePlural }}",
    "route": "{{ routePrefix }}",
    "perm": "{{ permissionPrefix }}.list",
}</pre>

      <p class="block">
        Occasionally an entry like this might also be useful:
      </p>

      <pre class="block is-family-code" style="padding-left: 3rem;">{
    "title": "New {{ modelTitle }}",
    "route": "{{ routePrefix }}.create",
    "perm": "{{ permissionPrefix }}.create",
}</pre>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('confirm-route')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('grant-access')">
          Menu looks good
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('grant-access')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="6"
                 value="grant-access"
                 label="Grant Access"
                 clickable>

      <h3 class="is-size-3 block">Grant Access</h3>

      <p class="block">
        You can grant access to each CRUD route, for any role(s) you like.
      </p>

      <div style="margin-left: 3rem;">

        <div v-if="listable" class="block">
          <h4 class="is-size-4 block">List {{ modelTitlePlural }}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-for="role in roles"
                        :key="role.uuid"
                        v-model="listingRoles[role.uuid]">
              {{ role.name }}
            </b-checkbox>
          </div>
        </div>

        <div v-if="creatable" class="block">
          <h4 class="is-size-4 block">Create {{ modelTitle }}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-for="role in roles"
                        :key="role.uuid"
                        v-model="creatingRoles[role.uuid]">
              {{ role.name }}
            </b-checkbox>
          </div>
        </div>

        <div v-if="viewable" class="block">
          <h4 class="is-size-4 block">View {{ modelTitle }}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-for="role in roles"
                        :key="role.uuid"
                        v-model="viewingRoles[role.uuid]">
              {{ role.name }}
            </b-checkbox>
          </div>
        </div>

        <div v-if="editable" class="block">
          <h4 class="is-size-4 block">Edit {{ modelTitle }}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-for="role in roles"
                        :key="role.uuid"
                        v-model="editingRoles[role.uuid]">
              {{ role.name }}
            </b-checkbox>
          </div>
        </div>

        <div v-if="deletable" class="block">
          <h4 class="is-size-4 block">Delete {{ modelTitle }}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <b-checkbox v-for="role in roles"
                        :key="role.uuid"
                        v-model="deletingRoles[role.uuid]">
              {{ role.name }}
            </b-checkbox>
          </div>
        </div>
      </div>

      <div class="buttons steps-control">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('add-to-menu')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="applyPermissions()"
                  :disabled="applyingPermissions">
          {{ applyingPermissions ? "Working, please wait..." : "Apply these permissions" }}
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('commit-code')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="7"
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
                  @click="showStep('grant-access')">
          Back
        </b-button>
        <wutta-button type="is-primary"
                      tag="a" :href="viewURL"
                      icon-left="arrow-right"
                      :label="`Show my new view: ${'$'}{viewPath}`"
                      once
                      :disabled="!viewURL" />
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

    ThisPageData.activeStep = location.hash ? location.hash.substring(1) : "choose-model"

    ThisPage.methods.activeStepChanged = function(value) {
        location.hash = value
    }

    ThisPage.methods.showStep = function(step) {
        this.activeStep = step
        location.hash = step
    }

    ThisPageData.modelOption = "model_class"
    ThisPageData.modelClasses = ${json.dumps(app_models)|n}
    ThisPageData.modelClass = null
    ThisPageData.modelName = "poser_widget"

    ThisPage.mounted = function() {
        const params = new URLSearchParams(location.search)
        if (params.has('modelClass')) {
            this.modelOption = "model_class"
            this.modelClass = params.get('modelClass')
        }
    }

    ThisPage.computed.modelLabel = function() {
        if (this.modelOption == "model_class") {
            return "Model Class"
        }
        if (this.modelOption == "model_name") {
            return "Model Name"
        }
    }

    ThisPage.computed.modelLooksBad = function() {
        if (this.modelOption == "model_class") {
            return !this.modelClass
        }
        if (this.modelOption == "model_name") {
            return !(this.modelName || "").trim()
        }
    }

    ThisPage.methods.modelLooksGood = function() {

        if (this.modelOption == "model_class") {
            // nb. from now on model name == class name
            this.modelName = this.modelClass
        }

        this.fetchingSuggestions = true

        const params = {
            action: "suggest_details",
            model_option: this.modelOption,
            model_name: this.modelName,
        }

        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.modelTitle = response.data.model_title
            this.modelTitlePlural = response.data.model_title_plural
            this.className = response.data.class_name
            this.routePrefix = response.data.route_prefix
            this.permissionPrefix = response.data.permission_prefix
            this.urlPrefix = response.data.url_prefix
            this.templatePrefix = response.data.template_prefix
            this.listable = true
            this.creatable = true
            this.viewable = true
            this.editable = true
            this.deletable = true
            this.gridColumns = response.data.grid_columns
            this.formFields = response.data.form_fields
            this.classFileName = response.data.class_file_name
            this.classFilePath = this.classFilePath.replace(/\/[^\/]+$/, "/" + response.data.class_file_name)
            this.fetchingSuggestions = false
        }, response => {
            this.fetchingSuggestions = false
        })

        this.showStep("enter-details")
    }

    ThisPageData.fetchingSuggestions = false

    ThisPageData.modelTitle = "Poser Widget"
    ThisPageData.modelTitlePlural = "Poser Widgets"

    ThisPageData.className = "PoserWidgetView"
    ThisPageData.routePrefix = "poser_widgets"
    ThisPageData.permissionPrefix = "poser_widgets"
    ThisPageData.urlPrefix = "/poser-widgets"
    ThisPageData.templatePrefix = "/poser-widgets"

    ThisPageData.listable = true
    ThisPageData.creatable = true
    ThisPageData.viewable = true
    ThisPageData.editable = true
    ThisPageData.deletable = true

    ThisPageData.gridColumns = null
    ThisPageData.formFields = null

    ThisPageData.viewModuleDirs = ${json.dumps(view_module_dirs)|n}
    ThisPageData.viewModuleDir = ${json.dumps(view_module_dir)|n}
    ThisPageData.classFileName = "poser_widgets.py"
    ThisPageData.classFilePath = "??/poser_widgets.py"
    ThisPageData.classFileOverwrite = false
    ThisPageData.writingViewFile = false
    ThisPageData.wroteViewFile = null
    ThisPageData.viewConfigPath = null
    ThisPageData.viewModulePath = null

    ThisPage.methods.writeViewFile = function() {
        this.writingViewFile = true

        this.routeCheckRoute = this.routePrefix
        this.routeChecked = null
        this.routeCheckProblem = false

        const params = {
            action: "write_view_file",
            view_location: this.viewModuleDir,
            view_file_name: this.classFileName,
            view_file_path: this.classFilePath,
            overwrite: this.classFileOverwrite,
            class_name: this.className,
            model_option: this.modelOption,
            model_name: this.modelName,
            model_title: this.modelTitle,
            model_title_plural: this.modelTitlePlural,
            route_prefix: this.routePrefix,
            permission_prefix: this.permissionPrefix,
            url_prefix: this.urlPrefix,
            template_prefix: this.templatePrefix,
            listable: this.listable,
            creatable: this.creatable,
            viewable: this.viewable,
            editable: this.editable,
            deletable: this.deletable,
            grid_columns: (this.gridColumns || "").split("\n").filter((col) => col.trim().length > 0),
            form_fields: (this.formFields || "").split("\n").filter((fld) => fld.trim().length > 0),
        }

        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.wroteViewFile = response.data.view_file_path
            this.viewConfigPath = response.data.view_config_path
            this.viewModulePath = response.data.view_module_path
            this.writingViewFile = false
            this.showStep("confirm-route")
        }, response => {
            this.writingViewFile = false
        })
    }

    ThisPageData.routeCheckRoute = "poser_widgets"
    ThisPageData.routeChecked = null
    ThisPageData.routeChecking = false
    ThisPageData.routeCheckProblem = false

    ThisPage.methods.routeCheck = function() {
        this.routeChecking = true
        const params = {
            action: "check_route",
            route: this.routeCheckRoute,
        }
        this.wuttaPOST(this.wizardActionURL, params, response => {

            // nb. we slow the response down just a bit so the user
            // can "see" that a *new* import was in fact attempted.
            setTimeout(() => {
                this.routeChecking = false
                this.routeChecked = this.routeCheckRoute
                if (response.data.problem) {
                    this.routeCheckProblem = true
                } else {
                    this.routeCheckProblem = false
                    this.viewURL = response.data.url
                    this.viewPath = response.data.path
                }
            }, 200)
        })
    }

    ThisPageData.menuFilePath = ${json.dumps(menu_path)|n}
    ThisPageData.viewURL = null
    ThisPageData.viewPath = null

    ThisPageData.roles = ${json.dumps(roles)|n}
    ThisPageData.listingRoles = ${json.dumps(listing_roles)|n}
    ThisPageData.creatingRoles = ${json.dumps(creating_roles)|n}
    ThisPageData.viewingRoles = ${json.dumps(viewing_roles)|n}
    ThisPageData.editingRoles = ${json.dumps(editing_roles)|n}
    ThisPageData.deletingRoles = ${json.dumps(deleting_roles)|n}
    ThisPageData.applyingPermissions = false

    ThisPage.methods.applyPermissions = function() {
        this.applyingPermissions = true

        const params = {
            action: "apply_permissions",
            permission_prefix: this.permissionPrefix,
        }

        if (this.listable) {
            params.listing_roles = this.listingRoles
        }
        if (this.creatable) {
            params.creating_roles = this.creatingRoles
        }
        if (this.viewable) {
            params.viewing_roles = this.viewingRoles
        }
        if (this.editable) {
            params.editing_roles = this.editingRoles
        }
        if (this.deletable) {
            params.deleting_roles = this.deletingRoles
        }

        this.wuttaPOST(this.wizardActionURL, params, response => {
            this.applyingPermissions = false
            this.showStep("commit-code")
        }, response => {
            this.applyingPermissions = false
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
