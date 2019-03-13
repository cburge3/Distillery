var values;
var xVal = 0;
var updateInterval = 10000;
var registered_values = ["TI100","TI101","ctrl/TK100/SP1","ctrl/TK100/SP2","ctrl/TK100/SP3","ctrl/TK100/SP4",
"ctrl/TK100/SP5"]

window.onload = function () {
    /* Register all datapoints requiring updates with the server */
    $.ajax({
    type: "POST",
    url: "/generator",
    data: {
        time: Date.now(),
        items: registered_values
        }
    });
    /* Populate dynamic text for all of the devices */
    $("h2").each(function(index, error) {
        $(this).text($(this).closest("div").attr("id"));
    });
    /* Format input boxes */
    $(".SP_numeric").attr("maxlength", 5)
    $(".SP_numeric").attr("size", 5)
    /* establish full path for algorithm references */
    $(".algorithm_reference").each(function(){
        var reference_name = $(this).attr("id");
        $(this).children("div").each(function(){
            var parameter_name = $(this).attr("id");
            $(this).children("label").attr("id", reference_name + parameter_name);
        });
    });
};

/* Send click commands to server */
$(".write").click(function(e) {
    e.preventDefault();
    $.ajax({
        type: "PUT",
        url: "/generator",
        data: {
            path: $(this).closest("div").attr("id"),
            time: Date.now(),
            value: $(this).attr("value"),
            class: $(this).closest("div").attr("class")
        }
    });
});
/* Prohibit invalid characters in SP field */
$(".SP_numeric").keyup(function(){
    var numbers = $(this).val();
    $(this).val(numbers.replace(/\D/, ''));
    $(this).parent().children("button").attr("value",$(this).val());
});

var v1 = ['TI100'],
v2 = ['TI101'],
x = ['x']
var datapoints = [x, v1, v2];

/* Periodically refresh incoming data */
      $(document).ready(function() {
        window.setInterval(function(){
          $.get("/generator").done(function(result) {
           values = JSON.parse(result);
            jQuery.each(values, function(i, val) {
            try {
                document.getElementById(i).innerHTML = val;
            }
            catch (exc) {
                //TODO tell server to unregister the extra value
                console.log(i + " does not exist on this page " + exc);
            }
            });
          });
        }, updateInterval);
      });

