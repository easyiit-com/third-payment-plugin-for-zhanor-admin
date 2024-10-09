$(document).ready(function () {
	"use strict";
	var modelEditor, templateIndexEditor, templateAddEditor, templateEditEditor, viewsEditor, apiEditor,schemaEditor, jsEditor, routeEditor;

	// 初始化编辑器的函数
	function initAceEditor(elementId, mode) {
		var editor = ace.edit(elementId);
		editor.session.setMode("ace/mode/" + mode);
		editor.setTheme("ace/theme/dracula");
		return editor;
	}

	modelEditor = initAceEditor("model_code", "python");
	templateIndexEditor = initAceEditor('template_index_code', 'html');
	templateAddEditor = initAceEditor('template_add_code', 'html');
	templateEditEditor = initAceEditor('template_edit_code', 'html');
	viewsEditor = initAceEditor('views_code', 'python');
	apiEditor = initAceEditor('api_code', 'python');
	schemaEditor = initAceEditor('schema_code', 'python');
	jsEditor = initAceEditor('js_code', 'javascript');
	routeEditor = initAceEditor('route_code', 'python');

	$("body").on("change", ".table_name", function () {
		const tableName = $(this).val();
		console.log(tableName);

		var formData = new FormData();
		formData.append('table_name', tableName);
		$.ajax({
			type: "post",
			url: "/admin/generator/code",
			data: formData,
			contentType: false,
			processData: false,
			success: function (data) {
				var table_list = data.data.table_fields;

				var checkboxesHtml = '';
				for (var i = 0; i < table_list.length; i++) {
					checkboxesHtml += '<label class="form-check form-check-inline"><input class="form-check-input table_fields" type="checkbox" type="checkbox" name="fields[]" value="' + table_list[i] + '" checked><span class="form-check-label">' + table_list[i] + '</span></label>';
				}

				show_code(data.data.model_code, data.data.template_index_code, data.data.template_add_code, data.data.template_edit_code, data.data.views_code,data.data.api_code, data.data.schema_code,data.data.js_code, data.data.route_code)
				$('#table_fields').on('click', '.table_fields', function () {
					const tableName = $('#table_name').val();
					console.log(tableName);
					var checkedFieldsValues = $('.table_fields:checked').map(function () {
						return this.value;
					}).get().join(",");
					var checkedControllerValues = $('controller:checked').map(function () {
						return this.value;
					}).get().join(",");
					    var formData = new FormData();
						formData.append('table_name', tableName);
						formData.append('fields', checkedFieldsValues);
						formData.append('controllers',  checkedControllerValues);
						$.ajax({
							type: "post",
							url: "/admin/generator/code",
							data: formData,
							contentType: false,
							processData: false,
							success: function (data) {
								show_code(data.data.model_code, data.data.template_index_code, data.data.template_add_code, data.data.template_edit_code, data.data.views_code,data.data.api_code,data.data.schema_code, data.data.js_code, data.data.route_code)
								toastr.success('Get Successfully')
							}
						});
				});
				$('#table_fields').html(checkboxesHtml);

				$('#controllers').on('click', '.controller', function () {
					const tableName = $('#table_name').val();
					console.log(tableName);
					
					var checkedFieldsValues = $('.table_fields:checked').map(function () {
						return this.value;
					}).get().join(",");
		
					var checkedControllerValues = $('.controller:checked').map(function () {
						return this.value;
					}).get().join(",");
					    var formData = new FormData(); 
						formData.append('table_name', tableName);
						formData.append('fields', checkedFieldsValues);
						formData.append('controllers',  checkedControllerValues);
						$.ajax({
							type: "post",
							url: "/admin/generator/code",
							data: formData,
							contentType: false,
							processData: false,
							success: function (data) {
								show_code(data.data.model_code, data.data.template_index_code, data.data.template_add_code, data.data.template_edit_code, data.data.views_code,data.data.api_code,data.data.schema_code, data.data.js_code, data.data.route_code)
								toastr.success('Get Successfully')
							}
						});
				});

				toastr.success('Get Successfully')
			},
			error: function (data) {
				var err = data.responseJSON.errors;
				$.each(err, function (index, value) {
					toastr.error(value);
				});
				document.getElementById("generator_button").disabled = false;
				document.getElementById("generator_button").innerHTML = "Save";
			}
		});
	});

	function show_code(model_code, template_index_code, template_add_code, template_edit_code, views_code, api_code, schema_code, js_code, route_code) {
		modelEditor.setValue(model_code);
		templateIndexEditor.setValue(template_index_code);
		templateAddEditor.setValue(template_add_code);
		templateEditEditor.setValue(template_edit_code);
		viewsEditor.setValue(views_code);
		apiEditor.setValue(api_code);
		schemaEditor.setValue(schema_code);
		jsEditor.setValue(js_code);
		routeEditor.setValue(route_code);
	};

  

	function generator() {
		"use strict";

		document.getElementById("generator_button").disabled = true;
		document.getElementById("generator_button").innerHTML = "{{_('Please wait')}}";

		var formData = new FormData();
		formData.append('table_name', $("#table_name").val());

		formData.append('model_code_checked', $("#model_code_checked").is(':checked') ? $("#model_code_checked").val() : 0);
		formData.append('template_index_code_checked', $("#template_index_code_checked").is(':checked') ? $("#template_index_code_checked").val() : 0);
		formData.append('template_add_code_checked', $("#template_add_code_checked").is(':checked') ? $("#template_add_code_checked").val() : 0);
		formData.append('template_edit_code_checked', $("#template_edit_code_checked").is(':checked') ? $("#template_edit_code_checked").val() : 0);
		formData.append('views_code_checked', $("#views_code_checked").is(':checked') ? $("#views_code_checked").val() : 0);
		formData.append('api_code_checked', $("#api_code_checked").is(':checked') ? $("#api_code_checked").val() : 0);
		formData.append('schema_code_checked', $("#schema_code_checked").is(':checked') ? $("#schema_code_checked").val() : 0);
		formData.append('js_code_checked', $("#js_code_checked").is(':checked') ? $("#js_code_checked").val() : 0);
		
		formData.append('route_code', $("#table_name").val());

		formData.append('model_code', modelEditor.getValue());
		formData.append('template_index_code', templateIndexEditor.getValue());
		formData.append('template_add_code', templateAddEditor.getValue());
		formData.append('template_edit_code', templateEditEditor.getValue());
		formData.append('views_code', viewsEditor.getValue());
		formData.append('api_code', apiEditor.getValue());
		formData.append('schema_code', schemaEditor.getValue());
		formData.append('js_code', jsEditor.getValue());
		formData.append('route_code', routeEditor.getValue());

		$.ajax({
			type: "post",
			url: "/admin/generator/create_file",
			data: formData,
			contentType: false,
			processData: false,
			success: function (data) {
				toastr.success(_('Submit Successfully'))
				document.getElementById("generator_button").disabled = false;
				document.getElementById("generator_button").innerHTML = "Submit";
			},
			error: function (data) {
				var msg = data.responseJSON.msg;
				toastr.error(msg);
				document.getElementById("generator_button").disabled = false;
				document.getElementById("generator_button").innerHTML = "Submit";
			}
		});
		return false;
	}

	// 绑定按钮点击事件
	$("#generator_button").click(function (event) {
		event.preventDefault(); // 阻止按钮的默认行为（如表单提交）
		// 调用 generator 函数
		generator();
	});
});
