var values;
var xVal = 0;
var updateInterval = 2000;

/* Populate dynamic text for all of the devices */
	window.onload = function () {
	    $("h2").each(function(index, error) {
	        console.log(index+' '+ error);
            $(this).text($(this).closest("div").attr("id"));
        });
}

/* Send click commands to server */
$("button").click(function(e) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "/generator",
        data: {
            id: $(this).closest("div").attr("id"), // < note use of 'this' here
            time: Date.now(),
            value: $(this).attr("value")
        }
    });
});

var v1 = ['TI100'],
v2 = ['TI101']
var datapoints = [v1, v2];

var chart = c3.generate({
    bindto: '#chart',
    data: {
      columns: datapoints
    }
});
/* Periodically refresh incoming data */
      $(document).ready(function() {
        window.setInterval(function(){
          $.get("/generator").done(function(result) {
           values = JSON.parse(result);
            jQuery.each(values, function(i, val) {
            document.getElementById(i).innerHTML = val;
            var l = datapoints.length;
            for (var j = 0; j < l; j++) {
                if (datapoints[j][0] == i){
                    datapoints[j].push(val);
                }
            }
            chart.load({
                columns: datapoints
                });
            });
          });
        }, updateInterval);
      });
