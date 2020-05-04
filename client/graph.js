var req = new XMLHttpRequest();
req.open("GET","http://localhost:5000/graph/setdata", false);
req.send();
var points = JSON.parse(req.responseText);

var svg = d3.select("svg"),
    margin = {top: 10, right: 0, bottom: 10, left: 30},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;









var x = d3.scaleLinear()
    .rangeRound([0, width]);

var y = d3.scaleLinear()
    .rangeRound([height, 0]);

var xAxis = d3.axisBottom(x),
    yAxis = d3.axisLeft(y);

var line = d3.line()
    .x(function(d) { return x(d[0]); })
    .y(function(d) { return y(d[1]); });

var drag = d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);

svg.append('rect')
    .attr('class', 'zoom')
    .attr('cursor', 'move')
    .attr('fill', 'none')
    .attr('pointer-events', 'all')
    .attr('width', width)
    .attr('height', height)
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

 var focus = svg.append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

x.domain(d3.extent(points, function(d) { return d[0]; }));
y.domain(d3.extent(points, function(d) { return d[1]; }));

focus.append("path")
    .datum(points)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-linejoin", "round")
    .attr("stroke-linecap", "round")
    .attr("stroke-width", 2.5)
    .attr("d", line);

focus.selectAll('circle')
    .data(points)
    .enter()
    .append('circle')
    .attr('r', 1.0)
    .attr('cx', function(d) { return x(d[0]);  })
    .attr('cy', function(d) { return y(d[1]); })
    .style('cursor', 'pointer')
    .style('fill', 'steelblue');

focus.selectAll('circle')
        .call(drag);

focus.append('g')
    .attr('class', 'axis axis--x')
    .attr('transform', 'translate(0,' + height + ')')
    .call(xAxis);

focus.append('g')
    .attr('class', 'axis axis--y')
    .call(yAxis);

function dragstarted(d) {
    d3.select(this).raise().classed('active', true);

}

function dragged(d) {
    d[0] = x.invert(d3.event.x);
    d[1] = y.invert(d3.event.y);
    d3.select(this)
        .attr('cx', x(d[0]))
        .attr('cy', y(d[1]))
    focus.select('path').attr('d', line);
}

function dragended(d) {
    d3.select(this).classed('active', false);
    var req = XMLHttpRequest()
    req.open("POST","http://localhost:5000/graph/setdata", true)
    req.send(JSON.stringify(points))
}



