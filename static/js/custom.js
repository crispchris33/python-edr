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
  
      // Change the content of the toast body
      $('.toast-body').text("Copied: " + $(this).text());
  
      // Add a temporary class for the click effect
      $(this).addClass("clicked");
      setTimeout(function() {
        $(".clicked").removeClass("clicked");
      }, 500);
    });
  });
  