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

    const [startNode, setStartNode] = useState(undefined)
    const [endNode, setEndNode] = useState(undefined)

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
            if (startNode != undefined) {
                vertex = document.getElementById('vertex_' + startNode)
                vertex.attr('fill', defaultNodeColor)
            }
            setStartNode(id);
            node.attr('fill', startNodeColor)
            selectingStartNode.current = false;
        }else if (selectingEndNode.current) {
            if (endNode != undefined) {
                vertex = document.getElementById('vertex_' + endNode)
                vertex.attr('fill', defaultNodeColor)
            }
            setEndNode(id);
            node.attr('fill', endNodeColor)
            selectingEndNode.current = false;
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