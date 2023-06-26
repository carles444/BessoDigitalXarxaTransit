const mountGraph = (jsonGraph, onclickNode) => {
        const vertices = jsonGraph.vertices;
        const edges = jsonGraph.edges;
    
        const nodes = []
        vertices.forEach((element) => {
            nodes.push({
                id: element.id,
                x: element.position[0],
                y: element.position[1],
            })
        })
    
        const links = []
        edges.forEach((element) => {
            links.push({
                id: element.id,
                source: nodes.find((node) => node.id === element.origin_vertex),
                target: nodes.find((node) => node.id === element.dst_vertex),
            })
        })
    
        var margin = { top: 0, right: 20, bottom: 20, left: 20 };
        var width = 1000 - margin.left - margin.right;
        var height = 800 - margin.top - margin.bottom;
    
        const svg = d3.select("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    
        // Calcula el desplazamiento necesario para centrar el grafo
        const offsetX = width / 2 - (d3.max(nodes, (d) => d.x) - d3.min(nodes, (d) => d.x)) / 2;
        const offsetY = height / 2 - (d3.max(nodes, (d) => d.y) - d3.min(nodes, (d) => d.y)) / 2;
    
        // Dibujar los enlaces
        const link = svg
            .append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .enter()
            .append("line")
            .attr("stroke-width", 2)
            .attr("x1", (d) => d.source.x + offsetX)
            .attr("y1", (d) => d.source.y + offsetY)
            .attr("x2", (d) => d.target.x + offsetX)
            .attr("y2", (d) => d.target.y + offsetY)
            .attr("id", (d) => 'edge_' + d.id)
    
        // Dibujar los nodos
        const node = svg
            .append("g")
            .selectAll("circle")
            .data(nodes)
            .enter()
            .append("circle")
            .attr("r", 20)
            .attr("fill", "#1B9C85")
            .attr("cx", (d) => d.x + offsetX)
            .attr("cy", (d) => d.y + offsetY)
            .attr("id", (d) => 'vertex_' + d.id)
            .style('cursor', 'pointer')
          
    
        // Añadir etiquetas a los nodos
        const labels = svg
            .append("g")
            .selectAll("text")
            .data(nodes)
            .enter()
            .append("text")
            .text((d) => d.id)
            .attr("font-size", 20)
            .attr("dx", -10)
            .attr("dy", 5)
            .attr("x", (d) => d.x + offsetX)
            .attr("y", (d) => d.y + offsetY)
            .style("pointer-events", "none");
            
    }

    export default mountGraph