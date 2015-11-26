function flash(message, category) {
  if (category == 'error') category = 'danger';
  $('<div class="alert alert-' + category + ' alert-dismissible"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' + message + '</div>').prependTo('.content').hide().slideDown();
}

///////////////
// categories
///////////////

function confirmDeleteCategory(elem) {
	localStorage.setItem('majorId', $(elem).attr('data-id'));
	$('#deleteMajorModal').modal();
}

function deleteCategory() {
	var id = localStorage.getItem('majorId');
	$.ajax({
		url: '/major/delete/' + id,
		data: {},
		type: 'POST',
		success: function(result) {
			$('#deleteMajorModal').modal('hide');
			if (result.success) {
				window.location.replace("/major");
			} else {
				window.location.reload(true);
			}
		},
		error: function(error) {
			console.log(error);
		}
	});
}

function confirmDeleteSubcategory(elem) {
	localStorage.setItem('minorId', $(elem).attr('data-id'));
	$('#deleteMinorModal').modal();
}

function deleteSubcategory() {
	var id = localStorage.getItem('minorId');
	$.getJSON('/_minor/delete/' + id, {}, function(result) {
		$('#deleteMinorModal').modal('hide');
		$('#minor-' + id).remove();
		if (result.success) {
			flash('Subcategory #' + id + ' is deleted.', 'success');
		} else {
			flash('Subcategory #' + id + ' is not found.', 'error');
		}
	});
}

function createNewSubcategory(elem) {
	localStorage.setItem('majorId', $(elem).attr('data-id'));
	$('#addMinorModal').modal();
}

function addSubcategory() {
	var id = localStorage.getItem('majorId');
	$.ajax({
		url: '/_minor/add',
		data: { name: $('#minor-name').val(), major_id: id },
		type: 'POST',
		success: function(result) {
			$('#deleteMajorModal').modal('hide');
			window.location.reload(true);
		},
		error: function(error) {
			console.log(error);
		}
	});
}

function editSubcategory(minorId) {
	var id = $('#minor-major').val();
	$.ajax({
		url: '/_minor/edit/' + minorId,
	  data: { name: $('#minor-name').val(), major_id: id },
	  type: 'POST',
		success: function(result) {
			window.location.replace('/major/' + id);
		},
		error: function(error) {
			console.log(error);
		}
	});
}

///////////////
// stores 
///////////////

function showEditStoreForm(elem) {
	var pattern = /^([^-]+)-(.*)$/g;
	var match = pattern.exec($(elem).attr('data-id'));
	localStorage.setItem('storeId', match[1]);
	localStorage.setItem('storeName', match[2]);
	$('#store-name').val(match[2]);
	$('#editStoreModal').modal();
	$('.store-add').hide();
	$('.store-edit').show();
}

function showAddStoreForm() {
	$('#editStoreModal').modal();
	$('.store-add').show();
	$('.store-edit').hide();
}

function deleteStore() {
	$.ajax({
		url: '/_store/delete/' + localStorage.getItem('storeId'),
		data: {},
		type: 'POST',
		success: function(result) {
			$('#editStoreModal').modal('hide');
			window.location.reload(true);
		},
		error: function(error) {
			console.log(error);
		}
	});
}

function editStore() {
	$.ajax({
		url: '/_store/add',
		data: { 
			store_id: localStorage.getItem('storeId'), 
			name: $('#store-name').val()
		},
		type: 'POST',
		success: function(result) {
			$('#editStoreModal').modal('hide');
			window.location.reload(true);
		},
		error: function(error) {
			console.log(error);
		}
	});
}

function addStore() {
	$.ajax({
		url: '/_store/add',
		data: { name: $('#store-name').val() },
		type: 'POST',
		success: function(result) {
			$('#editStoreModal').modal('hide');
			window.location.reload(true);
		},
		error: function(error) {
			console.log(error);
		}
	});
}

///////////////
// Transactions 
///////////////

function confirmDeleteTransaction(elem) {
	localStorage.setItem('transId', $(elem).attr('data-id'));
	$('#deleteTransactionModal').modal();
}

function deleteTransaction() {
	var id = localStorage.getItem('transId');
	$.getJSON('/_trans/delete/' + id, {}, function(result) {
		$('#deleteTransactionModal').modal('hide');
		window.location.replace('/trans');
	});
}

function addTableRow(tableId, hideRowId, num, withIdCol) {
	var table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
	var row = document.getElementById('rowToClone');

	$('#' + hideRowId).hide();
	for (i = 0; i < num; i++) {
		var clone = row.cloneNode(true);
		if (withIdCol)
			clone.insertBefore(document.createElement('td'), clone.firstChild);
		table.appendChild(clone);
	}
}

///////////////
// Items 
///////////////

function confirmDeleteItem(elem, reloadPage) {
	localStorage.setItem('itemId', $(elem).attr('data-id'));
	localStorage.setItem('reloadPage', reloadPage);
	$('#deleteItemModal').modal();
}

function deleteItem() {
	var id = localStorage.getItem('itemId');
	var reloadPage = localStorage.getItem('reloadPage');
	$.getJSON('/_item/delete/' + id, {}, function(result) {
		$('#deleteItemModal').modal('hide');
		if (reloadPage != 'false' || !result.success)
			window.location.reload(true);
		else
			window.location.replace('/item');
	});
}


