$(document).ready(function() {
    $(".copyable").on('click', function() {
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val($(this).text()).select();
      document.execCommand("copy");
      $temp.remove();
  
      var toastElList = [].slice.call(document.querySelectorAll('.toast'))
      var toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl)
      })
      toastList.forEach(toast => toast.show());
  
      $('.toast-body').text("Copied: " + $(this).text());
  
      //temporary class for the click effect
      $(this).addClass("clicked");
      setTimeout(function() {
        $(".clicked").removeClass("clicked");
      }, 500);
    });
});

      //file_monitor stuff
$(document).ready(function() {
    if ($("#fileMonitorTable").length) {
      var table = $('#fileMonitorTable').DataTable({
        retrieve: true,
        processing: true,
        serverSide: true,
        paging: true,
        ordering: true,
        info: false,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "ajax": {
          "url": "/file_monitor_data",
          "type": "POST",
          "data": function (d) {
            var eventTypeValues = [];
            $('#fileMonitorTable_wrapper input[type="checkbox"]:checked').each(function () {
                eventTypeValues.push($(this).val());
            });
            d.eventTypes = eventTypeValues;
        },
        },
        "order": [[3, 'asc']],
        "columns": [
          { 
            "data": "file_name", 
            "render": function(data, type, row, meta) {
              if(type === 'display'){
                data = '<a href="/file_monitor_item/' + encodeURIComponent(data) + '">' + data + '</a>';
              }
              return data;
            }
          },
          { "data": "path" },
          { "data": "file_extension" },
          { "data": "date_time" },
          { "data": "event_type" }
        ]
    });

    var checkboxes = $(
      '<div class="col-md-6">' +
      '<table class="table table-bordered mt-3">' +
      '<thead><tr><th colspan="2" class="text-center">Event Type</th></tr></thead>' +
      '<tbody>' +
      '<tr>' +
      '<td><label><input type="checkbox" name="eventType" value="1"> 1 - Created</label></td>' +
      '<td><label><input type="checkbox" name="eventType" value="2"> 2 - Deleted</label></td>' +
      '</tr>' +
      '<tr>' +
      '<td><label><input type="checkbox" name="eventType" value="3"> 3 - Changed</label></td>' +
      '<td><label><input type="checkbox" name="eventType" value="4"> 4 - Renamed</label></td>' +
      '</tr>' +
      '</tbody>' +
      '</table>' +
      '</div>'
    );
    
    $('#fileMonitorTable_wrapper').prepend(checkboxes);
    
    $('#fileMonitorTable_wrapper').on('change', 'input[type="checkbox"]', function () {
      table.ajax.reload();
    });  
  }
});

//hash status check - will check virus_total_result table for hash value existance
$(document).ready(function() {
  $('.vt-check').click(function() {
      var hash_type = $(this).data('hash-type');
      var hash_value = $(this).data('hash-value');

      $.ajax({
          url: '/run_vt_check',
          type: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({hash_type: hash_type, hash_value: hash_value}),
          success: function(result) {
              console.log(result);
          },
          error: function(error) {
              console.log(error);
          }
      });
  });
});

//tlsh list
$(document).ready(function() {
  var tableName = '#tlshTable';
  var file_name = $(tableName).data('file-name');

  $(tableName).DataTable({
      "processing": true,
      "serverSide": true,
      "ajax": {
          "url": "/data_tlsh",
          "type": "POST",
          "data": {
              "file": file_name
          }
      },
      "columns": [
          { 
              "data": "tlsh",
              "render": function(data, type, row) {
                  return '<a href="/tlsh_comparison?tlsh=' + data + '">' + data + '</a>';
              }
          },
          { "data": "path" },
          { "data": "file_size" },
          { "data": "date_time" }
      ]
  });
});

//TLSH comparison datatable tlsh_comparison.html
$(document).ready(function() {
  var tableName = '#tlshComparisonTable';
  var tlsh_value = $(tableName).data('tlsh-value');

  $(tableName).DataTable({
      "processing": true,
      "serverSide": true,
      "ajax": {
          "url": "/data_tlsh_comparison",
          "type": "POST",
          "data": {
              "tlsh": tlsh_value
          }
      },
      "columns": [
          { "data": "tlsh" },
          { "data": "file_name" },
          { "data": "path" },
          { "data": "file_size" },
          { "data": "date_time" },
          { "data": "diff" }
      ]
  });
});
