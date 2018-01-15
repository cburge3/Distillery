    var value;
    var xVal = 0;
    var updateInterval = 10000;
      $(document).ready(function() {
        window.setInterval(function(){
          $.get("/generator").done(function(result) {
           var values = JSON.parse(result);
            jQuery.each(values, function(i, val) {
            document.getElementById(i).innerHTML = val;
            });
          });
        }, updateInterval);
      });

	window.onload = function () {
      var dps = [{}];   //dataPoints.
      var chart = new CanvasJS.Chart("chartContainer",{
      	title :{
      		text: "Distillation Temp"
      	},
      	axisX: {
      		title: "Time"
      	},
      	axisY: {
      		title: "Temp\xB0F"
      	},
      	data: [{
      		type: "line",
      		dataPoints : dps
      	}]
      });
      var updateChart = function () {
        //var time = new Date();
        //xVal = time.getTime();
      	dps.push({x: xVal,y: value});
      	xVal = xVal + (updateInterval / 1000);
      	chart.render();
	// update chart after specified time.
};

setInterval(function(){updateChart()}, updateInterval);

}

$("button").click(function(e) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "/generator",
        data: {
            id: $(this).closest("div").attr("id"), // < note use of 'this' here
            time: Date.now(),
            value: $(this).attr("value")
        } /*,
        success: function(result) {alert(result);},
        error: function(result) {
            alert(result);
        }
        */
    });
});