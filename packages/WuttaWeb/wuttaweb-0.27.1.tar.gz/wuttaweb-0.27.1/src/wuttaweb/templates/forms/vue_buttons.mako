## -*- coding: utf-8; -*-
% if not form.readonly:
    <br />
    <div class="buttons"
         % if form.align_buttons_right:
         style="justify-content: right;"
         % endif
         >

      % if form.show_button_cancel:
          <wutta-button ${'once' if form.auto_disable_cancel else ''}
                        tag="a" href="${form.get_cancel_url()}"
                        label="${form.button_label_cancel}" />
      % endif

      % if form.show_button_reset:
          <b-button
            % if form.reset_url:
                tag="a" href="${form.reset_url}"
            % else:
                native-type="reset"
            % endif
            >
            Reset
          </b-button>
      % endif

      <b-button type="${form.button_type_submit}"
                native-type="submit"
                % if form.auto_disable_submit:
                    :disabled="formSubmitting"
                % endif
                icon-pack="fas"
                icon-left="${form.button_icon_submit}">
        % if form.auto_disable_submit:
            {{ formSubmitting ? "Working, please wait..." : "${form.button_label_submit}" }}
        % else:
            ${form.button_label_submit}
        % endif
      </b-button>

    </div>
% endif
