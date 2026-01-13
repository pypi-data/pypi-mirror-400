## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="form_vue_fields()">

  SOMETHING CRAZY

  <b-field label="name">
    <b-input name="name" v-model="${form.get_field_vmodel('name')}" />
  </b-field>
</%def>
