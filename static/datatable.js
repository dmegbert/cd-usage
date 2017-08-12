$(document).ready(function() {
    $(".form").on("submit", function(e){
      // Prevent actual form submission
      e.preventDefault();

      // Serialize form data
      var fileName = document.getElementById("start_date").value + "-" + document.getElementById("end_date").value;
      var data = $("form").serialize();

      // Submit form data via Ajax
        $.ajax({
            type:"POST",
            url: "/get_server_data",
            data: data,
            success: function(data){
            $('#example').dataTable({
                dom: 'Bfrtlip',
                buttons: ['colvis',
                    {extend: 'csv', filename: fileName },
                    {extend: 'excel', filename: fileName },
                    {extend: 'pdf', filename: fileName },
                    'copy',
                    'print'
                ],
                destroy: true,
                data: data,
                "columns": [
                    { "data": "org" },
                    { "data": "first" },
                    { "data": "last" },
                    { "data": "user" },
                    { "data": "created"},
                    { "data": "status"},
                    { "data": "modified"},
                    { "data": "logins"},
                    { "data": "fast"},
                    { "data": "power"},
                    { "data": "virtual"}
                ]
            });
         },
      });
   });
});
