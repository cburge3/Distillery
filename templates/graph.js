// Set the dimensions of the canvas / graph
var	margin = {top: 30, right: 20, bottom: 30, left: 50},
	width = 600 - margin.left - margin.right,
	height = 270 - margin.top - margin.bottom;

// Parse the date / time
var	parseDate = d3.time.format("%H:%M:%S").parse;

// Set the ranges
var	x = d3.time.scale().range([0, width]);
var	y = d3.scale.linear().range([height, 0]);

// Define the axes
var	xAxis = d3.svg.axis().scale(x)
	.orient("bottom").ticks(5);

var	yAxis = d3.svg.axis().scale(y)
	.orient("left").ticks(5);

// Define the line
var	valueline = d3.svg.line()
	.x(function(d) { return x(d.Time); })
	.y(function(d) { return y(d.value1); });

function buildValueLine(valueName){
    return d3.svg.line()
	.x(function(d) { return x(d.Time); })
	.y(function(d) { return y(d[valueName]); });
};

window.onload = function (){
    html = "";
    $.get("/chartlist").done(function(result) {
    var files = JSON.parse(result);
    for (var i = 0; i < files.length; i++) {
        html += "<option value=" + files[i] + ">" + files[i] +  "</option>";
    };
    $('#table_list').html(html);
    });
};

function drawGraph(){
    var selected = $('#table_list :selected').text();
    selected = "datafiles/" + selected + ".txt";
    console.log(selected);

    // Adds the svg canvas
    $("svg").remove();
    var	svg = d3.select("#chart")
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
    // Get the data

    d3.csv(selected, function(error, data) {
//    	data.forEach(function(d) {
//    		d.Time = parseDate(d.Time);
//    	});
    	var values = [];
    	for (z in data[0]){
    	    if (z != "Time") {
                values.push(z);
    	    };
    	};
    	data.forEach(function(d) {
    		d.Time = parseDate(d.Time);
    		values.forEach(function(e) {
    		    d[e] = +d[e];
    		});
    	});

    	// Scale the range of the data
    	x.domain(d3.extent(data, function(d) { return d.Time; }));

    	// Add the valueline path.

        values.forEach(function(c){
            y.domain([0, d3.max(data, function(d) { return d[c]; })]);
            var vl = buildValueLine(c);
            svg.append("path")
                .attr("class", "line")
                .attr("d", vl(data));
        });

    	// Add the X Axis
    	svg.append("g")
    		.attr("class", "x axis")
    		.attr("transform", "translate(0," + height + ")")
    		.call(xAxis);

    	// Add the Y Axis
    	svg.append("g")
    		.attr("class", "y axis")
    		.call(yAxis);

    });
};