## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/appinfo/index.mako" />

<%def name="middle_buttons()">
  ${parent.middle_buttons()}

  % if request.is_root:
      <b-button type="is-warning"
                icon-pack="fas"
                icon-left="table"
                @click="installSampleData()"
                :disabled="installingSampleData">
        {{ installingSampleData ? "Working, please wait..." : "Install Sample Data" }}
      </b-button>
      ${h.form(request.route_url(f"{route_prefix}.install_sample_data"), ref="installSampleDataForm")}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}

  % if request.is_root:
      <script>

        ThisPageData.installingSampleData = false

        ThisPage.methods.installSampleData = function() {
            if (confirm("Really install sample data?")) {
                this.installingSampleData = true
                this.$refs.installSampleDataForm.submit()
            }
        }

      </script>
  % endif
</%def>
