import { useState, useEffect, useRef } from 'react'
import LoadingSpinner from './LoadingSpinner';
import mountGraph from '../d3GraphUtils';


function Graph() {
    console.log('rendering')
    const [loading, setLoading] = useState(true);
    const selectingStartNode = useRef(false);
    const selectingEndNode = useRef(false);
    const [graph, setGraph] = useState();

    const defaultNodeColor = '#69b3a2'
    const startNodeColor = '#55DDE0'
    const endNodeColor = 'red'

    const startNode = useRef(undefined)
    const endNode = useRef(undefined)

    const getDijkstraPath = async () => {
        console.log(startNode, endNode)
        if (startNode == undefined || endNode == undefined) {
            return
        }
        setLoading(true);
        let data = await fetch('http://localhost:8000/getDijkstraPath?starting_v=' + startNode + '&ending_v=' + endNode, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:5173'
            }
        });
        console.log(startNode.id, endNode.id)
        console.log(data)
        let json = await data.json();
        console.log(json)

    }

    const setModesOff = () => {
        selectingEndNode.current = false;
        selectingStartNode.current = false;
    }

    const selectStartNode = () => {
        setModesOff();
        selectingStartNode.current = true;
    }
    const selectEndNode = () => {
        setModesOff();
        selectingEndNode.current = true;
    } 

    const clickNode = (id, node) => {
        if (selectingStartNode.current) {
            if (startNode.current != undefined) {
                let vertex = d3.select('vertex_' + startNode.current)
                vertex.style('fill', defaultNodeColor)
            }
            startNode.current = id;
            node.attr('fill', startNodeColor)
        }else if (selectingEndNode.current) {
            if (endNode.current != undefined) {
                let vertex = d3.select(endNode.current)
                vertex.style.fill = defaultNodeColor
            }
            endNode.current = id;
            node.attr('fill', endNodeColor)
        }
    }
    const getGraph = async () => {
        let data = await fetch('http://localhost:8000', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:5173'
            }
        });
        let jsonGraph = await data.json();
        setGraph(jsonGraph);
        mountGraph(jsonGraph, clickNode);
        setLoading(false);
    };

    useEffect(() => {
        getGraph();
    }, [])

    return (
        <div className='wrapper'>
            <nav id="sidebar">
                <button onClick={selectStartNode} type="button" className="btn btn-primary">Select Start</button>
                <button onClick={selectEndNode} type="button" className="btn btn-primary">Select End</button>
                <button onClick={getDijkstraPath} type="button" className="btn btn-primary">Find Shortest Path</button>

            </nav>

            <div id="content">
                
                {loading && <LoadingSpinner />}
                <svg className='container' width="1000" height="2000"></svg>
            </div>
        </div>
    )
}

export default Graph